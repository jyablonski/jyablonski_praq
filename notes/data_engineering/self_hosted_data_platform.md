# Self-Hosted Iceberg Lakehouse Platform

## Overview

A data platform is the set of systems that move data from where it is produced: operational databases, third-party APIs, event streams — into a governed, queryable state where it can be modeled, analyzed, and consumed by downstream tools. Businesses need one because operational systems are optimized for transactions, not analysis. Analytics turns operational data into insights businesses use to make decisions, measure performance, and find competitive advantages. A modern data platform handles ingestion, storage, transformation, governance, and serving as distinct but coordinated layers, so each can scale and evolve independently.

This document describes a self-hosted data platform built on the Apache Iceberg lakehouse pattern. The platform decouples storage, table format, catalog, and compute, so each layer is independently operable and replaceable. Data lives in S3 as Iceberg tables; metadata and access control live in a self-hosted catalog; multiple engines query the same tables for different workloads.

The platform serves three primary workloads:

- Ingestion of operational and third-party data into a governed bronze layer.
- Transformation of bronze data into modeled silver and gold layers consumed by analytics.
- Interactive analytics for analysts and BI tools against the modeled layers.

## How it's used

The platform serves three audiences, each with a distinct access pattern:

- Stakeholders consume data through Metabase dashboards, which run against Trino. They do not write SQL or interact with the platform directly; they see modeled, governed data in the form of charts and reports.
- Analysts query the lakehouse directly via Trino, running ad-hoc SQL against modeled tables in the silver and gold layers. They occasionally contribute to the dbt project when a transformation needs to be added or modified.
- Engineers own and operate the platform end-to-end: writing Dagster jobs for ingestion and maintenance, managing infrastructure via Terraform, Helm, and Kubernetes manifests, and contributing to the dbt project alongside analysts.

## Why self-hosted over Snowflake or Databricks

Snowflake and Databricks both ship excellent managed lakehouse offerings, and either would work. The self-hosted path can be the right choice because:

- We own every layer end-to-end. Every component is open source, runs on infrastructure we control, and can be tested, profiled, and debugged in isolation.
- Cost efficiency at scale is dramatic. Compute is priced at raw EC2 rates. There is no DBU markup, no per-query credit consumption, no minimum cluster spend. Workloads that cost $50K+/year on a managed platform run in the low thousands on self-hosted infrastructure of equivalent capacity.
- The platform is a strategic asset, not a cost center. Operating it builds institutional knowledge of the full data stack, which compounds over time. The team grows more capable of solving novel problems, not just configuring managed services. This is a long-term investment in engineering capability that managed platforms structurally cannot provide.
- End-to-end observability is built-in. No haggling with third-party vendors or APIs to get lineage, metrics, and logs.

The trade-off is honest: we spend engineering time on platform operability that we would otherwise spend on data products. This is only the right trade when the team has significant experience and competency in platform engineering, and when the business value of compute cost savings and engine optionality outweighs the operational overhead.

Snowflake is the simplest managed path for 100% of workloads, because the platform is managed for you and everything is SQL. Databricks is the next step up, because it primarily offers a managed Spark runtime with SQL and Python support. The self-hosted path is the most complex, but also the most flexible and cost-effective at scale.

## Architecture

The platform is composed of the following layers, each with a clear scope and replaceable independently of the others:

1. Storage — S3, holding all data as Parquet files.
1. Format — Apache Iceberg, the open table format providing ACID, schema evolution, and time travel.
1. Catalog — Apache Polaris, the metadata service that makes Iceberg tables discoverable and governs access.
1. Compute — Spark on EKS for batch transformation and maintenance; Trino for interactive SQL.
1. Ingestion — Python jobs using Polars and PyIceberg, with Soda data quality checks gating the bronze layer.
1. Transformation — dbt-spark for modeling bronze through silver to gold, with dbt tests for correctness.
1. Table maintenance — Dagster-scheduled Spark jobs handling compaction, snapshot expiration, orphan cleanup, and manifest rewrites.
1. Orchestration — Dagster, tying ingestion, transformation, and maintenance together as assets.
1. Observability — OpenLineage emitters across Spark, dbt, and Dagster, sent to a self-hosted Marquez backend.
1. BI — Metabase connected to Trino via JDBC for dashboards and analyst queries.

Each layer is detailed below.

### Storage layer: S3

Raw and processed data is stored in S3 as Parquet files organized by Iceberg's directory layout. S3 is the only storage system in the platform; there is no separate warehouse.

### Format layer: Apache Iceberg

All tables use the Apache Iceberg open table format. Iceberg provides ACID semantics, schema evolution, time travel via snapshots, and partition evolution on top of Parquet files in object storage.

The platform writes Iceberg v2 tables for now. Iceberg v3 (deletion vectors, row lineage, VARIANT) is the production target, but Trino does not yet support v3 as of mid-2026. The transformation layer will move to v3 once Trino support lands.

### Catalog layer: Apache Polaris

Polaris is the metadata service that makes Iceberg tables discoverable and queryable. It holds the current metadata pointer for every table, enforces RBAC, and vends scoped S3 credentials to engines on table access.

Polaris runs on EKS, backed by RDS Postgres for persistence, fronted by our IdP for authentication. All compute engines (Spark, Trino) talk to Polaris via the Iceberg REST Catalog spec.

Polaris is the centerpiece of the open-engine model. Tables registered in Polaris are queryable from any Iceberg REST-compatible engine, with consistent identity and access control.

### Compute layer

Two engines, each scoped to a workload class:

Spark on EKS handles batch transformation, CDC merges, large backfills, and Iceberg table maintenance. Spark runs via the Spark Operator, with executors scheduled by Karpenter onto dedicated NodePools. Drivers run on on-demand instances; executors run on spot with graceful decommissioning enabled so shuffle blocks migrate before node termination. Spark history server is deployed as a long-running service reading event logs from S3.

Trino serves interactive SQL for analysts and BI tools. Trino runs as a long-lived cluster on EKS, connected to Polaris as its sole catalog. Sizing accounts for dashboard-driven concurrency spikes from Metabase. Primarily serves read-only queries against silver and gold layers.

### Ingestion layer

Batch ingestion is custom Python, using Polars to read source data and write Iceberg bronze tables via PyIceberg. Jobs run as Kubernetes pods orchestrated by Dagster. This approach is intentional: ingestion logic is small, our team prefers to own it, and managed connectors add cost and constraints that we do not need at our scale.

Streaming usecases like CDC from Postgres -> Kafka ingest into the lakehouse via an Iceberg sink connector.

Each ingestion job emits Soda data quality checks against the resulting bronze table before downstream consumers see the data. Failures gate the rest of the pipeline.

### Transformation layer: dbt-spark

Transformation from bronze through silver to gold is handled by dbt, using the dbt-spark adapter against our Spark cluster. Models are SQL with Jinja templating. Incremental models use Iceberg MERGE for CDC-style updates. dbt tests cover correctness assertions within the transformation layer.

The specifics of bronze -> gold are out of scope for this document, but the platform supports any modeling logic that can be expressed in dbt and SQL.

### Table maintenance

Iceberg tables require ongoing maintenance to remain performant: compaction, snapshot expiration, orphan file cleanup, and manifest rewrites. These run as four Dagster jobs, each parametrized by table and fanning out to per-table Spark submissions:

- Compaction — hourly or daily depending on write volume per table
- Snapshot expiration — daily, retaining 7 days of snapshots
- Orphan file cleanup — weekly
- Manifest rewrite — weekly

Maintenance cadence is configured per table via Polaris table properties, read at job runtime to determine which tables process on each invocation. Failures are per-table, not per-job, with alerting wired into the platform's standard observability.

### Orchestration: Dagster

Dagster orchestrates ingestion, dbt builds, maintenance jobs, and dependencies between them. Tables are modeled as Dagster assets. Dagster emits OpenLineage events for every materialization, providing automatic lineage across Python ingestion, dbt models, and maintenance jobs.

### Observability: OpenLineage

Lineage is captured via OpenLineage emitters in Spark, dbt, and Dagster, sent to a self-hosted Marquez backend. This gives end-to-end visibility from raw source through final mart without per-tool integration work.

### BI: Metabase

Metabase connects to Trino via JDBC for analyst dashboards and ad-hoc queries. A single service account with Polaris-backed read permissions on the gold layer is sufficient for the initial deployment.

## Caveats and known constraints

- Trino on Iceberg v3 is not yet supported as of mid-2026. The transformation layer writes v2 tables until support lands; v3 features (deletion vectors, row lineage) are deferred.
- Spot interruptions will occur on Spark executor nodes. Graceful decommissioning mitigates but does not eliminate the cost; long-running shuffles on spot can still trigger stage recomputation.
- Catalog availability is a hard dependency for every engine. Polaris HA, backup, and upgrade procedures must be production-grade before the platform is load-bearing.

## Rough monthly cost estimate

Self-hosted on EC2, EKS, S3, and RDS. Assumes a mid-sized analytics workload — low TB of active data, daily batch with some incremental hourly jobs, modest analyst concurrency. All figures are rough order-of-magnitude.

| Component | Configuration | Est. monthly |
| --------------------------------------- | ------------------------------------------------- | ------------ |
| S3 storage + requests | 10 TB stored, moderate request volume | $300 |
| EKS control plane | 1 cluster | $75 |
| Spark executors (spot) | ~8 r7i.2xlarge equivalent, spot, ~50% utilization | $400 |
| Spark drivers (on-demand) | ~2 r7i.xlarge equivalent, long-running | $300 |
| Trino cluster | 1 coordinator + 4 workers, r7i.2xlarge, on-demand | $1,500 |
| Polaris service | 2 small pods + RDS Postgres (db.t4g.medium, HA) | $200 |
| Dagster | 2 small pods + RDS Postgres (db.t4g.small) | $100 |
| Marquez (OpenLineage) | 1 small pod + RDS Postgres (db.t4g.small) | $75 |
| Metabase | 1 small pod + RDS Postgres (db.t4g.small) | $75 |
| Observability (logs, metrics, alerting) | varies; assume modest self-hosted footprint | $200 |
| Data transfer | mostly intra-region; some egress for exports | $150 |
| Total | | ~$3,400 |

This is the steady-state cost of the platform itself. It does not include the EC2 cost of ingestion Python pods (small, included in EKS node capacity), one-time setup, or burst capacity for backfills. Realistic range is $3,000–$5,000/month depending on workload size, retention, and how aggressively spot is used for Trino workers.

The equivalent workload on Snowflake or Databricks typically runs 2–4x this figure once compute is sized for comparable performance, before factoring in storage and platform fees. The self-hosted path trades that margin for the engineering time required to operate it.

# Data Platform Architecture

## Overview

This document describes the end-to-end architecture for the data platform: ingestion, modeling, orchestration, quality, alerting, serving, and the engineering practices that hold it together. The design optimizes for a single golden path that every pipeline follows, with shared tooling that makes the right thing also the easy thing.

## Guiding principles

The platform is built around a small set of opinions that the rest of the design follows from.

Every pipeline follows the same shape. Ingest, write to S3, load to Snowflake, transform with dbt, run data quality checks, and optionally export to consumers. New pipelines do not invent new shapes. This makes the platform legible, debuggable, and easy to onboard new sources into.

Shared tooling is the implementation of the golden path. If two pipelines need the same thing, that thing lives in shared code, not copy-pasted between pipelines. The ingestion task base, the S3 writer, the data quality helpers, and the standardized backfill process all exist to enforce consistency without requiring discipline.

dbt docs is the data catalog and the source of truth. If a model is not documented in dbt, the company does not serve data or analytics from it. This rule is what makes the catalog actually function rather than rot.

Production is the only long-lived environment. There is no long-lived dev or staging. Developers iterate locally with docker and tilt, run against personal Snowflake schema targets where needed, and rely on dbt Slim CI plus pytest coverage to catch issues before merge.

## Ingestion

### Shared tooling

All ingestion tasks are built on a shared Python base that provides:

- Polars dataframe as the base abstraction for in-memory data
- Shared helpers for connecting to S3, databases, Google Sheets, and other source systems
- Shared helpers for data quality checks at the dataframe level
- Unified S3 writer that emits parquet in partitioned format (`data_source={data_source}/table={table}/year={year}/month={month}/...`)
- Standardized backfill process triggered through Dagster
- Built-in row count monitoring and other lightweight quality checks at ingestion time

This code is published in the Dagster service and imported by all ingestion tasks as needed.

### Source to S3 to Snowflake

Ingestion tasks pull from source systems, normalize into a Polars dataframe, and write parquet files to S3 under a partitioned prefix. From S3, data is loaded into Snowflake bronze tables using `COPY INTO` with `ERROR_ON_COLUMN_COUNT_MISMATCH = FALSE`.

### Schema handling

Schema evolution is handled by the combination of parquet files preserving everything and Snowflake loads tolerating column count mismatches. New fields appear in parquet automatically and can be backfilled into dbt later when analytics needs them. Existing field type changes are caught by dbt tests at the staging layer rather than by explicit contracts.

This is a deliberate choice. Schema contracts would catch more issues earlier but require maintenance and add friction. The parquet-preserves-everything safety net is judged sufficient for the volume and rate of source changes the platform sees.

The reality is if a source adds new fields, you typically don't need them in analytics right away. And when the time comes to add them, you can do so by adjusting the bronze table DDL, backfilling the source data from S3 into the Warehouse, and then making dbt changes and performing full refreshes as needed.

## Warehouse and modeling

### Medallion layers

The warehouse uses a four-layer medallion architecture in dbt.

Bronze. Raw data loaded as-is from S3. No transformation. One bronze table per source table.

Silver (staging). 1:1 with bronze tables. Standardizes column names and data types. Handles deduplication where needed. The boundary where ingestion-level data quality is validated.

Silver (core). Fact and dimension tables. The building blocks for analysis and reporting. Includes business logic where it is genuinely shared across downstream models.

Gold. Mart tables that pull from fact and dimension tables, aggregate data, and have final data quality checks. Optimized for BI tool consumption.

### Why aggregate in dbt

Pre-aggregating in gold rather than in the BI tool has clear advantages: data quality issues are caught before stakeholders see them, BI tool performance stays snappy because results are pre-built, source of truth is established ahead of time so debugging happens in dbt instead of the BI layer, and the BI tool itself becomes swappable without rebuilding metrics.

If there is a data issue, it's clear that it's coming from the warehouse and not from the BI tool.

### Materialization policy

Staging materialization follows source volume:

- Medium sources (1M to 50M rows per day): table, tests at staging
- Large sources (50M+ rows per day, append-only or with reliable update timestamps): incremental, tests at staging

Views with tests is explicitly not allowed because the test execution recomputes the view's underlying query, then downstream models recompute it again to materialize. Either views with no tests, or tables with tests. Nothing in between.

Silver core models default to table or incremental, almost never view. Gold models default to table for BI performance.

### Deduplication pattern

Deduplication happens at the staging layer using `qualify` with `row_number()` as needed. If you need a downstream SCD2 table, you can still do create a `rk` field w/ `row_number()` in staging without performing any filtering so that the full history is preserved, then filter to the latest record in the downstream SCD2 model.

```sql
select
    order_id,
    customer_id,
    order_status,
    updated_at,
    _loaded_at
from {{ source('orders', 'raw_orders') }}
qualify row_number() over (
    partition by order_id
    order by updated_at desc, _loaded_at desc
) = 1
```

The ordering clause must include a deterministic tiebreaker. If the source has no reliable ordering column, the ingestion layer adds `_loaded_at` so dedupe behavior is consistent.

A `unique` test on the partition key validates that dedupe is working.

### Testing policy

Staging tests cover ingestion-level breakage:

- `unique` on the primary key
- `not_null` on any column downstream models join on
- `accepted_values` on enum-like columns where source-side surprises matter
- Source freshness on the underlying bronze table

Silver core and gold tests cover semantic correctness, relationships between tables, and business-rule violations. Gold tables additionally have explicit row count, value range, and business logic checks as the final quality gate before serving.

### Unit tests

dbt unit tests cover non-trivial SQL logic. They are expected on silver core fact/dim models with business logic, on gold aggregations, and on any model with case statements, window functions, or business rules. They are optional on staging models that are pure renames and casts.

Fixtures live next to the model they test (co-located, not centralized). YAML is the default fixture format. LLM-assisted fixture generation is used to accelerate test authoring, with skill prompts written to explicitly request edge cases (nulls, empty inputs, duplicate keys, boundary dates) rather than just happy-path data.

### Warehouse routing

dbt model configs route specific models to larger Snowflake warehouses where needed. The convention is per-model or per-tag override, with a sensible default warehouse set at the project level.

### Documentation requirements

Every silver core and gold model has a description. Every column in silver core and gold has a description. Every model has a `meta.owner`. CI fails if these are missing. This is what makes the dbt docs source-of-truth rule actually enforceable.

Exposures are required for every BI dashboard and every CDP sync. A dashboard is not considered done until its exposure is in dbt.

## Orchestration

### Dagster as the orchestrator

Dagster orchestrates the golden path. Every pipeline is a sequence of assets: ingestion task, write to S3, load to Snowflake, dbt build, data quality checks, run export. The pipeline shape is identical across sources, with the source-specific logic encapsulated in the ingestion task.

### dbt integration

The dbt build step uses `dbt build` (not `dbt run` followed by `dbt test`) so that tests run as the build progresses and a failing test prevents downstream models from materializing on bad data.

Data quality checks at the end of the pipeline are dbt-tag-based. Tests tagged for the end-of-pipeline run (typically the final gold-layer checks and any cross-model assertions) execute after the main dbt build.

### Failure isolation

A single bad ingestion task fails only its branch of the DAG, not the whole platform. Independent pipelines continue running. The dbt build is scoped to the models downstream of the ingested data so a failure in one source does not block dbt builds for unrelated sources.

- Example: if the pipeline for data source A fails at ingestion, the pipelines for data sources B-Z still run, and the dbt models downstream of A's ingestion task do not build, but all other dbt models build as normal.
- For the purposes of failure isolation, assume there's no cross-source dependencies in dbt, although this is possible for things like User Profile dimensions that are shared across sources.
- If there are cross-source dependencies, then a failure in one source could have wider impact, but the principle of isolating failures as much as possible still applies.

### Backfills

Backfills are triggered through Dagster's backfill UI, scoped to ingestion. Downstream dbt builds pick up backfilled data on their next scheduled run. The shared ingestion tooling provides the standardized backfill primitives so individual pipelines do not implement their own backfill logic.

## Quality and alerting

### Layered quality checks

Data quality is enforced at three layers:

- Ingestion: row counts and basic dataframe-level checks via shared tooling
- dbt staging: `not_null`, `unique`, and source freshness tests
- dbt gold: row counts, value ranges, and business-rule assertions as the final gate

### Anomaly detection

dbt-elementary runs alongside dbt to provide anomaly detection on row counts, freshness drift, null rate changes, and model run times. Elementary catches the things that are hard to express as explicit tests. Explicit tests are still preferred wherever the condition can be written down, because explicit tests are clearer signal than "this looks anomalous."

### Alert routing

The alerting decision tree:

- Is this a critical pipeline with an established SLA and a runbook?
  - No: Slack alert. Fix same day. Mark the Slack message with a green check once resolved. Add fixes or steps to the pipeline runbook if needed.
  - Yes: PagerDuty alert. Fix ASAP.

A pipeline is not eligible for PagerDuty unless it has a written SLA with a business team that are agreed upon ahead of time, and a runbook for troubleshooting. This is what keeps the PagerDuty rotation actually meaningful without leaving on-call engineers on an island.

Elementary anomalies route through the same Slack channel as pipeline failure alerts, so anomaly-driven incidents go through the same fix-and-update-runbook loop.

### Runbook structure

Every PagerDuty-eligible pipeline has a runbook with: symptoms, common causes, queries to run, rollback procedure, and escalation path. Runbooks are updated as part of incident resolution.

## Serving

### BI tool

Gold tables are exposed to the BI tool. Data refreshes automatically. Stakeholders consume dashboards built on gold tables and do not write transformations in the BI layer.

### Reverse ETL to CDP (Optional)

Data exports to Segment / CDP happen as the final step of the Dagster DAG. Two paths are supported:

- Segment-managed reverse ETL, where Segment pulls from the warehouse on its own schedule
- Internal Python service that queries gold tables and posts to the CDP API

The Python path is preferred when the mapping logic is custom or when the export needs to be tightly coupled to pipeline completion. The Segment path is preferred when standard reverse ETL covers the use case.

## Platform engineering

### Repository structure

A monorepo holds Dagster code, dbt projects, Terraform for AWS and warehouse infrastructure, Migration tool for bronze layer tables etc.

### Local development

Local development uses docker and tilt. Developers run pipelines against personal Snowflake targets where needed. There is no long-lived dev or staging Snowflake environment.

### CI/CD

GitHub Actions runs CI and CD. CI includes:

- dbt Slim CI using `--defer` and `state:modified+` against the prod manifest, so PRs only build and test changed models
- pytest with a minimum 80% coverage requirement on Dagster and Python code
- dbt unit tests for models with logic
- Description and ownership checks for silver core and gold models
- SQL formatting via SQLFluff or sqlfmt in pre-commit

### Testing policy

Python test coverage is enforced at 80% as a floor. Coverage percentage alone is not the goal; code review confirms that tests cover actual transformation logic, not just import-time execution.

Dagster asset tests follow a standardized pattern (to be documented in the repo) so the team does not invent multiple competing patterns.

### Cost and query monitoring

Two dedicated Dagster DAGs handle Snowflake observability:

- Cost monitoring: aggregates Snowflake credit usage by warehouse, service, and business use case. Trends are visualized in the BI tool. Weekly drift in per-model cost is the leading indicator for capacity planning.
- Query monitoring: surfaces the top N most expensive queries, paired with dbt-elementary for model-level performance trends.

All dbt-generated queries are tagged with a Snowflake `query_tag` containing the dbt invocation ID and model name, so cost attribution back to specific pipelines and models is exact rather than guessed from SQL text.

## Onboarding a new source

The strongest test of a golden path is how long it takes to add a new source. The flow:

1. Add a new ingestion task that uses the shared tooling base. Configure the source connection and the S3 destination.
1. Define the bronze table in dbt sources YAML.
1. Add a staging model with the appropriate materialization based on source volume.
1. Add silver core models if the source feeds new facts or dimensions.
1. Add gold models if the source enables new marts.
1. Wire the new pipeline into Dagster following the existing pattern.
1. Add tests and documentation per the policies above.
1. Add an exposure if a BI dashboard or CDP sync will consume the data.

The work is mostly configuration and SQL. The platform itself does not change. This makes streamlines onboarding for new engineers, gives LLMs a clear pattern to generate code for, and keeps the focus on the source-specific logic rather than platform management.

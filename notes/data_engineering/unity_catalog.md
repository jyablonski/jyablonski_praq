# Unity Catalog

## What It Is

Unity Catalog is a unified governance layer for data and AI assets, originally built by Databricks and open-sourced in June 2024 under the Apache 2.0 license (now hosted by the LF AI & Data Foundation). It provides a single place to control access, track lineage, audit activity, and discover assets across workspaces, clouds, and engines. It exists in two forms: the managed service built into Databricks, and a standalone open-source server (Unity Catalog OSS).

The core abstraction is a three-level namespace: `catalog.schema.object` (tables, views, volumes, functions, models). The metastore sits above catalogs as the top-level container, typically scoped to one cloud region.

## What It Does

- Access control — Fine-grained permissions via standard ANSI SQL `GRANT`/`REVOKE`, plus attribute-based access control (ABAC), row filters, and column masks. Policies are defined once and enforced across all attached workspaces.
- Lineage — Automatically captures table- and column-level lineage as queries run, across languages and workflows.
- Auditing — Every read, write, schema change, and grant is logged to audit system tables.
- Discovery — Searchable catalog of governed assets with tags, comments, and metadata.
- Multi-format support — Governs Delta Lake, Apache Iceberg, Parquet, CSV, and JSON; managed tables are always Delta or Iceberg.
- Credential vending — Issues short-lived, scoped storage credentials so external engines can read/write governed tables without standing cloud access.
- AI governance — Extends the same model to ML models, functions/tools, and (in the managed product) AI gateway controls for agents and MCPs.

A key distinction is managed vs. external tables: managed tables let Unity Catalog own both governance and the underlying file lifecycle (compaction, vacuum, layout tuning), while external tables put governance under Unity Catalog but leave the data lifecycle to your cloud provider.

## Intended Users

- Platform / data engineering teams — Set up metastores, catalogs, external locations, storage credentials, and the overall governance model.
- Data analysts and scientists — Discover, query, and share governed assets through SQL and Catalog Explorer.
- Governance / security / compliance teams — Define access policies, review audit logs, track lineage for regulated data, and enforce classification.
- AI/ML teams — Govern models, unstructured data in volumes, and AI tools under one permission model (useful for RAG and agentic workloads).

## How It's Hosted

There are two deployment models:

- Managed (Databricks) — Unity Catalog runs as an account-level control-plane service inside Databricks. It's automatically enabled for workspaces created after Nov 8, 2023 (Nov 9 on Azure). Metadata lives in the Databricks control plane; data files stay in your own cloud storage (S3, ADLS, GCS). No infrastructure for you to run.
- Open-source (self-hosted) — The OSS server is a standalone Java/Spring application you run yourself (locally, in a container, or on Kubernetes). It implements the Apache Iceberg REST Catalog API and the Apache Hive metastore API, making it engine-agnostic and usable from Spark, Trino, DuckDB, Flink, and others. The OSS version is API-compatible with the managed service but is governance-focused and does not include the full proprietary feature set (e.g., advanced ABAC, managed-table optimization, AI gateway).

In both cases, the actual data sits in object storage you control — Unity Catalog governs metadata and access, not the bytes.

## How It's Updated / Managed

Unity Catalog objects can be created and modified through several interfaces, which matters for how you treat it in version control:

- Catalog Explorer (console/UI) — Point-and-click management of catalogs, schemas, grants, tags, and external locations. Good for exploration and one-off changes; not version-controlled, so console edits can drift from source-of-truth.
- SQL — `CREATE CATALOG`, `CREATE SCHEMA`, `GRANT`, `REVOKE`, etc., runnable from notebooks, SQL editors, or jobs.
- Databricks CLI — Scriptable management of Unity Catalog resources.
- REST API — Programmatic control, and the integration point the OSS server exposes for external clients.
- Infrastructure-as-Code (Git) — The recommended pattern for production. The Terraform `databricks` provider manages metastores, catalogs, schemas, grants, external locations, and storage credentials declaratively, so governance lives in a Git repo, goes through PR review, and deploys via CI/CD. This is the "git vs. console" tradeoff: console changes are fast but ephemeral and drift-prone, while Terraform/Git gives you reviewable, reproducible, auditable governance — at the cost of more upfront wiring. Many teams allow console use in dev and lock production grants behind Terraform.
- OSS updates — The open-source server itself is upgraded by pulling new releases from the GitHub repo (versioned, e.g., 0.x) and redeploying your container/binary; its catalog contents are managed through the same REST/SQL/CLI surfaces.

Identity is provisioned separately: principals (users, groups, service principals) are defined at the Databricks account level, typically synced from your IdP via SCIM, then referenced in grants.

## Alternative Tools

Open table catalogs (closest functional alternatives):

- Apache Polaris — Snowflake-originated, open-source Iceberg REST catalog; strong fit for Iceberg-first lakehouses.
- AWS Glue Data Catalog — Managed, deeply integrated with the AWS ecosystem (Athena, EMR, Lake Formation for access control).
- Project Nessie — Git-like catalog with branching/versioning semantics for Iceberg.
- Apache Gravitino — Open-source multi-catalog metadata lake / federation layer.
- Apache Hive Metastore — The legacy baseline; widely supported but lacks modern lineage, fine-grained access, and multi-format governance.

Cloud/warehouse-native governance:

- Snowflake Horizon — Snowflake's built-in governance and discovery suite.
- Microsoft Purview — Azure-centric governance, classification, and lineage.

Enterprise data governance / cataloging platforms (broader scope, often complementary):

- Collibra, Alation, Atlan, data.world — Business-glossary, stewardship, and org-wide discovery layers that frequently sit *above* a technical catalog like Unity Catalog rather than replacing it.

## Quick Comparison

- Choose Unity Catalog if you're on Databricks or want one open catalog spanning Delta + Iceberg with strong lineage and SQL-based access control.
- Choose Polaris / Nessie if you're Iceberg-only and want a lightweight, engine-neutral REST catalog.

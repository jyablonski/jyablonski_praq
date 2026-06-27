# Apache Polaris

## What is a data catalog

A data catalog is the service that makes data discoverable, addressable, and governable. In a warehouse like Snowflake, the catalog is bundled invisibly: when you write `SELECT * FROM analytics.orders`, Snowflake resolves the name to physical storage, checks your permissions, and executes the query — all inside one system. In a lakehouse, those responsibilities are explicit and separate.

A lakehouse catalog answers three questions for every query, from every engine:

- Where does this table live right now? Iceberg tables are versioned; each commit produces a new metadata file. The catalog holds the pointer to the current metadata file and updates it atomically on every write.
- Who is allowed to read or write it? The catalog enforces role-based access control at the namespace and table level, before any engine touches S3.
- What credentials should this engine use to access the underlying files? Modern catalogs vend short-lived, scoped storage credentials to engines on demand, so individual compute services do not need broad S3 IAM permissions.

Without a catalog, a lakehouse is a folder of Parquet files in S3 that no engine can safely use concurrently. With one, it behaves like a database: tables have names, permissions, and transactional commits.

## When you need a catalog

A catalog becomes necessary the moment any of the following are true:

- More than one engine reads or writes the same tables (e.g., Spark for transformation, Trino for analytics).
- More than one user or service needs different levels of access to different tables.
- Tables need atomic, concurrent writes — committed once and visible everywhere immediately.
- Data needs to be discoverable across teams without each team knowing physical S3 paths.

If only a single engine ever touches the data and there are no governance requirements, the engine's own metadata store (e.g., Hive Metastore, Spark's built-in catalog) is sufficient. This is rarely the case for a production data platform.

## What Apache Polaris is

Apache Polaris is an open-source implementation of the Iceberg REST Catalog specification. It is a service — typically deployed on Kubernetes, backed by a relational database — that any Iceberg-compatible engine can connect to over HTTP.

Polaris was co-created by Snowflake and Dremio, donated to the Apache Software Foundation in 2024, and graduated to a top-level Apache project in February 2026. It is governed by the Apache Foundation, not any single vendor, and contributions come from Snowflake, Dremio, Google, Microsoft, Confluent, and others. This vendor neutrality is the point: tables registered in Polaris are queryable from any compliant engine, including Snowflake and Databricks themselves.

Polaris provides:

- Metadata management for Iceberg tables across one or more catalogs and nested namespaces.
- Role-based access control with principal roles, catalog roles, and fine-grained privileges down to the table level.
- Credential vending, issuing short-lived, scoped cloud storage credentials to engines on table access.
- Catalog federation, presenting external catalogs (AWS Glue, Hive Metastore, other Polaris instances) as if they were local.
- Identity provider integration with Okta, Google, and other OIDC-compatible providers.

## Polaris vs. Iceberg: what each is responsible for

Polaris and Iceberg are often discussed together, but they own different layers of the stack. Understanding the split clarifies why both are needed and what fails if either is missing.

Apache Iceberg owns the table. It defines how data is physically organized in object storage and how the table's state evolves over time:

- The on-disk layout — Parquet data files, manifest files, and manifest list files
- The metadata file format that describes the table at a point in time (schema, partition spec, snapshots, file listings, statistics)
- The rules for atomic commits — how a new metadata file becomes the current one
- Schema evolution, partition evolution, and snapshot semantics (time travel)
- The on-disk encoding of row-level deletes (positional, equality, deletion vectors)

Iceberg is a specification and a set of libraries. It is not a running service. An Iceberg table on disk is fully self-describing — given the path to its current metadata file, any Iceberg-aware engine can read it without external coordination.

Polaris owns the pointer and the policy. It is the service that tells engines which version of a table is current, who is allowed to access it, and how:

- The mapping from logical table name (`analytics.orders`) to the current metadata file location in S3
- Atomic updates to that pointer when writers commit new snapshots
- Namespace organization — how tables are grouped, named, and discovered
- Access control — which principals can read or write which tables
- Credential vending — issuing short-lived, scoped S3 credentials to engines on table access
- Federation with other catalogs and identity providers

Polaris is a running service. It does not read or write Iceberg data files. It does not understand query plans. It tells engines where to look and whether they are allowed to look.

### The interaction at query time

When Spark runs `SELECT * FROM analytics.orders`:

1. Spark asks Polaris: "What is `analytics.orders`?"
1. Polaris checks that Spark's principal has read access on that table.
1. Polaris returns the S3 path to the table's current metadata file, plus a short-lived S3 credential scoped to the table's files.
1. Spark uses the credential to read the metadata file directly from S3. The metadata tells Spark which data files exist, which snapshot is current, and what the schema is.
1. Spark reads the Parquet data files from S3 and executes the query.

Polaris is in the path for steps 1–3 and never sees the actual data. Iceberg's on-disk format governs steps 4–5 and never coordinates with Polaris during the read.

### What fails if either is missing

- Without Iceberg, the data on disk has no transactional semantics, no schema versioning, no atomic visibility. Concurrent writers corrupt each other. There is no time travel. Engines must agree on a custom file layout, which defeats the open-format premise.
- Without Polaris (or an equivalent catalog), every engine needs its own private knowledge of where tables live and who can read them. Concurrent writes have no atomic source of truth for "what is the current version." Access control fragments across engines. Tables stop being discoverable as a coherent set.

The two layers compose: Iceberg makes a table a durable, evolving object; Polaris makes the set of tables a governed, discoverable system.

## Comparable tooling

Polaris is not the only Iceberg REST Catalog implementation. The realistic alternatives:

- Unity Catalog (OSS) — Databricks' catalog, open-sourced in 2024. Functionally comparable to Polaris, with strong lineage and attribute-based access control. The trade-off is that Databricks steers its roadmap; if you are not committed to the Databricks ecosystem, Polaris is the more neutral choice.
- Project Nessie — Dremio-originated catalog with Git-like branching and tagging semantics for tables. Useful if you genuinely need data CI/CD workflows. Lacks built-in fine-grained access control and credential vending, so production deployments often pair it with another layer.
- AWS Glue Data Catalog — managed AWS service that supports Iceberg. Adequate for AWS-only deployments with simple governance needs. Limited RBAC granularity and no credential vending; tightly coupled to AWS.
- Apache Gravitino — broader metadata lake project that includes Iceberg catalog functionality alongside other metadata types. More ambitious in scope; less mature as a focused catalog.
- Hive Metastore — the legacy default. Still works, still common, but lacks RBAC, credential vending, and the REST API standard. Not recommended for new deployments.

For a vendor-neutral, production-grade Iceberg catalog in 2026, Polaris is the default choice.

## Self-hosting Polaris

Polaris is a Quarkus-based Java service. It ships as a container image, a Helm chart, and a downloadable binary. The recommended production deployment is the Helm chart on Kubernetes, backed by Postgres for persistence.

### Required infrastructure

- A Kubernetes cluster (EKS or equivalent)
- A Postgres database for catalog metadata (RDS Postgres or CockroachDB are both supported)
- An S3 bucket (or buckets) where Iceberg table data will live
- An IAM role that Polaris can assume to vend scoped credentials to engines
- An OIDC identity provider for authentication

### Deployment with Helm

The Apache Polaris project publishes a Helm chart. A minimal deployment looks like this:

```yaml
# values.yaml
image:
  repository: apache/polaris
  tag: "1.4.0"

persistence:
  type: postgresql
  postgresql:
    host: polaris-db.internal
    port: 5432
    database: polaris
    username: polaris
    existingSecret: polaris-db-credentials

authentication:
  type: oidc
  oidc:
    issuerUrl: https://our-idp.example.com
    clientId: polaris

storage:
  defaultBaseLocation: s3://our-lakehouse-bucket/warehouse/
  awsRoleArn: arn:aws:iam::123456789012:role/polaris-storage-access

ingress:
  enabled: true
  host: polaris.internal.example.com
  tls:
    enabled: true
```

Install with:

```bash
helm repo add polaris https://polaris.apache.org/helm
helm install polaris polaris/polaris \
  --namespace data-platform \
  --create-namespace \
  --values values.yaml
```

### Bootstrapping the catalog

After Polaris is running, create a catalog and grant access. This is typically done via the Polaris admin CLI or REST API. Example using the CLI:

```bash
# Create a catalog backed by S3
polaris catalogs create \
  --name analytics \
  --type internal \
  --storage-type s3 \
  --default-base-location s3://our-lakehouse-bucket/warehouse/analytics/ \
  --role-arn arn:aws:iam::123456789012:role/polaris-storage-access

# Create a principal (service account) for Spark
polaris principals create --name spark-transformation

# Create a role with read/write privileges on the analytics catalog
polaris principal-roles create --name analytics-writer
polaris catalog-roles create --catalog analytics --name writer
polaris privileges grant \
  --catalog analytics \
  --catalog-role writer \
  --privilege TABLE_WRITE_DATA

# Assign the role to the principal
polaris principal-roles grant --principal spark-transformation --principal-role analytics-writer
polaris catalog-roles grant --catalog analytics --catalog-role writer --principal-role analytics-writer
```

### Connecting an engine

From Spark, configuration to use Polaris as the catalog looks like:

```python
spark = SparkSession.builder \
    .config("spark.sql.catalog.analytics", "org.apache.iceberg.spark.SparkCatalog") \
    .config("spark.sql.catalog.analytics.catalog-impl", "org.apache.iceberg.rest.RESTCatalog") \
    .config("spark.sql.catalog.analytics.uri", "https://polaris.internal.example.com/api/catalog") \
    .config("spark.sql.catalog.analytics.credential", f"{client_id}:{client_secret}") \
    .config("spark.sql.catalog.analytics.warehouse", "analytics") \
    .config("spark.sql.catalog.analytics.scope", "PRINCIPAL_ROLE:ALL") \
    .getOrCreate()

# Now the catalog is usable
spark.sql("CREATE TABLE analytics.bronze.events (id BIGINT, ts TIMESTAMP) USING iceberg")
spark.sql("SELECT * FROM analytics.bronze.events LIMIT 10")
```

Trino is configured similarly via a catalog properties file:

```properties
# /etc/trino/catalog/analytics.properties
connector.name=iceberg
iceberg.catalog.type=rest
iceberg.rest-catalog.uri=https://polaris.internal.example.com/api/catalog
iceberg.rest-catalog.warehouse=analytics
iceberg.rest-catalog.security=oauth2
iceberg.rest-catalog.oauth2.credential=${ENV:POLARIS_CREDENTIAL}
iceberg.rest-catalog.vended-credentials-enabled=true
```

### Operational concerns

- High availability. Run at least two Polaris pods behind a service. The Postgres backend should be HA (RDS Multi-AZ or equivalent). Polaris itself is stateless; all state lives in Postgres.
- Backups. Back up the Postgres database on the standard cadence. Catalog metadata is critical — losing it means losing the pointer to every table's current state.
- Upgrades. Polaris follows semantic versioning. Read the release notes for schema changes before upgrading; the project provides migration scripts for the Postgres schema.
- Monitoring. Polaris exposes Prometheus metrics. Key signals are request latency, error rate, and database connection pool saturation.
- Secrets management. Client credentials, database passwords, and IAM role ARNs should live in your secrets manager (AWS Secrets Manager, Vault), not in values files.

A two-pod Polaris deployment with a small HA Postgres instance is sufficient for a platform serving low-to-mid TB of data and a handful of engines. Scaling is horizontal; add more pods if request volume grows.

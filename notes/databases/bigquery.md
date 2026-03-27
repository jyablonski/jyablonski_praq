# BigQuery

## What BigQuery is

BigQuery is Google's fully managed, serverless cloud data warehouse built on Google's internal Dremel query engine. The core architectural idea is complete separation of compute and storage — you do not provision clusters or manage servers. Queries are automatically parallelized across as many machines as needed, and storage is backed by Colossus, Google's distributed filesystem.

---

## Concrete strengths

- truly serverless — no cluster sizing, no warmup, no patching
- deep GCP ecosystem integration — Looker, Dataflow, Pub/Sub, Vertex AI, Cloud Composer, BigQuery ML all connect natively
- flexible pricing — on-demand (pay per TB scanned) for irregular workloads, flat-rate slot reservations for steady high-volume workloads
- BigQuery Omni — query data in AWS S3 or Azure Blob Storage without copying it to GCP
- federated queries — query Bigtable, Cloud Spanner, GCS, Google Sheets in-place without ingestion
- strong SQL dialect — excellent window functions, arrays, structs, JSON querying, and best-in-class geospatial support via BigQuery GIS
- load jobs are free — you only pay for storage and compute, not ingestion

## How it scales

- small/medium scale (GBs to low TBs): works well but on-demand pricing rewards partitioned/clustered tables to minimize bytes scanned
- large scale (high TBs to PBs): the Dremel engine shines here, parallelizing transparently across thousands of slots with no capacity planning
- extreme scale (hundreds of PBs, real-time ingestion): supports millions of rows per second via streaming inserts; battle-tested at Google's internal scale

The main scaling caveat is high-concurrency dashboarding. On-demand gives no SLA guarantees under heavy simultaneous query load. Flat-rate reservations or Snowflake's multi-cluster warehouse model can be more predictable for that pattern.

---

## BigQuery vs Snowflake

| | BigQuery | Snowflake |
|---|---|---|
| Compute model | Serverless, automatic | Virtual warehouses, explicitly sized |
| Concurrency | Can queue under load on-demand | Multi-cluster auto-scaling, predictable |
| Cloud neutrality | GCP-native (Omni for cross-cloud queries) | Runs identically on AWS, GCP, Azure |
| Time travel | Available, less polished UX | Up to 90 days, more mature |
| Data sharing | Analytics Hub | Snowflake Marketplace, more mature ecosystem |
| Stored procedures | SQL UDFs, external connections | Javascript, Python, Java, Scala via Snowpark |
| Semi-structured data | STRUCT/ARRAY, powerful but steeper learning curve | VARIANT type, flexible schema-on-read |
| Pricing idle cost | Storage only when idle | Virtual warehouse burns credits while running |

Snowflake is more turnkey for high-concurrency BI and multi-cloud organizations. BigQuery is better for GCP-native teams, bursty/unpredictable workloads, petabyte-scale queries, and ML pipelines integrated with Vertex AI.

---

## GCS ingestion patterns

Google Cloud Storage is the universal intake for BigQuery batch pipelines. Producers write files (Parquet, CSV, JSON, Avro, ORC) to GCS and BigQuery picks them up. This keeps producers decoupled from the warehouse — the write site needs no knowledge of BigQuery.

### Load jobs (default for batch)

Free, simple, idempotent. Fire a load job pointing at a GCS URI with wildcard support.

```python
job = client.load_table_from_uri(
    "gs://your-bucket/path/*.parquet",
    "your_project.your_dataset.your_table",
    job_config=bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.PARQUET,
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
    ),
)
job.result()
```

Use this for: dbt source ingestion, Airflow DAGs, nightly exports, vendor file drops, log archival — anything with a natural batch cadence.

### External tables / BigLake

Define a table that points at GCS files and query them in-place without loading. No data movement, no BigQuery storage cost. Slower than native tables, no clustering benefits. BigLake is the production-grade version — adds row/column-level security and caching.

Use this for: querying raw data before deciding whether to land it, infrequently queried large datasets.

### Data Transfer Service

Handles scheduling for recurring GCS-to-BigQuery loads without needing Airflow. Less flexible — no transformation logic, no conditional loading.

Use this for: simple "pick up new files every hour and append" patterns with no orchestrator.

---

## Streaming patterns

### GCS + load job (batch)

Best for any pipeline where latency of minutes to hours is acceptable. Examples:
- NBA analytics pipeline hitting the stats API on a schedule
- nightly CRM export (Salesforce CSV dump)
- log archival from Cloud Logging
- third-party vendor file drops

### Pub/Sub → BigQuery subscription (recommended streaming path)

The cleanest streaming pattern on GCP. Application publishes a JSON message to a Pub/Sub topic. A BigQuery subscription wires that topic directly to a BigQuery table — no Cloud Function, no load job, no file. GCP handles the write automatically.

Application write-site code in Go:

```go
result := topic.Publish(ctx, &pubsub.Message{
    Data: data, // JSON bytes
})
_, err = result.Get(ctx)
```

The application has no knowledge of BigQuery. It just knows a topic name.

Setup (one-time per table):

```bash
gcloud pubsub subscriptions create user-events-bq-sub \
  --topic=user-events \
  --bigquery-table=my_project:my_dataset.user_events \
  --use-topic-schema
```

Data lands tabular — JSON keys map to BigQuery column names and are deserialized into the correct types. Common gotchas:
- key name mismatch silently drops the field (null in that column)
- wrong JSON type causes message rejection
- timestamp fields expect RFC3339 format
- schema changes (renames) require coordinated producer + table updates
- always configure a dead letter topic to catch rejected messages

Use this for: clickstream/user behavior events, ad impressions, IoT sensor readings, webhook receivers, microservice audit trails — any application-generated event stream where a few seconds of latency is acceptable and at-least-once delivery is fine.

### Storage Write API (high-throughput, exactly-once)

The low-level write surface for cases where correctness guarantees matter. Three modes:

- default stream — at-least-once, rows immediately visible, no stream lifecycle to manage
- buffered stream — exactly-once via offset tracking, rows visible after explicit flush/commit
- pending stream — atomic batch commit, nothing visible until `FinalizeWriteStream` + `BatchCommitWriteStreams`

Use this for: CDC/database replication (Debezium → BigQuery), financial transaction ledgers where duplicates are unacceptable, internal ingestion platform infrastructure, atomic partition replacement.

---

## Pub/Sub topic schema

Attach an Avro schema to the topic to validate messages at publish time. Bad messages are rejected at the producer before they can land wrong in BigQuery.

```bash
gcloud pubsub schemas create user-events-schema \
  --type=AVRO \
  --definition='{
    "type": "record",
    "name": "UserEvent",
    "fields": [
      {"name": "user_id",    "type": "string"},
      {"name": "amount",     "type": ["null", "double"]},
      {"name": "is_premium", "type": ["null", "boolean"]},
      {"name": "ts",         "type": "string"}
    ]
  }'
```

Nullable Avro fields use union syntax `["null", "string"]`, which maps to NULLABLE in BigQuery. With `--message-encoding=JSON` the application still publishes plain JSON — no Avro serialization required on the producer side.

Avro → BigQuery type mapping:
- `string` → STRING
- `double` / `float` → FLOAT64
- `long` / `int` → INT64
- `boolean` → BOOL

---

## Terraform module pattern

Each event stream (one topic → one table) is encapsulated in a reusable module that creates the BigQuery table, Pub/Sub schema, topic, subscription, and dead letter topic together. Call it once per logical stream.

```hcl
module "user_events" {
  source     = "./modules/bq_pubsub_sink"
  project    = var.project
  dataset_id = "my_dataset"
  table_id   = "user_events"
  avro_schema    = jsonencode({ ... })
  bigquery_schema = [ ... ]
}

module "order_events" {
  source     = "./modules/bq_pubsub_sink"
  project    = var.project
  dataset_id = "my_dataset"
  table_id   = "order_events"
  avro_schema    = jsonencode({ ... })
  bigquery_schema = [ ... ]
}
```

The module outputs the topic name, which application services use as their only configuration dependency.

One caveat: the Avro schema and BigQuery schema are separate definitions that must be kept in sync manually. The type mapping is deterministic so it is possible to derive one from the other programmatically, but for most teams manually maintaining both in the module call is sufficient given how infrequently schemas change.

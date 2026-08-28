# Data Pipeline Framework

1. Ingest from source, save canonical Parquet to the immutable S3 landing layer
1. Load canonical Parquet from S3 to the warehouse Bronze layer
1. Run ingestion/load quality, source freshness, and Bronze layer checks
1. Run dbt transformations (Silver staging)
1. Run dbt transformations (Gold facts and dimensions)
1. Run reconciliation checks
1. Run reverse ETL syncs (optional)

### Ingestion

Pull data from the source, canonicalize it as Parquet, and write it to the immutable S3 landing layer as partitioned files. Do not overwrite an existing object; each extraction should write to a unique run path.

Batch and CDC data should use separately marked buckets so that their processing semantics are unambiguous:

- Incremental batch extract: `s3://my-data-batch-bucket/<data_source>/extract_type=incremental/run_id=<run_id>/year=<year>/month=<month>/day=<day>/customer_data-incremental-<run_id>-part-000.parquet`
- Full snapshot or backfill: `s3://my-data-batch-bucket/<data_source>/extract_type=backfill/run_id=<run_id>/year=<year>/month=<month>/day=<day>/customer_data-backfill-<run_id>-part-000.parquet`
- CDC events: `s3://my-data-cdc-bucket/<data_source>/run_id=<run_id>/year=<year>/month=<month>/day=<day>/customer_data-cdc-<run_id>-part-000.parquet`

Use the `backfill` marker for a full snapshot used to initialize, rebuild, or repair a dataset. A routine full snapshot can use `extract_type=full_snapshot` and a `-full-snapshot-` filename marker instead. The partition date should be explicitly defined as the extraction, event, or source-update date; extraction date is the safest default for batch landing data.

The ingestion process should record a small run-level manifest containing:

- `run_id`, source name, extraction type, source time window, and source watermark or CDC cursor
- manifest path, data paths, file count, row count, byte count, and per-file path, size, row count, and checksum
- start time, completion time, and status such as `started`, `completed`, or `failed`
- failure details when the extraction does not complete

The run is complete only after all expected files and the manifest have been durably written to S3. The manifest is the handoff contract between ingestion and loading: it gives the warehouse load the exact files, extraction type, and run ID to process, making reruns and backfills traceable.

#### Extraction modes

- **Full snapshot:** extracts the complete source state at a point in time. It is useful for an initial load or rebuilding a target, but downstream processing must replace or reconcile the affected target rather than append the snapshot blindly.
- **Incremental batch:** extracts records added or changed since a stored watermark. Persist the source watermark with the run and advance the ingestion checkpoint only after the extraction and manifest are durably written. A failed warehouse load should retry the same run manifest rather than create a different extraction. The extract must have a defined treatment for updates, deletes, and late-arriving records.
- **CDC:** captures ordered inserts, updates, and deletes from a source change stream. CDC files belong in the separate CDC bucket and should retain the source operation and ordering cursor needed to apply changes idempotently.
- **Backfill:** re-extracts a specified historical range or dataset. It should use a new run ID and the `backfill` marker, and should not be confused with the routine incremental watermark.

Ingestion code should have unit tests for pagination, cursor handling, canonicalization, partition/path generation, metadata, and retry behavior. Integration tests should exercise the source connector and an isolated S3 landing path, including writing Parquet and the run manifest. These tests should not require production buckets or credentials.

Ingestion validation should stay focused on whether the extraction succeeded and can be loaded: source connection/request errors, incomplete pagination, missing source cursors, corrupt or unreadable Parquet, unexpected empty results where data is required, and file-level counts or checksums that do not match the run manifest. More detailed business-quality checks belong in the warehouse and dbt layers.

### Load from S3 to Warehouse

S3 is used as a middleman to decouple the ingestion process from the warehouse loading process, allowing for more flexible and reliable data pipelines. The warehouse Bronze layer should retain the canonical source-aligned records plus enough ingestion metadata to trace each record to its run and source file.

The orchestrator should pass the ingestion `run_id` or manifest path to the load step. The load step reads the manifest’s extraction type and exact data paths; it should not infer a path from the schedule or scan both batch and CDC buckets. This is how a backfill automatically loads the `extract_type=backfill` files without a separate hard-coded load configuration.

This is a simple `COPY INTO` pattern to load data from S3 into the warehouse. The production implementation should use the appropriate external stage or storage integration, target-column mapping, and load error policy. The path below represents a data path selected from the run manifest:

```sql
COPY INTO my_table
FROM '<s3-data-path-from-run-manifest>'
FILE_FORMAT = (TYPE = PARQUET);
```

For each load, record the same run ID and manifest path, along with the extraction type, load start and completion times, status, files discovered, files loaded, rows loaded, rows rejected, and any load error details. Compare the load results with the ingestion manifest before marking the run successful. The load should be safe to retry without duplicating files or records. Incremental loads typically merge or append according to the source key, backfills load into a controlled replacement or merge process, and CDC loads apply operations in source-cursor order.

### Quality, Freshness & Bronze Layer Checks

Source freshness checks ensure that the data ingested from the source is up to date relative to its expected delivery schedule or source watermark. Freshness SLAs are optional and should be defined only where timeliness matters, with the target agreed with the relevant business stakeholder team.

Bronze layer checks validate the integrity and quality of the canonical source-aligned data stored in the Bronze layer, ensuring it is ready for further transformations. At minimum, check that the expected run and files were loaded, required identifiers are usable, and the basic record shape is loadable.

The idea behind doing detailed data-quality checks in the warehouse, instead of all at ingestion time, is to centralize validation and preserve the S3 landing data for investigation and replay. Ingestion should still block on transport and loadability failures, while warehouse checks can identify source-data quality problems without discarding the extract.

Quality checks should be layered: ingestion unit and integration tests validate connector behavior, load checks compare the manifest with warehouse results, and dbt tests validate Silver and Gold models. A failed check should make the affected run visible and prevent downstream consumption when the dataset is not safe to use; lower-risk checks can alert without blocking. Define incident expectations and freshness SLAs with business stakeholder teams when the dataset supports time-sensitive reporting or operational workflows.

### dbt Transformations (Silver)

The Silver layer contains source-aligned staging models that clean and standardize Bronze data before it is used by Gold models. Keep these models close to a 1:1 relationship with their source tables, with type normalization, naming cleanup, light deduplication, and source-level filters. Avoid placing cross-source business logic, fact/dimension definitions, or major aggregates here.

Run dbt tests for Silver models as part of the pipeline, including appropriate key, nullability, relationship, and source-alignment checks. Tag models and related resources by pipeline so a focused build can select the resources for one source or workflow:

```shell
dbt build --select tag:customer_pipeline
```

Use `tag:customer_pipeline+` when the pipeline should also select downstream resources.

For example:

- Clean and standardize customer data from the Bronze layer.
- Normalize timestamps, identifiers, and source-specific status values.
- Deduplicate records according to a documented source key or ingestion rule.
- Apply lightweight source-level filters needed to make the data usable by Gold models.

### dbt Transformations (Gold)

The Gold layer contains business-ready fact and dimension models built from Silver staging models. Fact models should declare their grain and keys; dimension models should declare their entity grain and key behavior. This is where shared business rules, cross-source joins, enrichment, and appropriate aggregations belong.

Run dbt tests for Gold models after the models build, with emphasis on declared grain, unique keys, relationships, expected exclusions, and important business measures. Gold resources can use the same pipeline tag, allowing the orchestration layer to run the relevant Silver and Gold resources together with `dbt build --select tag:customer_pipeline`.

For example:

- Create a fact model for orders or events at a declared grain.
- Create dimension models for customers, products, or accounts.
- Apply shared business rules and joins needed by downstream metrics.
- Create curated aggregates or marts for stable reporting use cases.

### Reconciliation Checks

Run reconciliation checks at the grain where the comparison is meaningful. Reconcile the source extract to Bronze, Bronze to Silver, and Silver to Gold rather than assuming that a Gold row count should equal the source row count.

- **Source to Bronze:** compare expected and loaded files, rows, bytes, checksums, and source watermarks.
- **Bronze to Silver:** account for documented deduplication, invalid-record handling, and source-level filters.
- **Silver to Gold:** validate fact and dimension keys, expected exclusions, distinct entity counts, and business measures at the declared grain. Aggregation and joins can legitimately change row counts.
- **Gold to semantic layer:** validate governed metric results and join behavior for important datasets.

Every intentional exclusion should have a documented reason and be included in the expected result. For example, if the source produced 100,000 events and 300 are intentionally excluded for a defined reason, the expected result is 99,700 events at that comparison grain. Reconciliation should also define the time window, treatment of duplicates, updates, deletes, late-arriving records, and any acceptable tolerance.

### Reverse ETL Syncs (Optional)

If data needs to be synced back to operational systems, it can be handled through reverse ETL syncs after the upstream Gold models and reconciliation checks complete.

Reverse ETL writes should use idempotent upserts keyed by the destination’s stable identifier. Track a source updated timestamp or deterministic row hash so the sync sends only new or actually changed records and avoids unnecessary overwrites. The sync should record its run status, accepted and rejected records, destination errors, and a replay path for failed records.

Common destinations include CDPs, CRMs, ERPs, and simple Google Sheets integrations.

## Semantic Layer

The semantic layer joins the Gold fact and dimension models to provide a governed, unified view for downstream analytics and reporting. It should define the permitted relationships, dimensions, metrics, filters, and intended grain rather than serving as an arbitrary collection of joins.

- Single source of truth for governed metric and dimension definitions
- Consistent reporting across downstream consumers
- Join paths that reduce accidental fanout and double counting
- Simplified data access for analysts and applications

The semantic layer is the source of truth for consumer-facing business definitions, while dbt remains responsible for building and testing the underlying Gold models. It may expose a unified query interface without requiring every consumer to recreate the joins and metric logic independently.

Either the semantic layer, or the Gold models themselves, can serve as the source for downstream consumers. The decision to use which depends on factors such as the complexity of the joins, the need for governed metrics, and the capabilities of the downstream tools.

- Generally, if data will need to be served to multiple downstream consumers with consistent metrics and governed joins, the semantic layer is preferred.
- If the downstream use case requires raw or lightly transformed data for a single consumer, the Gold models themselves may be used directly.

## Downstream Use Cases

1. BI Tools
1. Third-party systems
1. Governed LLM or agent interfaces
1. Dev MCP

## General Quality

Quality checks should be applied at the stage best suited to the failure they detect:

- Unit and integration tests for ingestion connector behavior, canonicalization, Parquet output, and S3 manifests
- S3 load checks comparing the ingestion manifest with warehouse results
- Source freshness checks and optional freshness SLAs where timeliness matters
- dbt tests for Silver and Gold models, including key, relationship, and business-rule checks
- dbt reconciliation tests across the relevant layer boundaries
- Unit and integration tests for reverse ETL behavior
- Monitoring and alerting for failed runs, failed checks, and agreed SLA breaches

Quality checks should identify an owner and whether a failure blocks downstream processing or only raises an alert. Freshness targets and alert expectations should be agreed with business stakeholder teams for datasets that support time-sensitive reporting or operational workflows.

## Other

The following topics are intentionally deferred from this framework revision and should be addressed separately depending on the needs of the organization or project:

- Schema evolution and compatibility
- Governance, ownership, and access controls
- PII identification, handling, and protection
- Data Catalog tooling

# Serving Enriched User Profile Insights via Reverse ETL

## Problem

Companies use transactional databases (Postgres) for all user-facing apps and CRUD operations, while analytical databases (Snowflake) power data science and BI workloads. When we enrich user profiles with behavioral insights (e.g. "most active newsletter reader", "top topics of interest"), these live in Snowflake but need to be served in Postgres for app consumption. With millions of users and daily-changing metrics, how can we efficiently sync this data without downtime or excessive load?

- Latency is too high to serve directly from Snowflake for real-time app queries, and expensive

## Approach: Daily Full Refresh via Staging Table Swap

An atomic table swap pattern using a staging table allows us to perform a full refresh of the enriched user profile insights daily, without downtime or locking issues.

The process involves exporting the Snowflake table to S3, loading it into a staging table in Postgres, and then atomically swapping the staging table with the production table. This avoids long-running transactions and index thrashing associated with bulk updates, while ensuring that reads are never blocked during the refresh.

- Atomic means the swap happens in a single transaction, so there's no point in time where the production table is unavailable or in an inconsistent state.
- The staging table is a temporary holding area for the new data, allowing us to build indexes and validate the data before it goes live.

### Why not incremental upsert?

Because the enrichment model aggregates daily behavioral data, the vast majority of rows change every day. An incremental upsert based on `_dbt_updated_at` or similar would still touch nearly the full table, and a bulk `UPDATE` on 11M rows causes index thrashing, table bloat, and long-running transactions.

### Why not truncate + reload?

Truncate acquires an `ACCESS EXCLUSIVE` lock, blocking all reads for the duration of the load. Wrapping it in a transaction prevents partial-state issues (rollback on failure), but reads still block until the load completes. Acceptable if the sync runs at off-peak hours, but the staging swap avoids this entirely.

### Pipeline steps

1. dbt model finishes in Snowflake, materializing `gold.dim_user_profile_summary`
1. Snowflake `COPY INTO` exports the table to S3 as CSV (or Parquet)
1. Postgres loads into `user_profile_insights_staging` via one of:
   - `aws_s3.table_import_from_s3()` (preferred if on RDS/Aurora, no intermediary needed)
   - Python `psycopg` using `COPY FROM STDIN` streaming from S3 through an Airflow worker
1. Build indexes on the staging table after the load completes (faster than loading with indexes in place)
1. Atomic table swap:
   ```sql
   BEGIN;
   ALTER TABLE user_profile_insights RENAME TO user_profile_insights_old;
   ALTER TABLE user_profile_insights_staging RENAME TO user_profile_insights;
   DROP TABLE user_profile_insights_old;
   COMMIT;
   ```
1. Run data quality checks (row count comparison vs Snowflake, `synced_at` freshness)

### Postgres table design

```sql
CREATE TABLE user_profile_insights (
    user_id BIGINT PRIMARY KEY,
    my_analytics_cols float, -- .... add all of them like so
    synced_at TIMESTAMP NOT NULL DEFAULT now()
);
```

- Discrete columns are better if the app filters/indexes on specific fields
- `synced_at` provides observability into data freshness

## Key Considerations

- The staging swap makes reads zero-downtime; the lock only exists for the instant of the rename
- Loading into an empty staging table with `COPY` is fast (minutes for 11M rows)
- Indexes should be created post-load on the staging table, not before
- If using the `aws_s3` extension, Postgres pulls directly from S3 with no worker hop
- If using Python, stream via `COPY FROM STDIN` rather than row-by-row inserts
- Schedule the sync after the upstream dbt model completes, orchestrated via Airflow

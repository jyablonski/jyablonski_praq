# Data Source: {Source Name}

> **Owner:** {team or individual}
> **System of record:** {e.g. Salesforce, Stripe, internal API, vendor SFTP}
> **Last reviewed:** {date}

## Overview

{2-3 sentences. What is this data source? What business domain does it represent? Why do we ingest it?}

## Business Purpose

{Who relies on this data and for what? Be specific about use cases.}

- {e.g. "Finance uses this for monthly revenue reconciliation"}
- {e.g. "Marketing uses this to build audience segments for campaign targeting"}
- {e.g. "Product uses this to track feature adoption metrics in the weekly business review"}

## Ingestion Details

| Property | Value |
| ------------------- | ------------------------------------------------------------- |
| Ingestion method | {e.g. Fivetran, custom Airflow DAG, API pull, SFTP} |
| Cadence | {e.g. every 15 min, hourly, daily at 04:00 UTC, event-driven} |
| Landing zone | {e.g. `raw.stripe.*`, S3 bucket, specific schema} |
| Freshness SLA | {e.g. "Data should be no more than 1 hour old by 9am ET"} |
| Historical backfill | {Is it supported? How far back? Any caveats?} |

### Ingestion pipeline

- **DAG/pipeline:** {link to Airflow DAG, Fivetran connector, or orchestration config}
- **Config/repo:** {link to source code or terraform}
- **Alerting:** {where failures surface, e.g. Slack channel, PagerDuty}

## Schema and Key Tables

| Table | Description | Grain | Approximate volume |
| ---------------- | ------------------ | ------------------------------ | ------------------------- |
| `{schema.table}` | {what it contains} | {e.g. one row per transaction} | {e.g. ~2M rows, ~50k/day} |
| `{schema.table}` | {what it contains} | {e.g. one row per user} | {e.g. ~500k rows} |

### Key fields

- `{field_name}`: {what it represents, any nuances}
- `{field_name}`: {e.g. "This is the canonical user ID, joins to `dim_users.user_id`"}

## Downstream Modeling

| Model | Layer | Description |
| --------------------- | ------------ | --------------------------------------------- |
| `{stg_source__table}` | Staging | {light renaming, type casting, deduplication} |
| `{int_model}` | Intermediate | {joins, business logic} |
| `{fct_or_dim_model}` | Marts | {final consumption layer, what it powers} |

**dbt project:** {link to relevant dbt models directory or docs site}

## Data Quality

### Known issues and gotchas

- {e.g. "The `updated_at` field is not always populated for records created before 2023-01-01"}
- {e.g. "Duplicate records can appear during high-volume periods; the staging model handles dedup using `row_number()`"}
- {e.g. "The vendor occasionally changes field names without notice during API version bumps"}

### Tests and monitoring

- {e.g. "dbt tests: unique, not_null on primary keys; accepted_values on status fields"}
- {e.g. "Freshness check in dbt source YAML, warns after 2h, errors after 6h"}
- {e.g. "Anomaly detection on row counts via Elementary/Monte Carlo/custom checks"}

## Access

- **Who can query this:** {e.g. "Anyone with the `analytics` role in Snowflake"}
- **PII/sensitivity:** {Does this contain PII? Any masking or access restrictions?}
- **Retention policy:** {e.g. "Raw data retained for 13 months, then archived to cold storage"}

## Contacts

- **Source system admin:** {who to contact at the vendor or internal team for source-side issues}
- **Data engineering:** {who owns the pipeline}
- **Primary stakeholders:** {who to loop in if something breaks}

## Related Resources

- {Link to vendor API docs}
- {Link to source system admin panel}
- {Link to dbt docs for this source}
- {Link to relevant Slack channel}

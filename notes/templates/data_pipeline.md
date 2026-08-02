# Data Pipeline: {Pipeline Name}

<!-- Complete every required field. Sections labeled optional may be removed when they do not apply. Link to Airflow, dbt, and source-controlled configuration instead of copying facts those systems already own. -->

> **Technical owner:** {team or individual}
> **Business owner:** {team or individual}
> **Criticality:** {Low / Medium / High}

## In an Incident

| Question | Answer |
| -------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| Will the next run recover missed data? | {Yes — it catches up automatically / No — rerun the failed logical date} |
| Maximum tolerable delay | {duration before business impact or SLA breach} |
| Who must be notified? | {Slack channel and stakeholders, based on the escalation matrix below} |
| Where do I start? | [Rerun procedure](#rerun-procedure), [Troubleshooting](#troubleshooting), or [Escalation](#escalation) |

## Overview

{2-3 sentences. What data does this pipeline move or transform? Why does it exist? Describe the path from the source to its final consumers.}

**Example shape:** Source API → S3 landing → warehouse raw layer → dbt silver models → dbt gold models → Segment export.

## Business Impact

### Stakeholders and use cases

| Stakeholder | Use case | Impact if late or unavailable | Contact |
| ---------------- | ---------------------------------------------- | ----------------------------------------------------------------------- | ----------------------------------- |
| {e.g. Marketing} | {e.g. Build audiences for lifecycle campaigns} | {e.g. Campaign audiences remain stale until the next successful export} | {team, individual, or Slack handle} |
| {e.g. Finance} | {e.g. Reconcile daily revenue} | {e.g. Daily reporting is delayed} | {team, individual, or Slack handle} |

### Criticality

**Rating:** {Low / Medium / High}

**Rationale:** {Explain the rating in terms of business impact, data freshness, number of consumers, and whether a delay causes data loss or only stale data.}

- **Low:** A delay of one or more days has little business impact and no data is lost.
- **Medium:** Same-day recovery is expected because reports, decisions, or non-critical customer workflows depend on the data.
- **High:** Prompt recovery is required because customer-facing workflows, revenue, compliance, or executive reporting depend on the data.

## Outputs

- dbt Models
- Segment Audiences (rETL)
- APIs
- Internal Apps

## Service Levels

| Objective | Target | Measurement and monitor | Agreed with |
| ----------------------- | ----------------------------------------------- | ----------------------------------------------------------- | ------------------------------- |
| Expected completion | {e.g. by 06:00 UTC each day} | {where completion is measured and dashboard/alert link} | {business owner or stakeholder} |
| Freshness | {e.g. source data is no more than 24 hours old} | {timestamp, query, and monitor used to calculate freshness} | {business owner or stakeholder} |
| Typical runtime | {e.g. 45 minutes} | {Airflow duration metric or other monitor} | {technical owner} |
| Maximum tolerable delay | {e.g. 4 hours} | {when the delay window starts and how a breach is detected} | {business owner or stakeholder} |

## Relevant Links

Treat the orchestration code and generated lineage as authoritative. Document only behavior that is not obvious from those sources.

- S3 Buckets
- API Documentation
- Vendor Documentation

## Recovery and Reruns

### Recovery semantics

**Recovery mode:** {Choose one: `Next run catches up automatically` / `Failed run must be rerun`}

{Explain why. State whether extraction uses a durable cursor or lookback window, whether loads and models are idempotent, and whether the next scheduled run includes records missed by the failed run.}

- **If the next run catches up:** {Describe the cursor, high-water mark, or lookback behavior that prevents missed records. State how duplicates are handled.}
- **If a rerun is required:** {State which failed DAG run or logical date must be rerun, the maximum safe delay, and which stakeholders must be notified while data is stale.}
- **Partial failures:** {State whether to retry from the failed task, clear downstream tasks, or rerun the entire DAG.}
- **Late-arriving data:** {State the lookback window, merge key, finalization rule, and whether already-exported records are corrected downstream.}

### Rerun procedure

1. Confirm the failed logical date and the last successfully processed source watermark in {Airflow, a control table, or logs}.
1. Resolve the underlying issue before retrying so the rerun does not fail for the same reason.
1. {Retry the failed task / clear these tasks: `{task_ids}` / trigger the DAG with `{configuration}`.}
1. Verify the S3 batch and warehouse load are not duplicated. {Describe the partition overwrite, merge key, or deduplication behavior.}
1. Confirm the relevant dbt models and tests succeed.
1. Verify the Segment export completed for the expected audience or record count, if applicable.
1. Confirm freshness is restored and notify {stakeholders or Slack channel}.

## Troubleshooting

### Ingestion fails with an authentication error

API credentials for {source system} are changed frequently. A `401`, `403`, or token-expired response usually means the Airflow connection or secret is stale.

1. Confirm the source API is reachable and inspect the response status without logging credentials or tokens.
1. Check when `{Airflow connection or secret-manager entry}` was last rotated.
1. Ask {source system owner} whether the credentials, scopes, or allowlist recently changed.
1. Update the credential through {approved secret rotation process}; do not paste it into Airflow logs, a ticket, or Slack.
1. Test the connection, rerun `{ingest_to_s3}`, and verify a new S3 object was written for the failed logical date.

### dbt fails on an accepted value

The dbt step normally fails when {source field} contains a new value, such as `xyz`, that is not included in the accepted-values test or downstream business logic.

1. Inspect the failing dbt test and query the new values and their record counts in `{silver model}`.
1. Confirm with {business or source owner} whether each value is legitimate or bad source data.
1. If legitimate, update the accepted-values test and any mappings or downstream logic that must handle it. Do not only weaken the test.
1. If invalid, coordinate a source correction or explicitly quarantine the records.
1. Rerun the silver model and its tests, then rerun the downstream gold and export tasks.

### Warehouse load fails

- Check for {schema drift, malformed files, duplicate keys, warehouse capacity, or permissions}.
- Compare the S3 manifest or object count with the warehouse load history.
- {Document the safe retry or cleanup procedure for a partially loaded batch.}

### Segment export fails

- Check {Segment workspace or reverse ETL tool} for rejected records, rate limits, and destination errors.
- Confirm the gold model completed and contains the expected number of eligible records.
- {Document whether the export is idempotent and how to resend the failed batch without duplicating events or profiles.}

## Escalation

Use the pipeline's criticality and current business impact to determine urgency. A low-criticality failure that will catch up automatically does not require the same response as a high-criticality SLA breach.

| Criticality | Default response |
| ----------- | ---------------------------------------------------------------------------------------------------- |
| Low | {Create ticket and fix within 3 business days} |
| Medium | {Notify `#{data-team-channel}` and affected stakeholders, and fix within the agreed response window} |
| High | {Page data on-call, follow above process, and fix ASAP} |

Override the default response when actual impact is more severe than the documented rating. Include:

- The DAG run and failed task links
- The affected logical date and current data freshness
- Business use cases or exports affected
- Whether the next run will catch up automatically or a rerun is required
- Current diagnosis, mitigation, and next update time

Escalate source/API issues to {source owner or vendor support}. Escalate unresolved orchestration, storage, or warehouse issues to {data platform on-call or PagerDuty service}.

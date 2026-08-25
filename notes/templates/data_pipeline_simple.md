# Data Pipeline

## Overview

Brief description of what the pipeline does, why it exists, and what it serves downstream.

## Criticality & SLA

- **Criticality:** Low / Medium / High
- **Expected Runtime:** ~20 minutes
- **SLA:** NA / pipeline finished by 7am ET

## Ownership

- **Owner:** Data Platform
- **Stakeholders:** Analytics, Finance, Growth
- **Slack:** `#data-platform`

## Inputs & Dependencies

- Source systems, APIs, tables, files, or upstream DAGs
- External dependencies or credentials
- Any assumptions about upstream data availability

## Outputs

- Final tables / marts
- Exports, files, APIs, or downstream systems
- Primary consumers

## Business Impact

Describe what happens if the pipeline is delayed or fails.

- Affected reports, applications, or workflows
- Stakeholder groups impacted
- Whether stale data is acceptable and for how long

## Backfill & Recovery

Describe how historical data is processed and how to recover from failures.

- Incremental vs. full-refresh behavior
- Backfill command / DAG parameters
- Safe backfill ranges or limitations
- Whether downstream pipelines need to be rerun

## Troubleshooting

### Common Issue 1

Document known failure modes and their fixes.

### Common Issue 2

Document known failure modes and their fixes.

## Relevant Links

- Airflow DAG
- Source code
- Data catalog / lineage
- Dashboards
- S3 / GCS locations
- Third-party documentation
- Runbooks / incident docs

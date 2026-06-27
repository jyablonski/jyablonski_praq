# Soda

## What is Soda

Soda is a data quality framework for asserting that data meets expectations. Checks are defined as YAML, executed as SQL against a data source, and produce pass/fail results that can gate downstream pipelines or alert on regressions.

Soda is not a service or a platform. It is a Python library (`soda-core`) that runs as a job, on demand, against an existing query engine. There is nothing long-running to deploy.

## What problem it solves

Data pipelines fail silently in two distinct ways:

- Code is wrong. The transformation logic produces incorrect output. Tests inside the transformation framework (dbt tests, SQLMesh audits) catch this.
- The world changed. Upstream sources renamed a column, dropped rows, broke their schedule, or started sending malformed values. The transformation code is correct but its inputs are not.

Soda addresses the second case. It runs at the ingestion boundary — between external sources and the transformation layer — and fails loudly when incoming data violates assumptions that downstream code depends on.

## Where it fits in the platform

Soda runs against bronze tables immediately after ingestion, before any dbt model consumes them. The flow is:

1. Python ingestion job writes raw data to an Iceberg bronze table.
1. Soda scan runs against the bronze table, executing assertions defined in YAML.
1. On pass, downstream dbt models proceed.
1. On fail, Dagster halts the pipeline and alerts.

Soda is not used for assertions about transformation correctness — those live in dbt tests, where they sit next to the SQL they validate. Soda's value is at the boundary the platform does not control.

## Comparable tooling

- Great Expectations — Python-first equivalent of Soda. More flexible (arbitrary Python in custom expectations), heavier conceptual model (suites, batches, checkpoints), more code to maintain. Worth choosing if you need programmatic logic Soda's YAML cannot express.
- dbt tests / SQLMesh audits — bound to the transformation layer. Covers correctness of models, not quality of ingested data. Complementary to Soda, not a substitute.
- Pandera — schema validation for pandas/Polars DataFrames in-process. Validates an in-memory object before it lands as a table; different scope from Soda, which validates the table after it lands.
- Deequ / PyDeequ — Spark-native, runs as a Spark job. Natural fit only if ingestion is already Spark-based.
- Monte Carlo / Anomalo / Bigeye — managed observability platforms that auto-profile tables and detect anomalies without explicit assertions. Different category; complements Soda rather than replacing it.

For declarative ingestion-layer checks in 2026, Soda is the default choice.

## How checks are defined

Two files per project:

```yaml
# configuration.yml — connection details
data_source analytics:
  type: trino
  host: trino.internal
  port: 8080
  catalog: iceberg
  schema: bronze
  username: ${TRINO_USER}
  password: ${TRINO_PASSWORD}
```

```yaml
# checks/orders.yml — assertions
checks for bronze.orders:
  - row_count > 0
  - row_count between 1000 and 10000000
  - freshness(updated_at) < 1h
  - missing_count(order_id) = 0
  - duplicate_count(order_id) = 0
  - invalid_percent(status) < 1%:
      valid values: ['pending', 'shipped', 'cancelled']
  - schema:
      fail:
        when required column missing: [order_id, customer_id, updated_at, status]
        when wrong column type:
          order_id: bigint
          updated_at: timestamp
```

## Running checks

Soda is invoked via its Python API directly from Dagster, as an asset check on the bronze table:

```python
from dagster import asset_check, AssetCheckResult
from soda.scan import Scan

@asset_check(asset=bronze_orders)
def bronze_orders_quality():
    scan = Scan()
    scan.set_data_source_name("analytics")
    scan.add_configuration_yaml_file("soda/configuration.yml")
    scan.add_sodacl_yaml_file("soda/checks/orders.yml")
    scan.execute()

    return AssetCheckResult(
        passed=not scan.has_check_fails(),
        metadata={"results": scan.get_checks_text()},
    )
```

Results surface in the Dagster UI next to the asset, fail the run on assertion failure, and propagate to the platform's standard alerting.

## Operational notes

- No service to deploy. Soda Core is a pip-installable library. It runs inside the Dagster pod or as a Kubernetes job; there is no daemon, no UI, no database.
- One Python environment per engine. Each engine Soda queries needs its corresponding driver: `soda-core-trino`, `soda-core-spark`, `soda-core-snowflake`. Install only what you use.
- Checks live in Git. YAML files are versioned alongside the ingestion code they protect. Changes go through code review like any other platform change.
- Soda Cloud is optional. Soda offers a managed UI and anomaly detection service. This platform does not require it; failures are surfaced through Dagster and standard alerting. Adopt Soda Cloud later if anomaly detection becomes a requirement.
- Performance. Soda checks are SQL queries against your engine. A scan with twenty assertions on a single table runs twenty queries; size your Trino or Spark capacity accordingly. For very large tables, use sampling (`samples limit 100000`) on expensive checks.

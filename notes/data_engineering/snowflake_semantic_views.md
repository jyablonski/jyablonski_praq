# Snowflake Semantic Views

## What a Semantic View Is

A Snowflake Semantic View is a schema-level database object that defines governed business concepts over physical Snowflake tables or views. It can contain:

- Logical tables mapped to warehouse tables, views, or SQL queries.
- Primary keys and relationships between logical tables.
- Dimensions used for grouping and filtering.
- Facts representing row-level quantitative values.
- Metrics representing approved aggregations and calculations.
- Filters, synonyms, descriptions, tags, custom instructions, and verified questions.

Snowflake stores and executes the semantic object. Consumers query the Semantic View rather than independently recreating its joins and metric formulas.

```text
Git repository
  semantic view YAML
        |
        | CI validates and deploys
        v
Snowflake Semantic View
        |
        +-- SQL consumers
        +-- Cortex Analyst and Cortex Agents
        +-- supported BI tools such as Sigma
```

## Recommended Source of Truth

Keep the native Semantic View YAML in Git and treat it as the source of truth. Snowflake is the deployed runtime representation.

```text
Git YAML --deploy--> Snowflake object
Git YAML <--export-- Snowflake object  # bootstrap or drift detection only
```

Do not allow regular two-way editing. If developers edit YAML in Git while other users edit the object in Snowsight, the two definitions will drift and the next deployment will overwrite or alter the UI changes.

Choose one operating model:

- Git-managed, recommended: changes begin in YAML, go through review and CI, and deploy to Snowflake. Restrict direct production editing.
- UI-managed: changes happen in Snowsight, then the object is exported to YAML and committed immediately. This is easier initially but harder to enforce reliably.

## Example YAML

This example models completed-order revenue over orders and customers. The exact database and schema names should refer to deployed dbt marts rather than raw ingestion tables.

```yaml
name: sales_analysis
description: Governed sales metrics and customer dimensions.

tables:
  - name: orders
    description: One row per customer order.
    synonyms:
      - sales orders
    base_table:
      database: ANALYTICS
      schema: GOLD
      table: FCT_ORDERS
    primary_key:
      columns:
        - ORDER_ID
    dimensions:
      - name: order_date
        description: Date the order was placed.
        synonyms:
          - purchase date
        expr: orders.order_date
        data_type: DATE
      - name: order_month
        description: Calendar month in which the order was placed.
        expr: DATE_TRUNC('month', orders.order_date)
        data_type: DATE
      - name: order_status
        description: Whether the order was completed or cancelled.
        expr: orders.status
        data_type: VARCHAR
    facts:
      - name: order_amount
        description: Monetary amount associated with the order.
        expr: orders.amount
        data_type: NUMBER(12, 2)
        access_modifier: private_access
    metrics:
      - name: monthly_revenue
        description: Revenue from completed orders, attributed to the month the order was placed.
        synonyms:
          - revenue
          - completed revenue
        expr: SUM(IFF(orders.order_status = 'completed', orders.order_amount, 0))
        access_modifier: public_access

  - name: customers
    description: Customer attributes used to segment sales metrics.
    base_table:
      database: ANALYTICS
      schema: GOLD
      table: DIM_CUSTOMERS
    primary_key:
      columns:
        - CUSTOMER_ID
    dimensions:
      - name: customer_segment
        description: Commercial segment assigned to the customer.
        synonyms:
          - segment
        expr: customers.segment
        data_type: VARCHAR
      - name: customer_region
        description: Sales region assigned to the customer.
        synonyms:
          - region
          - territory
        expr: customers.region
        data_type: VARCHAR

relationships:
  - name: orders_to_customers
    left_table: orders
    right_table: customers
    relationship_columns:
      - left_column: CUSTOMER_ID
        right_column: CUSTOMER_ID

verified_queries:
  - name: monthly_revenue_trend
    question: How is monthly revenue trending?
    verified_by: Data Team
    use_as_onboarding_question: true
    sql: |
      SELECT *
      FROM SEMANTIC_VIEW(
        sales_analysis
        DIMENSIONS orders.order_month
        METRICS orders.monthly_revenue
      )
      ORDER BY order_month;
```

Unlike legacy stage-based semantic-model YAML, this file is used to create a native schema object. It does not need to remain on a Snowflake stage after deployment.

## Creating or Updating the View from YAML

Snowflake accepts the YAML document as a string through `SYSTEM$CREATE_SEMANTIC_VIEW_FROM_YAML`:

```sql
CALL SYSTEM$CREATE_SEMANTIC_VIEW_FROM_YAML(
  'ANALYTICS.SEMANTIC',
  $$
  name: sales_analysis
  description: Governed sales metrics and customer dimensions.
  tables:
    # Remaining YAML omitted here.
  $$,
  FALSE,
  TRUE
);
```

The arguments are:

1. Fully qualified target schema. Both database and schema are required.
1. Complete YAML specification.
1. `verify_only`: `TRUE` validates without creating or changing the object.
1. `create_or_alter`: `TRUE` uses `CREATE OR ALTER` behavior instead of the default `CREATE OR REPLACE ... COPY GRANTS` behavior.

Use `create_or_alter = TRUE` for normal deployments because it preserves unaffected materializations where possible. The default replace behavior copies existing grants, but replacing the object is a larger lifecycle event.

## CI/CD Sync Workflow

The recommended deployment order is:

1. Build and test the upstream dbt models.
1. Deploy the dbt tables and views referenced by the semantic YAML.
1. Render environment-specific database and schema names if necessary.
1. Call the procedure with `verify_only = TRUE`.
1. Call it again with `verify_only = FALSE` and `create_or_alter = TRUE`.
1. Run smoke queries against the deployed Semantic View.
1. Apply or verify consumer grants.
1. Export the deployed object and compare its normalized semantic content with the source YAML.

Validation must run after the referenced dbt objects exist. YAML syntax can be validated locally, but only Snowflake can validate referenced tables, columns, expressions, keys, and relationships completely.

### Passing a YAML File Safely

Avoid constructing a shell command by interpolating the YAML into SQL. Quotes, dollar signs, and newlines make shell interpolation fragile. Read the file and pass it as a bound parameter through the Snowflake connector:

```python
from pathlib import Path


def deploy_semantic_view(connection, path, target_schema, verify_only):
    yaml_spec = Path(path).read_text()

    with connection.cursor() as cursor:
        cursor.execute(
            """
            CALL SYSTEM$CREATE_SEMANTIC_VIEW_FROM_YAML(
              %s,
              %s,
              %s,
              %s
            )
            """,
            (
                target_schema,
                yaml_spec,
                verify_only,
                True,
            ),
        )
        return cursor.fetchone()[0]
```

The CI job uses its Snowflake deployment identity. Credentials remain in the CI secret manager rather than the YAML or deployment script.

### Environment-Specific Names

The native YAML contains physical database and schema names. For development, staging, and production, use one of these patterns:

- Render a small set of explicit placeholders in CI, such as `${DATABASE}` and `${GOLD_SCHEMA}`.
- Generate an environment-specific YAML artifact from a reviewed template.
- Maintain separate environment overlays if the physical models genuinely differ.

Do not let the semantic definitions themselves vary silently by environment. Metric expressions, relationships, descriptions, and visibility should remain identical; only physical object locations should normally change.

## Exporting YAML from Snowflake

Export an existing view with:

```sql
SELECT SYSTEM$READ_YAML_FROM_SEMANTIC_VIEW(
  'ANALYTICS.SEMANTIC.SALES_ANALYSIS'
);
```

Useful cases:

- Bootstrap Git from a view initially created in Snowsight or DDL.
- Review exactly what Snowflake deployed.
- Detect production drift caused by direct object editing.
- Migrate between authoring approaches.

Do not rely on a byte-for-byte diff. Snowflake can normalize identifier casing, ordering, quoting, or formatting during the round trip. Parse both YAML documents and compare their semantic structure, or review the exported content as a generated artifact.

Snowflake also supports export and import using Open Semantic Interchange YAML. That path is useful for cross-tool portability, but Snowflake-specific behavior may be represented through vendor extensions. Use Snowflake's native YAML when Snowflake is the only target and full feature fidelity matters.

## Suggested Repository Layout

```text
semantic_views/
  sales_analysis.yml
  customer_success.yml

scripts/
  deploy_semantic_view.py
  compare_semantic_view.py

tests/
  semantic_views/
    sales_analysis.sql
    verified_questions.yml
```

Each Semantic View should have:

- One reviewed YAML source file.
- A named owner.
- Descriptions and synonyms for stakeholder-facing members.
- Explicit public/private access modifiers for facts and metrics.
- Smoke queries for important metric/dimension combinations.
- Verified natural-language questions for Cortex Analyst.
- An evaluation set that checks query generation and result correctness.

## Privileges

The deployment role needs:

- `USAGE` on the target database and schema.
- `CREATE SEMANTIC VIEW` on the target schema.
- `SELECT` on tables and views referenced by the YAML.
- `OWNERSHIP` on an existing Semantic View when updating or replacing it, unless ownership is held through the deployment role hierarchy.

A SQL or BI consumer generally needs:

- `USAGE` on the parent database and schema.
- `USAGE` on a warehouse.
- `SELECT` on the Semantic View.

The consumer does not need `SELECT` on the underlying tables merely to query the Semantic View. Cortex Analyst additionally uses `REFERENCES` to inspect and use a Semantic View. If an AI workflow is allowed to fall back to standard SQL against physical tables, that separate path requires its own underlying-table permissions.

## Querying the View

Query a metric by dimensions with the `SEMANTIC_VIEW` construct:

```sql
SELECT *
FROM SEMANTIC_VIEW(
  ANALYTICS.SEMANTIC.SALES_ANALYSIS
  DIMENSIONS orders.order_month,
             customers.customer_segment
  METRICS orders.monthly_revenue
)
ORDER BY order_month, customer_segment;
```

Snowflake also supports querying a Semantic View with a table-like `FROM` reference and the `AGG()` function for metrics. In either syntax, Snowflake validates the requested metric/dimension combination and generates the underlying joins and aggregation.

## dbt Integration

Snowflake Labs publishes the `dbt_semantic_view` package. It adds a dbt materialization that creates Semantic Views from DDL-like model content using `ref()` and `source()`.

That package is useful when the team wants Semantic View deployment to be part of `dbt run`, but it is not the same as syncing the native YAML file shown above. Choose one deployment path:

- Native YAML plus `SYSTEM$CREATE_SEMANTIC_VIEW_FROM_YAML`: best when YAML is the reviewed source of truth and import/export or cross-tool YAML workflows are important.
- dbt semantic-view materialization: best when keeping the object lifecycle entirely inside dbt outweighs using native YAML directly.

Do not deploy the same Semantic View from both paths.

## Sigma Consumption

Sigma can browse and query Snowflake Semantic Views directly, but its integration remains beta and has limitations that should influence model design:

- Facts are not exposed, so stakeholder-facing calculations must be metrics.
- Derived metrics are not currently available.
- Joins, unions, and transposes with a Semantic View are not supported.
- Metrics and relationships are available only to the Sigma element sourced directly from the Semantic View, not its child elements.
- Duplicate dimension names across logical tables can make the view unqueryable from Sigma.
- Accessible dimensions and metrics depend on relationship direction from the selected logical table.
- Public APIs do not currently support Semantic View sources.

The Sigma Snowflake connection role needs `SELECT` on each Semantic View. Definition changes deployed to Snowflake become available to live Sigma queries without a separate model-definition sync, although Sigma's AI search index can lag metadata changes or require a manual refresh.

Do not assume that every Sigma AI surface interprets Snowflake metrics and relationships identically. Validate the specific Sigma workbook, data-model, or Assistant workflow being adopted against representative questions.

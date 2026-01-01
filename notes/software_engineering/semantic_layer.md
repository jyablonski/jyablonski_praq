# Semantic Layer

Data teams build semantic layers to standardize business logic, enforce consistency, and enable self-service analytics. Just querying `SELECT  FROM model` in a BI tool leaves too much room for misinterpretation, inconsistency, and duplication of effort as your company and data needs scale.

Without a semantic layer: Each analyst or BI tool user might define metrics differently (e.g., "monthly active users" might mean different things to marketing and finance). With a semantic layer: Core definitions (like `revenue`, `active_users`, `churn_rate`) are defined once and reused everywhere — across dashboards, teams, and tools.

Data teams can't trust every stakeholder to correctly join `orders` to `customers`, apply time filters, or define a metric using all edge-case logic. Semantic layers act as a single source of truth for key metrics and dimensions.

BI users often aren’t SQL experts. Semantic layers abstract the complexity (joins, filters, partitioning logic) behind a user-friendly interface. Instead of writing complex SQL, users can just drag “Revenue” or “Churn” into a chart.

A semantic layer (like dbt Metric Layer, Looker’s LookML, or MetricFlow) enables multiple tools (Looker, Mode, Hex, etc.) to query the same definitions. This avoids metric drift across tools and reports.

- But, Semantic Layers are essentially a specification/API, not a query interface that end users interact with directly. You need something to consume it.

## A Better Pattern

Layered Architecture (Modern Analytics Stack):

1. Data Lake → Warehouse
1. dbt / ETL: Clean, join, model data into consistent tables (e.g., `fct_orders`, `dim_customers`)
1. Semantic Layer: Define metrics like `average_order_value`, dimensions like `order_date`, and relationships
1. BI Tool: Just picks metrics and filters from semantic layer

## Why Not Just Predefine the Table?

You can build a wide "presentation layer" table (say `fct_revenue_metrics`) that includes every metric and dimension your BI users need. This is:

- Simple
- Performant (assuming materialized / pre-aggregated)
- Controlled (you define the exact shape)

And this works pretty well at small scale or with a limited team

- Metric definitions are stable
- Dashboards are highly curated
- Query performance is great, because it's just selecting precomputed results from a table (`select x, y from table z`)

But it doesn't scale well when you add complexity. If users need:

- 10 dimensions (e.g., country, device, customer type)
- 5 metrics
- Across multiple time grains (daily, weekly, monthly)

You’d need to either:

- Materialize dozens of tables to cover all combos
- Or store raw data and re-aggregate in the BI tool (which means... semantic logic again)

Stakeholders will always want:

- A new cut of the data (e.g., "Can I see conversion by _browser_?")
- A modified metric (e.g., "Revenue, but excluding refunds")

Without a semantic layer, you either:

- Say “no”
- Create yet another table

If every metric is materialized into a table:

- Where do users see how “revenue” was defined?
- How do you trace changes?
- What if the logic changes?

Semantic layers let you version, document, and test metric logic — like code.

## Where Predefined Tables Shine

Predefined tables sacrifice flexibility for speed and stability. They can still serve a use case for:

- KPI dashboards with stable requirements
- High level Executive summaries
- Real-time metrics (e.g., orders in the last 24 hours)
- Any dataset that is refreshed once a day and can be precomputed easily

## The Best Practice? Use Both

1. Use dbt or ETL to create clean models (`fct_orders`, `dim_customers`)
1. Add semantic layer for key metrics (churn, LTV, etc.)
1. Materialize common metrics as views or tables if performance matters
1. Let BI tools use semantic definitions for flexibility — but point to precomputed sources when available

| Approach | Pros | Cons |
| ---------------------- | -------------------------------------- | --------------------------------------- |
| Predefined tables | Fast, simple, easy to cache | Inflexible, hard to scale, logic hidden |
| Semantic layer | Flexible, documented, reusable | May be slower, adds complexity |
| Hybrid (best practice) | Performance + governance + flexibility | Requires careful architecture |

## Recommended Setup: dbt + Looker

1. Use dbt for:

   - Building clean, well-modeled tables (like `fct_orders`, `dim_customers`)
   - Documenting columns, not necessarily metrics
   - (Optional) Using `dbt metrics` if you also serve metrics to non-Looker tools (e.g., Hex or Mode) so dbt is the source of truth

1. Use LookML for:

   - Defining metrics (like `total_revenue`, `LTV`, `churn_rate`)
   - Applying joins, dimension groups, filters
   - Exposing those to users in Explores
   - Surfacing tooltips/descriptions directly in the UI

1. Optionally use dbt docs or dbt semantic layer for:

   - Cross-tool metadata
   - Programmatic metric usage (e.g., in APIs or notebooks)
   - dbt Semantic layer would be for if you wanted to serve these metrics someplace outside of Looker

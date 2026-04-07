# ELT Data Warehouse Best Practices

This document outlines a clean, scalable approach to designing ELT pipelines in a modern data warehouse, including layering strategy, dbt project structure, and BI modeling tradeoffs.

______________________________________________________________________

## 1. ELT Workflow Overview

A well-structured ELT pipeline separates concerns across layers:

**Raw (Bronze) → Staging + Core (Silver) → Marts (Gold)**

Each layer has a clear responsibility:

### Raw / Bronze

- Exact copy of source data
- Minimal transformation
- Includes ingestion metadata (timestamps, batch IDs)
- Supports replay and debugging

**Goal:** Preserve source fidelity

______________________________________________________________________

### Staging (Silver - Part 1)

- One model per source table
- Standardize naming and data types
- Light cleaning and deduplication
- No joins or business logic

**Goal:** Clean, source-aligned tables

______________________________________________________________________

### Core (Silver - Part 2)

- Join staging models
- Build reusable business entities
- Define consistent grains
- Apply shared business logic

Includes:

- Fact tables (`fct_*`)
- Dimension tables (`dim_*`)
- Intermediate models (`int_*`)
- Bridge tables

**Goal:** Reusable, consistent business layer

______________________________________________________________________

### Marts (Gold)

- Business-facing, curated tables
- Domain-specific (finance, marketing, product)
- Pre-aggregated or denormalized where appropriate
- Designed for BI and reporting

**Goal:** Stable, easy-to-use analytics layer

______________________________________________________________________

## 2. Recommended dbt Project Structure

Each layer should be organized based on its purpose.

### Staging → Group by Source System

```text
models/
  staging/
    app/
      stg_app__users.sql
      stg_app__orders.sql
    stripe/
      stg_stripe__charges.sql
      stg_stripe__invoices.sql
    salesforce/
      stg_salesforce__accounts.sql
```

**Why:**

- Mirrors ingestion layer
- Easy lineage tracing (raw → staging)
- Avoids premature domain assumptions

______________________________________________________________________

### Core → Group by Business Entity

```text
models/
  core/
    customers/
      dim_customers.sql
      int_customer_status.sql
    orders/
      fct_orders.sql
      int_orders_enriched.sql
    billing/
      fct_payments.sql
      int_revenue_classification.sql
```

**Why:**

- Represents shared business concepts
- Reusable across domains
- Avoids duplicating logic across teams

______________________________________________________________________

### Marts → Group by Business Domain

```text
models/
  marts/
    finance/
      mart_revenue_daily.sql
      mart_mrr_monthly.sql
    marketing/
      mart_campaign_performance.sql
    product/
      mart_feature_usage_daily.sql
```

**Why:**

- Aligns with stakeholders
- Clear ownership
- Matches how data is consumed

______________________________________________________________________

## 3. Fact + Dimension vs Curated Mart Approach in BI

There are two primary ways to serve data to BI tools.

______________________________________________________________________

### Approach A: Fact + Dimension (Semantic Layer in BI)

Expose:

- `fct_orders`
- `fct_payments`
- `dim_customers`
- `dim_products`

BI tool:

- joins tables
- defines metrics
- aggregates dynamically

#### Pros

- Flexible exploration
- Reusable base models
- Fewer warehouse tables
- Supports many slicing combinations

#### Cons

- Untested aggregations
- Metric inconsistency across dashboards
- Grain confusion (easy to double count)
- Business logic leaks into BI layer
- Hard to validate correctness
- Potential performance issues

______________________________________________________________________

### Approach B: Curated Marts

Expose:

- `mart_revenue_daily`
- `mart_mrr_monthly`
- `mart_customer_retention`

BI tool:

- filters and visualizes
- minimal logic

#### Pros

- Consistent, validated metrics
- Easier for analysts and stakeholders
- Strong performance
- Fully testable in warehouse
- Clear grain and definitions

#### Cons

- Less flexible for ad hoc analysis
- More models to maintain
- Risk of mart proliferation

______________________________________________________________________

## 4. Recommended Hybrid Approach

A strong production setup uses both patterns with clear boundaries:

- **Core (facts/dims) → for advanced analysis**
- **Marts → default for dashboards and business users**
- **BI layer → thin (minimal logic)**

______________________________________________________________________

## 5. Key Design Principles

- Separate layers by responsibility, not convenience
- Keep staging source-aligned and simple
- Centralize business logic in core
- Treat marts as the primary consumption layer
- Avoid mixing facts, marts, and aggregates into one “gold” bucket
- Prefer tested, version-controlled transformations over BI-defined logic

______________________________________________________________________

## Outstanding Questions

1. What should the default materialization strategy be for staging models: views, tables, or incremental models?

   1. What criteria should justify exceptions?
   1. How do test performance, cost, and downstream reuse affect this decision?

1. How should Core and Mart layers be organized as the number of source systems grows?

   1. How do we distinguish source-specific models from conformed models?
   1. How should naming and folder structure communicate intended joins and model boundaries?

1. What is the standard pattern for mart-layer business logic versus downstream aggregations?

   1. When should a mart be a reusable business-ready table versus a metric- or dashboard-specific aggregate?
   1. Should aggregation models be modeled separately from base marts?
   1. What materialization patterns should we use for base marts versus downstream aggregates?

1. How should metric definitions, model grain, and intended usage be communicated to stakeholders?

   1. Where should documentation live across dbt and BI tools?
   1. How do we make trusted models, metric definitions, and table grain easy to understand and discover?

## Example source system

Assume your app database has these source tables:

```text
app_db.orders
app_db.order_details
app_db.customers
app_db.stores
app_db.payments
app_db.refunds
app_db.products
```

### 1. Raw layer

This is just landed source data.

```text
raw.app_db_orders
raw.app_db_order_details
raw.app_db_customers
raw.app_db_stores
raw.app_db_payments
raw.app_db_refunds
raw.app_db_products
```

### 2. Staging layer

This layer is grouped by **source system**.

```text
models/
  staging/
    app_db/
      stg_app_db__orders
      stg_app_db__order_details
      stg_app_db__customers
      stg_app_db__stores
      stg_app_db__payments
      stg_app_db__refunds
      stg_app_db__products
```

These are still basically one model per source table.

What each staging model does conceptually:

- standardize names
- cast types
- dedupe source rows if needed
- expose one clean version of each source object

### 3. Core layer

This layer is grouped by **business entity / process**.

This is where source tables start being combined into reusable analytics models.

Example structure:

```text
models/
  core/
    customers/
      dim_customers
      customer_store_relationships

    stores/
      dim_stores

    products/
      dim_products

    orders/
      fct_orders
      fct_order_line_items

    payments/
      fct_payments

    finance/
      fct_refunds
```

### 4. Mart layer

This layer is grouped by **business domain / consumer area**.

Example:

```text
models/
  marts/
    finance/
      mart_daily_revenue
      mart_monthly_net_sales
      mart_refund_rates

    marketing/
      mart_customer_ltv
      mart_first_order_cohorts

    product/
      mart_product_sales_daily
      mart_product_attach_rate

    operations/
      mart_store_performance_daily
      mart_order_fulfillment_summary
```

These are curated outputs built from core models.

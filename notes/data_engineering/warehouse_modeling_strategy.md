# Data Warehouse Modeling Strategy

## Overview

This document outlines a scalable data modeling strategy for small to mid sized companies. The approach balances flexibility for BI consumption with engineering rigor around testing, version control, and maintainability.

This is not a one-size-fits-all solution, ultimately every organization must adapt to their unique context and what works for their engineers & business users. But, the principles and structure described here can serve as a strong foundation to build a robust and scalable pattern on to serve data effectively.

______________________________________________________________________

## The Core Problem

When serving data to BI tools, teams face a fundamental tension:

Option A: Let BI tools query fact/dimension tables directly

- Maximum flexibility for slicing and dicing
- Concern: Performance when aggregating hundreds of millions of rows on every dashboard load

Option B: Pre-aggregate everything into custom mart tables

- Better query performance in the BI layer
- Concern: Lots of one-off tables, maintenance burden, inconsistent metrics across dashboards

Neither extreme works well at scale. The solution is a structured layering approach blending both approaches that provides testable, business-logic-applied models without sacrificing flexibility.

______________________________________________________________________

## The Three-Layer Architecture

### Bronze Layer (Raw/Sources)

Purpose: Auditability and replay capability

Characteristics:

- Raw data as received from source systems
- Minimal or no transformation
- Full historical record for reprocessing
- One-to-one mapping with source tables

What lives here:

- Raw API responses
- CDC streams from production databases
- Event logs
- Third-party data dumps

Naming convention: `{source}_{table}`

- Example: `stripe_customers`, `salesforce_accounts`, `app_db_user_subscriptions`, `app_db_users`

______________________________________________________________________

### Silver Layer (Two Phases)

The silver layer is split into two distinct phases, each with a clear purpose.

#### Phase 1: Staging Models

Purpose: Make raw data usable

Characteristics:

- Source-conformed and cleaned
- Properly typed columns
- Deduplicated records
- Renamed columns to standard conventions
- One-to-one with source tables
- No business logic, no joins

Testing focus:

- Data quality: nulls, types, uniqueness
- Freshness checks
- Row count validation

Naming convention: `stg_{source}_{table}`

It's important to identify standards for consistency:

- Column naming
  - e.g., snake_case, no spaces
  - `customer_id` not `custid`
  - Booleans like `is_deleted`, `has_paid` etc w/ consistency
- Timestamp handling (e.g., UTC, consistent formats)
- Data type conventions (e.g., use integers for IDs, decimals for amounts)
- Testing standards (which tests to apply to which columns)
- Incremental Logic (are you using metadata fields or source timestamps across all models?)

#### Phase 2: Fact & Dimension Tables

Purpose: Establish the dimensional models used as building blocks for all reporting & analytics

Characteristics:

- Proper grain defined for each table
- Surrogate keys generated
- Slowly changing dimensions handled
- Relationships between entities clearly modeled
- Still normalized, still building blocks

Testing focus:

- Referential integrity between facts and dimensions
- Grain validation (no duplicates at expected grain)
- Surrogate key uniqueness

Naming convention: `fct_{process}` and `dim_{entity}`

______________________________________________________________________

### Gold Layer

The gold layer serves business consumers and is where testable business logic lives in mart models built from the fact + dimension tables.

#### Entity Marts (Primary)

Purpose: Business-facing interface with logic applied

Characteristics:

- Organized around business entities or processes, not dashboards
- Joins facts and dimensions together
- Applies business logic (revenue recognition, customer segmentation, cohort definitions)
- Remains at row-level grain (no pre-aggregation)
- Extensively tested against business rules

Testing focus:

- Business rule validation
- Reconciliation against control totals (finance reports, CRM exports)
- Metric consistency checks

Naming convention: `mart_{entity}`

Examples:

- `mart_orders` — Every order with all relevant dimensions joined, business logic applied
- `mart_customers` — One row per customer with derived attributes (LTV, segment, status)
- `mart_subscriptions` — Subscription-level grain with MRR calculations, churn flags

Key principle: Build 5-10 entity marts organized around what the business cares about, not what reports someone requested.

For example, `mart_orders` could be used to build:

- Sales performance dashboards
- Customer lifetime value reports
- Product performance analyses
- Instead of building 1 individual table for each of these use cases, build one well-structured `mart_orders` table that serves multiple purposes.
- Then this 1 mart model can be thoroughly tested to ensure all business logic is correct before any BI consumption.

#### Aggregated Tables (When Necessary)

Purpose: Performance optimization for specific use cases

Characteristics:

- Built on top of entity marts, not directly from facts/dims
- Treated as a cache, not a source of truth
- Created only when there's evidence of performance problems
- Documented as derived from the tested mart layer

Naming convention: `agg_{entity}_{grain}`

When to create:

- Sub-second response times required (embedded analytics, customer-facing dashboards)
- Same expensive aggregation runs hundreds of times daily
- Compute costs are a genuine concern

______________________________________________________________________

## Why This Structure Works

### Clear Contracts

Each layer has a defined purpose. New models have an obvious home. Code review is easier because everyone shares the same mental model.

### Testability

Business logic lives in dbt where it can be version controlled and tested before getting sent out to the BI layer. Tests validate the building blocks (silver) and the finished product (gold).

### Debugging Simplicity

When someone says "revenue looks off," the investigation path is clear:

1. Check the mart — is the data correct there?
1. If mart is wrong -> pipeline issue in silver layer
1. If mart is correct -> BI configuration issue

### Flexibility Without Chaos

BI tools query mart tables that have row-level grain. They can aggregate and slice however they want. But they don't define what "revenue" or "active customer" means — those definitions are in your tested mart layer.

### Maintenance Efficiency

At this company size, engineer time spent debugging why two dashboards show different numbers (because they hit different custom marts with different refresh schedules) typically exceeds the compute cost of just structuring things properly upfront.

______________________________________________________________________

## Testing Strategy by Layer

| Layer | Test Types | Examples |
| ------------------- | ------------------------------ | --------------------------------------------------------- |
| Bronze | Freshness, schema validation | Data arrived within SLA, expected columns exist |
| Silver (Staging) | Data quality | Not null, unique keys, accepted values, valid types |
| Silver (Facts/Dims) | Referential integrity, grain | Foreign keys exist, no duplicates at grain |
| Gold (Marts) | Business rules, reconciliation | Revenue >= 0, totals match finance, segment logic correct |

______________________________________________________________________

## The BI Layer's Responsibility

With this structure, BI tools become responsible only for:

- Aggregation (sum, count, avg)
- Filtering and slicing
- Visualization
- Dashboard-level caching/extracts (if supported)

They do NOT define:

- What "revenue" means
- Which customers count as "active"
- How cohorts are calculated
- Any business logic

______________________________________________________________________

## When to Create Pre-Aggregated Tables

Before building an aggregated table, ask:

1. Can the mart be queried directly with acceptable performance? -> Do that
1. Is it slow because of missing clustering/partitioning? -> Fix the underlying model
1. Is it slow because of genuinely expensive aggregations running repeatedly? -> Consider an aggregate, but make it general-purpose

______________________________________________________________________

## Practical Workflow

1. dbt runs and refreshes all layers
1. dbt tests validate each layer (data quality -> referential integrity -> business rules)
1. If tests pass, marts are "released" and BI tools query fresh data
1. If tests fail, the pipeline errors out, Data Team is alerted, and investigation begins immediately
1. (Optional) Provide automated messaging to stakeholders if key business rule tests fail in the Gold Layer
   1. For Example, if `mart_orders` revenue test fails, send alert that the 4 downstream dashboards relying on it may be impacted.

This ensures the data contract is enforced before consumption.

______________________________________________________________________

## Example dbt Project Structure

```
dbt_project/
├── dbt_project.yml
├── packages.yml
│
├── models/
│   │
│   ├── staging/                     # Silver Phase 1
│   │   ├── staging.yml              # Source definitions
│   │   │
│   │   ├── stripe/
│   │   │   ├── _stripe__sources.yml
│   │   │   ├── _stripe__models.yml  # Tests for staging models
│   │   │   ├── stg_stripe__charges.sql
│   │   │   ├── stg_stripe__customers.sql
│   │   │   └── stg_stripe__subscriptions.sql
│   │   │
│   │   ├── salesforce/
│   │   │   ├── _salesforce__sources.yml
│   │   │   ├── _salesforce__models.yml
│   │   │   ├── stg_salesforce__accounts.sql
│   │   │   ├── stg_salesforce__opportunities.sql
│   │   │   └── stg_salesforce__contacts.sql
│   │   │
│   │   └── app_db/
│   │       ├── _app_db__sources.yml
│   │       ├── _app_db__models.yml
│   │       ├── stg_app__users.sql
│   │       ├── stg_app__orders.sql
│   │       └── stg_app__order_items.sql
│   │
│   ├── intermediate/                # Optional: Complex transformations
│   │   ├── _intermediate__models.yml
│   │   ├── int_orders__pivoted.sql
│   │   └── int_customer__unioned.sql
│   │
│   ├── core/                        # Silver Phase 2: Facts & Dimensions
│   │   ├── _core__models.yml        # Referential integrity tests
│   │   │
│   │   ├── fct_orders.sql
│   │   ├── fct_subscriptions.sql
│   │   ├── fct_payments.sql
│   │   │
│   │   ├── dim_customers.sql
│   │   ├── dim_products.sql
│   │   ├── dim_dates.sql
│   │   └── dim_geography.sql
│   │
│   └── marts/                       # Gold Layer
│       ├── _marts__models.yml       # Business rule tests
│       │
│       ├── mart_orders.sql          # Row-level, all logic applied
│       ├── mart_customers.sql       # One row per customer, derived attrs
│       ├── mart_subscriptions.sql   # MRR, churn flags, lifecycle stage
│       ├── mart_products.sql        # Product performance metrics
│       │
│       └── aggregates/              # Performance optimizations (if needed)
│           ├── _aggregates__models.yml
│           ├── agg_orders__daily.sql
│           └── agg_revenue__monthly.sql
│
├── tests/                           # Custom data tests
│   ├── assert_revenue_positive.sql
│   ├── assert_orders_reconcile_to_finance.sql
│   └── assert_customer_segments_complete.sql
│
├── macros/
│   ├── generate_surrogate_key.sql
│   ├── cents_to_dollars.sql
│   └── fiscal_quarter.sql
│
└── seeds/
    ├── finance_control_totals.csv   # For reconciliation tests
    └── country_codes.csv
```

______________________________________________________________________

## Example: From Normalized Source to Denormalized Mart

This example illustrates how five normalized application database tables flow through the warehouse layers, consolidating into two fact tables, two dimension tables, and ultimately one mart model.

### Why This Transformation Matters

Transactional databases (PostgreSQL, MySQL) are optimized for:

- Data integrity via normalization
- Minimizing redundancy to prevent update anomalies
- Fast writes and ACID compliance
- Many small, related tables connected by foreign keys

Analytical warehouses (Snowflake, BigQuery) are optimized for:

- Query performance on large datasets
- Denormalization to reduce joins at query time
- Accepting data redundancy in exchange for read speed
- Wide tables that contain everything needed for analysis

The warehouse transformation takes normalized source data and intentionally denormalizes it for analytical consumption.

### Source Tables (Application Database)

A typical e-commerce application database might have these five normalized tables:

```
┌────────────────────────────────────────────────────────────────────────────┐
│                        APPLICATION DATABASE (PostgreSQL)                   │
│                                                                            │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                     │
│  │   users     │    │   orders    │    │ order_items │                     │
│  ├─────────────┤    ├─────────────┤    ├─────────────┤                     │
│  │ id (PK)     │◄───│ user_id(FK) │    │ id (PK)     │                     │
│  │ email       │    │ id (PK)     │◄───│ order_id(FK)│                     │
│  │ name        │    │ status      │    │ product_id  │───►┌─────────────┐  │
│  │ created_at  │    │ created_at  │    │ quantity    │    │  products   │  │
│  └─────────────┘    │ shipping_   │    │ unit_price  │    ├─────────────┤  │
│                     │ address_id  │───►└─────────────┘    │ id (PK)     │  │
│                     └─────────────┘                       │ name        │  │
│                            │                              │ category    │  │
│                            ▼                              │ brand       │  │
│                     ┌─────────────┐                       └─────────────┘  │
│                     │  addresses  │                                        │
│                     ├─────────────┤                                        │
│                     │ id (PK)     │                                        │
│                     │ street      │                                        │
│                     │ city        │                                        │
│                     │ state       │                                        │
│                     │ postal_code │                                        │
│                     │ country     │                                        │
│                     └─────────────┘                                        │
└────────────────────────────────────────────────────────────────────────────┘
```

This normalized structure makes sense for the application:

- User email changes update one row, not hundreds of order records
- Product details are stored once, referenced by foreign key
- Address data isn't duplicated across orders

But for analytics, this means every query requires 4-5 joins.

### Bronze Layer

Raw tables land as-is from the source system via CDC or batch extraction:

- `app_db_users`
- `app_db_orders`
- `app_db_order_items`
- `app_db_products`
- `app_db_addresses`

### Silver Layer: Staging (5 Models)

Each source table gets a corresponding staging model. These clean and rename but don't join:

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                           STAGING MODELS (1:1 with source)                   │
│                                                                              │
│   stg_app_db_users          stg_app_db_orders         stg_app_db_order_items │
│   stg_app_db_products       stg_app_db_addresses                             │
│                                                                              │
│   Purpose: Clean, rename, type, dedupe. No joins, no business logic.         │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Silver Layer: Facts & Dimensions (4 Models from 5 Staging Models)

Now we model for analytics. The five staging models consolidate into four core models:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CORE LAYER                                     │
│                                                                             │
│  FACT TABLES (events/transactions)      DIMENSION TABLES (entities)         │
│  ┌──────────────────────────────┐       ┌──────────────────────────────┐    │
│  │        fct_orders            │       │       dim_customers          │    │
│  │  ← stg_app_db_orders         │       │  ← stg_app_db_users          │    │
│  │  ← stg_app_db_addresses      │       │  ← stg_app_db_addresses      │    │
│  │                              │       │                              │    │
│  │  (address denormalized in)   │       │  (latest address included)   │    │
│  └──────────────────────────────┘       └──────────────────────────────┘    │
│                                                                             │
│  ┌──────────────────────────────┐       ┌──────────────────────────────┐    │
│  │      fct_order_items         │       │       dim_products           │    │
│  │  ← stg_app_db_order_items    │       │  ← stg_app_db_products       │    │ 
│  └──────────────────────────────┘       └──────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

Notice that `stg_app_db_addresses` feeds into multiple models. This is intentional denormalization:

- `fct_orders` includes the shipping address at time of order (point-in-time snapshot)
- `dim_customers` includes the customer's current address

### Gold Layer: Mart (1 Model from 4 Core Models)

Finally, the mart joins everything together into one wide, analysis-ready table:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              MART LAYER                                      │
│                                                                             │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │                         mart_orders                                 │    │
│  │                                                                     │    │
│  │   ← fct_orders                                                      │    │
│  │   ← fct_order_items (aggregated to order grain)                     │    │
│  │   ← dim_customers                                                   │    │
│  │   ← dim_products (for category/brand attributes)                    │    │
│  │                                                                     │    │
│  │   Contains: order details, customer attributes, product mix,        │    │
│  │             shipping geography, business logic (recognized revenue, │    │
│  │             first order flag, order size tier, etc.)                │    │
│  │                                                                     │    │
│  │   Grain: One row per order                                          │    │
│  │   Width: 30+ columns (everything needed for order analysis)       │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### The Complete Flow

```
APPLICATION DB          BRONZE           SILVER              SILVER            GOLD
(Normalized)            (Raw)            (Staging)           (Core)            (Mart)
─────────────────────────────────────────────────────────────────────────────────────

users ─────────────► raw.users ───► stg_app__users ────┐
                                                       ├──► dim_customers ───┐
addresses ─────────► raw.addresses► stg_app__addresses─┤                     │
                                                       │                     │
                                                       └──► fct_orders ──────┼──► mart_orders
orders ────────────► raw.orders ──► stg_app__orders ──────►                  │
                                                                             │
order_items ───────► raw.order_items► stg_app__order_items► fct_order_items─┤
                                                                             │
products ──────────► raw.products ► stg_app__products ───► dim_products ────┘


Tables:    5              5                5                   4                 1
```

### What Gets Denormalized Where

| Source Field | Normalized Location | Denormalized Into |
| ---------------- | ------------------- | --------------------------------------------------------- |
| User email | `users.email` | `dim_customers.email`, `mart_orders.customer_email` |
| User name | `users.name` | `dim_customers.name`, `mart_orders.customer_name` |
| Shipping city | `addresses.city` | `fct_orders.shipping_city`, `mart_orders.shipping_city` |
| Shipping state | `addresses.state` | `fct_orders.shipping_state`, `mart_orders.shipping_state` |
| Product category | `products.category` | `dim_products.category`, `mart_orders.primary_category` |
| Product brand | `products.brand` | `dim_products.brand`, `mart_orders.primary_brand` |

Yes, this means `customer_email` might exist in multiple places. That's the tradeoff: we accept redundancy in exchange for queries that don't require joins.

### Query Performance Impact

Before (querying normalized source):

```sql
-- 5 table joins for a simple order report
SELECT 
    o.id,
    u.email,
    u.name,
    a.city,
    a.state,
    SUM(oi.quantity * oi.unit_price) as order_total
FROM orders o
JOIN users u ON o.user_id = u.id
JOIN addresses a ON o.shipping_address_id = a.id
JOIN order_items oi ON oi.order_id = o.id
JOIN products p ON oi.product_id = p.id
WHERE o.created_at >= '2024-01-01'
GROUP BY o.id, u.email, u.name, a.city, a.state
```

After (querying mart):

```sql
-- Zero joins, everything pre-computed
SELECT 
    order_id,
    customer_email,
    customer_name,
    shipping_city,
    shipping_state,
    order_total
FROM mart_orders
WHERE created_at >= '2024-01-01'
```

The mart query is simpler to write, easier to understand, and significantly faster to execute.

______________________________________________________________________

## Example Reconciliation Test

```sql
-- tests/assert_orders_reconcile_to_finance.sql

with mart_total as (
    select sum(recognized_revenue) as total
    from {{ ref('mart_orders') }}
    where created_at >= '2024-01-01'
      and created_at < '2024-04-01'
),

finance_total as (
    select expected_revenue as total
    from {{ ref('finance_control_totals') }}
    where period = '2024-Q1'
)

-- Test fails if any rows returned
select *
from mart_total
cross join finance_total
where abs(mart_total.total - finance_total.total) > 100
```

______________________________________________________________________

## Key Takeaways

1. Establish structure early. The cost of restructuring a production warehouse far exceeds the cost of upfront design work.
1. Two-phase silver layer is essential. Separating staging (cleaning) from dimensional modeling (facts/dims) prevents messy models trying to do too much.
1. Build marts around business entities, not dashboards. Five to ten well-structured marts beat fifty one-off tables.
1. Test the finished product, not just the building blocks. Business rule validation happens at the mart layer before BI consumption.
1. Let BI tools handle aggregation and visualization. They should not define what metrics mean.
1. Pre-aggregate only with evidence. Wait until you have proof that performance is a problem before adding complexity.
1. Document and commit to the pattern. When the whole team shares the same mental model, everything moves faster.

# Semantic Layers

## Baseline

To understand semantic layers, it's helpful to start with a baseline of a common modern data stack architecture and how it serves the business.

For sake of argument, assume you're in a data team of 3 people, 5 stakeholder teams, sub-100 headcount. Data team solely owns the BI tool; only the team can change metrics or calcs.

- Bronze: raw loads from 3rd party and internal DB into Snowflake.
- Silver staging: 1:1 with bronze, normalizes columns/types, light testing.
- Silver fact + dim: business logic, some multi-table joins.
- Gold marts: join facts + dims, more business logic, aggregate, pre-compute all metrics.
- BI tool loads marts, serves dashboards. Instant because everything is pre-computed.
- dbt docs (static site) exposes definitions, metrics, dashboard links to stakeholders.

### What a semantic layer actually is

A semantic layer owns metric and dimension definitions independently of physical storage. Define a metric once, query it consistently no matter who asks or how they slice it. The core phrase: "define once, query anywhere."

It solves two distinct problems:

1. Definition consistency. One enforced source of truth, so "revenue" and "active user" can't drift across dbt, the BI tool, and ad-hoc queries.
1. Dynamic aggregation. A metric is defined atomically and the layer compiles SQL on demand for whatever grain/slice the consumer asks. You don't pre-decide the grain.

### How the existing setup maps to semantic-layer concepts

- The gold marts are a hand-built, materialized semantic layer. Grains and joins picked up front, metrics pre-computed, then frozen.
- Consistency is solved through ownership, not tooling. With 3 people owning everything and a locked-down BI tool, definition drift is governed socially. The semantic layer's enforcement pitch buys little here.
- dbt docs is passive documentation. It describes the contract but does not enforce it. A semantic layer is an active query interface that owns the definition. Not needed when the team is the only author.

### The real tradeoff: build time vs runtime

The strongest argument for the current approach is an engineering principle, not a data fad: push computation and validation to build time, where the result is a materialized artifact that can be tested, rather than runtime, where it is ephemeral and cannot.

- Materialized mart: assert row counts, non-negative metrics, sane deltas, totals equal sum of parts. Tested artifact at rest.
- Runtime-compiled SQL (BI-layer or semantic-layer serving): result exists only for one query. Underlying facts/dims can pass every test while a fanout join or wrong filter context silently doubles a number. Nothing to test.

This is the regression to avoid in a setup that cares about validation.

### Where pre-computation genuinely hits a wall

The boundary is additive vs non-additive metrics.

- Additive metrics (sums) compose. A single low-grain mart (for example revenue by day by product by region) lets the BI tool roll up to any combination of those dimensions for free. Test the atomic mart once. No semantic layer needed for this slicing.
- Non-additive metrics over arbitrary slices are the wall. Distinct counts (DAU/WAU/MAU, distinct accounts), ratios where the denominator shifts with the slice (conversion, AOV, retention), medians/percentiles. DAU cannot be summed into MAU. You cannot pre-compute distinct active users for every possible user-dragged date range.

OBT covers the additive long-tail (a wide atomic table the BI tool rolls up). It does NOT close the non-additive arbitrary-slice gap. Pitch OBT precisely: additive long-tail yes, non-additive arbitrary slice stays a one-off analyst query against silver. Claiming OBT solves all slicing is the one place the argument is unsound as stated.

### dbt options

- Define side is open source: dbt-core and MetricFlow. Write semantic models and metric YAML, query locally via MetricFlow CLI. The new MetricFlow spec (Fusion engine) is coming to dbt Core in 1.12.
- Serve side is gated: the Semantic Layer API (JDBC/GraphQL endpoint a BI tool connects to) requires dbt Cloud. Basic features start on the Starter plan (~$100/dev/mo); full feature set is Enterprise (~$50k/yr).
- So "you need dbt Cloud" is correct for production serving, not strictly Enterprise.

Headless alternatives that live outside the BI tool:

- Cube: most adopted open-source headless layer, own SQL/REST/GraphQL APIs and caching. Tradeoff is a separate server to operate.
- Lightdash, Omni: lighter, integrate tightly with dbt models.
- Snowflake Semantic Views: warehouse-native, definitions live as Snowflake objects, no third-party server. Best fit for a Snowflake stack and closest to the "testable, owned definition" philosophy.

### Snowflake Semantic Views (2026 mechanics)

Define logical tables over physical fact/dim tables, declare joins once as named relationships, define dimensions and metrics on top. The planner generates join SQL from the relationships when a metric is requested by a dimension.

```sql
CREATE SEMANTIC VIEW sales_analysis
  TABLES (
    orders AS fct_orders PRIMARY KEY (order_id),
    customers AS dim_customer PRIMARY KEY (customer_id)
  )
  RELATIONSHIPS (
    orders_to_customers AS orders (customer_id) REFERENCES customers (customer_id)
  )
  FACTS (orders.order_amount AS order_total)
  DIMENSIONS (
    customers.region AS customer_region,
    orders.order_date AS order_date
  )
  METRICS (
    orders.total_revenue AS SUM(orders.order_total),
    orders.distinct_customers AS COUNT(DISTINCT orders.customer_id)
  );
```

- Strict clause order: TABLES, RELATIONSHIPS, FACTS, DIMENSIONS, METRICS. Wrong order errors out.
- Dimensions can be flagged non-additive for a metric (encodes the additive/non-additive distinction). Facts/metrics can be marked private.
- Queried with non-standard SQL: `SELECT * FROM SEMANTIC_VIEW(view METRICS ... DIMENSIONS ...)`.
- Semantic views are code: git-versionable, CI/CD deployable, manageable through dbt.

### The consumption problem (the deciding factor)

The query uses `SEMANTIC_VIEW(...)`, which is non-standard SQL. An arbitrary BI tool emitting normal SELECTs does not know how to construct it. Consumption must be explicitly supported, and in 2026 that support is fragmented.

- First-class consumer is AI: semantic views power Cortex Analyst, Cortex Agents, Snowflake Intelligence. The headline use case is the natural-language path, which is the part being distrusted.
- Traditional BI is patchy: native Tableau TDS export, partners (Sigma, Omni, Honeydew, Hex) in varying maturity, some still in preview.
- Power BI: hard no. Microsoft has publicly stated it will not support third-party semantic models in the Power BI front end. The workaround runs the other way (ingest a Power BI model into Snowflake to generate a semantic view).

Read: Snowflake Semantic Views are an AI-first feature wearing a BI label. The consumption surface they are built for is agents, not dashboards. The dashboard-serving path is the weakest part.

### Anthropic / OpenAI Snowflake integrations

Both are model-provider deals that power the AI consumption surface, not BI integrations.

- Anthropic: $200M partnership (Dec 2025), Claude in Cortex AI across all major clouds, expanded at Snowflake Summit 26 (June 2026). Powers Cortex agents over governed data.
- OpenAI: $200M partnership (Feb 2026), models in Cortex AI Functions, REST API, Snowflake Intelligence, Cortex Code. GPT-5.5 in preview April 2026. Also an Azure OpenAI route via Microsoft.

These supply the reasoning engine behind Cortex Analyst/Agents. The semantic view supplies governed definitions and join logic; the model interprets natural language against it; the consumer is a chat/agent interface, not a locked-down BI tool. None of it solves serving governed metrics to BI stakeholders.

The bet shape: ~$400M across both deals, all aimed at making natural-language-over-governed-data trustworthy. The celebrated number is ~90%+ accuracy on complex text-to-SQL on internal benchmarks. For a trust-asymmetry argument, ~90% with silent confident failures is the wrong profile for a board-deck foundation.

### The position (how it connects)

Trust is the currency. It is slow to build and instant to lose. A dashboard backed by a tested mart has a bounded, known failure surface. An AI answer has an unbounded, silent, confident one. For a foundation, prefer the boring bounded failure mode.

Three things to keep straight:

1. Separate the semantic model from AI delivery. The semantic layer is a governance/definition artifact; AI delivery is a consumption surface. Adopt one without the other. A governed layer can be adopted for purely deterministic reasons (tool-queried, no LLM).
1. Additive, not replacement. Even in a trustworthy-AI future, pre-computed dashboards stay the right tool for stable, high-traffic, board-deck questions. A governed AI surface absorbs the exploratory long-tail that currently routes to a human. The deterministic core stays the foundation because it is the part that can be trusted.
1. "Proven" is an internal bar, not a press release. The trigger is running it against own data, definitions, and stakeholder questions and deciding the failure rate and mode are acceptable for the bounded job. Already tested and unimpressed, which is the right instinct.

Triggers that would change the calculus:

- Mart sprawl becomes the dominant maintenance cost (near-duplicate marts differing only by grain/dimension).
- A second consumption surface appears beyond the owned BI tool (reverse ETL, internal app, notebook-heavy analysts).
- Metric definitions become contested across teams and need enforcement rather than a doc page.
- The human-expert model hits its scaling ceiling as the org grows (volume of unanticipated questions saturates a 3-person team).

### Takeaways

Delivering value through data is about trust, and trust has an asymmetric failure profile. AI consumption today, in the only form the current architecture supports (ungoverned text-to-SQL), has an unbounded silent-failure surface, which is wrong for a foundation. Warehouse-native implementations tested and found immature. So anchor on proven, testable, deterministic delivery: dashboards and governed self-service, with the team as the expert layer for the long tail.

Keep the deterministic core as the trust foundation indefinitely. Adopt a governed semantic layer if and when a deterministic driver justifies it. Layer AI consumption on top only for the exploratory long-tail, and only once verified against an internal trust bar. Never frame it as AI replacing the proven thing, because the proven thing is what makes the whole stack trustworthy.

Why the framing matters: "I will switch when AI can replace dashboards" sounds like waiting to rip out a working system. "I keep the deterministic core as the trust foundation and add governed, AI-assisted exploration for the long-tail when it is proven against my own bar" sounds like someone who knows what each tool is for and will not be sold a replacement narrative.

# Data Team Responsibilites

## Core Pillars

1. Analytics & reporting. Serving data to internal humans for decisions: dashboards, metrics, ad hoc analysis, exec/board reporting. The deliverable is a trustworthy, repeatable answer layer.

1. Foundation. The base that everything else runs on: warehouse, ingestion, orchestration, transformation framework, CI/CD, cost control, plus governance, quality, and compliance. Horizontal, no business KPI of its own, justified by leverage and risk.

1. User-facing data products. Data fed back into the end-user experience, in one of two modes:

- Serving data directly: the numbers themselves are the feature (embedded/customer-facing dashboards, usage analytics, sold data feeds).
- Moving a KPI via a model: data drives a decision the user experiences but doesn't see as data (recommendations, search ranking, personalization, fraud scoring, pricing).

Highest leverage, but the most technical. The consumer is the end user, not an internal team.

4. Activation. Pushing modeled data out to internal operational systems: CDPs, CRMs, ad platforms, support tools (reverse ETL). The consumer is another team's system, not a person reading a chart. This is the most optional of all 4, some business models don't need it.

## Analytics & Reporting

Stakeholders & value. Execs, ops, product, finance, plus whoever owns the upstream source data you depend on. Value is faster, trustworthy decisions and removing the analyst bottleneck: questions get answered repeatably instead of one-off. Without it every decision is a fresh manual pull.

What gets built. SQL (with some Python for ad hoc) -> dbt, a warehouse, a BI tool, mart models that feed into dashboards, a defined metric catalog, and a self-serve ad hoc workflow. The work front-loads light and back-loads heavy: the language is simple, the modeling and enrichment layer is where the real work lives.

How success is judged. Trust (do numbers reconcile and match across surfaces), time-to-answer, and adoption. No revenue KPI of its own; it is judged on whether people rely on it.

Where it breaks & consequences. Metric drift and definition sprawl (two dashboards disagree, trust collapses), silent upstream schema changes, stale data behind a fresh-looking chart. Blast radius is usually reputational and decision-quality rather than direct revenue, but lost trust is slow to rebuild.

## Foundation

Stakeholders & value. The other three pillars are the stakeholders; the data team itself is the primary customer. Value is pure leverage: every other bucket can exist and ship fast, cost stays bounded, and compliance risk stays contained. The counterfactual is no analytics and no products at all, so it is justified by enabling everything above it, not by a metric of its own.

What gets built. Database / warehouse management, cloud infrastructure, orchestration, transformation framework, CI/CD, secrets management, plus the horizontal concerns of governance, data quality, lineage, cost control, and compliance. Typically in Python, Terraform, Bash etc.

How success is judged. Reliability (uptime, pipeline success rate), cost vs value added, can analysts, analytics engineers, and data engineers ship solutions quickly without the infra getting in the way? Explicitly judged on leverage and risk, with no business KPI of its own. Naming that directly is what keeps the section from sounding like plumbing.

Where it breaks & consequences. Pipeline failures that cascade into every downstream pillar, runaway warehouse cost, a CI/CD gap that lets a bad change reach production, a governance or compliance miss. Blast radius is the widest of any bucket precisely because everything sits on top of it: a Foundation failure can take down analytics, activation, and products at once.

## User-facing Data Products

Stakeholders & value. Product, engineering, and the end user (external customer). For mode (a) the stakeholder is whoever owns the product surface or the data-feed contract; for mode (b) it is product plus whatever team owns the KPI. Value is data becoming part of the product itself: a sellable/retained feature, or the lever that moves a user-facing metric. Without it the experience is static.

What gets built.

- Mode (a), serving data directly: SQL/Python -> warehouse, an API or serving layer, a frontend -> embedded dashboards, usage analytics, sold data feeds. Because this is user-facing, this typically involves a higher engineering standard, SLAs, and more rigor to get it right.
- Mode (b), moving a KPI via a model: Python -> feature store, training pipeline, model registry, serving infra -> recommendations, ranking, personalization, fraud scoring, pricing. Much more complex work, multiple services/workflows needed, ML + engineering talent, and the stakes are higher because it's directly customer-facing and can impact the user experience either positively or negatively.

How success is judged.

- Mode (a): tenant SLAs (uptime, latency, freshness), isolation correctness, no cross-tenant leakage.
- Mode (b): the measured KPI delta the model is meant to move, plus serving latency, model freshness, and guardrail metrics.

Where it breaks & consequences. Mode (a): a tenant boundary leak exposes one customer's data to another, the highest-consequence failure in the doc. Mode (b): model drift, training/serving skew, a bad score shipped at scale (wrong fraud flags, harmful recommendations). Consequences are direct: customer-facing, contractual, and in the leak case a security incident.

## Activation

Stakeholders & value. The teams that own the destination systems: marketing, sales ops, support, growth. The consumer is their system; the stakeholder is the team you negotiate field mappings and freshness with. Value is letting those teams act on modeled data inside their own tools without manual CSV exports, closing the loop between warehouse and operations.

What gets built. Automated syncs that push modeled data from the internal warehouse out to the third party tools: CDPs, CRMs, ad platforms etc. Data typically modeled in SQL, export built in Python, and the sync itself is either a reverse ETL tool or a custom-built sync. The warehouse is the source of truth, and the syncs push segments, scores, and traits into the destination systems.

How success is judged. Data & sync reliability, freshness in the destination, and field-mapping correctness. The awkward part: the actual win shows up in another team's KPI (better-targeted campaigns, faster resolution), not a number you own, which makes activation easy to undersell while it's still important to the business.

Where it breaks & consequences. Destination API limits and rate caps, schema mismatches between warehouse and tool, partial syncs that leave systems disagreeing, PII pushed where it shouldn't go. Consequences range from a broken campaign to a compliance exposure when sensitive fields land in the wrong platform.

## Tools

- Warehouse (Snowflake)
- BI Tool (Looker, Metabase, Lightdash)
- Orchestration (Airflow)
- Ingestion (Python, Airflow)
- Transformation framework (dbt)
- Catalog (dbt docs)
- Optional CDP (Segment)

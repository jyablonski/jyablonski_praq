# Data Catalog Overview

## What Is a Data Catalog?

A data catalog is a centralized inventory of an organization's data assets — tables, views, dashboards, pipelines, ML features, and the metadata that describes them. It answers the questions "what data do we have, where does it live, what does it mean, and can I trust it?"

Think of it as the index for a data platform: it doesn't store the data itself, but it stores rich metadata *about* the data — schemas, ownership, lineage, freshness, quality scores, descriptions, tags, and usage statistics.

This doc is specifically referencing data catalogs like OpenMetadata or dbt Docs, not Lakehouse catalogs like Unity Catalog or Polaris, which are more about access control and governance than discovery and documentation.

## What They're Used For

- Discovery — find the right table or dashboard without pinging six people on Slack. Full-text search across names, columns, and descriptions.
- Lineage — trace a column upstream to its source or downstream to every dashboard it feeds. Critical for impact analysis before a breaking change.
- Trust & governance — surface freshness, test results, ownership, and certification status so consumers know whether an asset is production-grade.
- Documentation — a single home for column-level descriptions, business glossary terms, and tribal knowledge that would otherwise rot in wikis.
- Compliance — tag and track PII/sensitive fields, manage access policies, and support audit requirements.

## Intended Users & Purpose

| User | What they get out of it |
| --------------------- | -------------------------------------------------------------- |
| Data engineers | Lineage for impact analysis, schema change tracking, ownership |
| Analysts / scientists | Self-serve discovery, trustworthy tables, documentation |
| Analytics engineers | dbt model docs, test coverage, downstream consumers |
| Data platform team | Governance, deprecation workflows, usage metrics |
| Stakeholders / PMs | Business glossary, certified dashboards, data definitions |

The core purpose is to reduce the time-to-find and time-to-trust for any data asset, and to give the platform team a control plane for governance.

## Questions a Data Catalog Answers

Without a catalog, each of these turns into a Slack thread, a tribal-knowledge hunt, or a guess. With one, they're a search box away:

1. "Which table should I actually use?" — There are four tables with `orders` in the name. Which is the certified, production one, and which are abandoned dev experiments nobody deleted?

1. "If I change this column, what breaks?" — Before altering or dropping a field, what models, dashboards, reports, and downstream consumers depend on it? Without lineage, you find out when something breaks in prod.

1. "Who owns this, and who do I ask?" — A table looks wrong or stale. Who's responsible for it, and who do I escalate to — without pinging the whole data channel hoping someone recognizes it?

1. "Can I trust this number?" — Is this table fresh? Did its tests pass? When did it last load successfully? Is it certified, or is someone querying a half-built model that loads three days late?

1. "What does this column even mean?" — Is `status = 3` "shipped" or "refunded"? Does `revenue` include tax? Is `active_user` a 30-day or 7-day definition? The business meaning usually lives in one person's head.

1. "Where does this dashboard's data come from?" — An exec's KPI looks off. What's the full path from source system → warehouse → model → dashboard, so I can trace where it went wrong?

1. "Where does PII live?" — For a deletion request, audit, or access review, which tables and columns contain personal or sensitive data, and who can currently query them?

The common thread: in each case the answer *exists* somewhere — in someone's memory, a buried wiki page, or by reverse-engineering SQL — but a catalog makes it discoverable instead of dependent on finding the right person on the right day.

## Static vs. Live: dbt docs vs. OpenMetadata

The biggest fork in catalog tooling isn't features — it's whether the catalog is a static artifact or a live service. This is the distinction that determines which questions it can actually answer.

Static (dbt docs). `dbt docs generate` produces a snapshot at build time: a self-contained static site reflecting the state of your project *as of that run*. It's built from artifacts your pipeline already emits (`manifest.json`, `catalog.json`), version-controlled next to the code, and reviewed in PRs. That makes it excellent at the *reference documentation* job — answering the simple, static questions:

- Model and column descriptions
- Column-level lineage *within dbt*
- Test definitions and which models they cover
- A searchable site for "which table should I use?" and "what does this column mean?"

But it's a photograph, not a feed. It only knows about dbt, and only what was true at generation time. Nothing dynamic is hooked up to it, so it can't tell you whether a table loaded this morning, how stale it is right now, or what's happening in the orchestrator or BI tool. The *trust* questions — "is this fresh? did last night's run pass? can I rely on this number?" — are simply out of scope.

Live (OpenMetadata). A dedicated catalog is a running service that *continuously ingests* metadata from across the platform — recent dbt run results, orchestrator run history, warehouse profiling, BI usage — and presents it as current state. That's what unlocks the operational layer dbt docs structurally can't reach:

- Freshness and last-successful-load per table
- Recent test pass/fail *results*, not just test definitions
- Pipeline run status, and end-to-end lineage spanning dbt *plus* the orchestrator, warehouse, and dashboards
- Usage and profiling metrics on the actual data

The catch is that "live" means infrastructure. You're no longer shipping a static site from CI — you're operating a service with a metadata database, a search index, and a recurring ingestion pipeline. That's a genuine architecture shift, not a bigger version of dbt docs.

| | dbt docs (static) | OpenMetadata (live) |
| -------------------------------------------- | ----------------------------------- | ------------------------------------------ |
| Form | Static site, generated at build | Running service + stateful deps |
| Metadata freshness | Snapshot as of last `docs generate` | Continuously ingested |
| Scope | dbt only | dbt + orchestrator + warehouse + BI |
| "What / where / meaning" | Yes | Yes |
| "Is it fresh / did it pass / can I trust it" | No | Yes |
| Live metrics & run status | No | Yes |
| Operational cost | ~free to host static site | Service to host, scale, and keep ingesting |

The mental model: dbt docs answer questions about your *code*; a live catalog answers questions about your *data*. Static docs tell you a column is *supposed* to be a fresh daily revenue total; a live catalog tells you whether today's load actually landed.

## How They're Updated

Catalogs are kept current through ingestion connectors, broadly in two styles:

- Pull-based (most common) — the catalog runs scheduled ingestion jobs that connect to source systems (warehouse, orchestrator, BI tool) and scrape metadata on a cron. Low coupling; the catalog owns the refresh cadence.
- Push-based / event-driven — sources emit metadata events (e.g. via an API or message bus) as changes happen, giving near-real-time updates at the cost of more integration work in each producing system.

Typical sources include the warehouse information schema, dbt artifacts (`manifest.json`, `run_results.json`), the orchestrator's run history, and BI tools. Many teams run ingestion as an orchestrated job (an Airflow/Dagster DAG) so it sits alongside the rest of the platform.

### How They're Updated — Source of Truth

Different metadata has different owners. The rule that prevents drift: one source of truth per asset type, and disable editing everywhere else.

- Definitions for modeled assets — dbt is the source of truth. Descriptions live as `description:` fields in schema YAML, reviewed in PRs, and OpenMetadata ingests them from dbt artifacts and *presents* them. Disable (or ignore) UI edits for these, or the next ingestion run will clobber them — or create silent drift if it doesn't.
- Business glossary — catalog-native. Terms like "Active Customer" or "MRR" don't map 1:1 to dbt models, so they're managed in OpenMetadata's Glossary feature by stewards, usually behind an approval workflow. Optionally manage it as-code via OpenMetadata's CSV import / API if you want a git-backed glossary, but the catalog remains the source of truth. Glossary terms are then *linked* to columns and tables.
- Certified dashboards & certification status — catalog-native. Dashboards live in the BI tool, not dbt; certification is a tag applied by a steward in the catalog.

In short: dbt owns what's in dbt and OpenMetadata reflects it; the glossary and certification are owned and presented by the catalog itself.

## How They're Hosted

Most open-source catalogs ship as containers and are deployed however the platform team prefers:

- Docker / Docker Compose — quickest path for a POC or small team; one command brings up the app plus its backing stores.
- Kubernetes / Helm — the standard for production. Run the app as a Deployment, scale ingestion workers independently, and externalize the metadata DB and search index to managed services (RDS, OpenSearch).
- Managed / SaaS — vendor-hosted offerings exist if you'd rather not operate it yourself.

A catalog almost always needs two stateful dependencies: a relational store for the metadata graph and a search index for fast discovery. In K8s these are usually externalized rather than run as in-cluster StatefulSets.

## When to Adopt a Data Catalog

A dedicated catalog is operational overhead — a service, a database, a search index, and an ingestion pipeline to keep running. For a small or early team, that cost usually outweighs the benefit. Start simpler and graduate when you feel the pain:

1. A Google Doc / wiki — fine when "what data do we have?" is answerable by a few people and a single page. Source of truth is the doc.
1. dbt docs — once you're modeling in dbt, `dbt docs` gives you descriptions, column-level lineage, and a searchable site essentially for free, version-controlled and reviewed in PRs. It's *static* — a snapshot of your code, not a live view of your data — but for many teams that's the right stopping point for a long time.
1. A dedicated catalog (OpenMetadata, etc.) — adopt when you outgrow dbt docs, signaled by things like:
   - Lineage and assets that span beyond dbt — orchestrator pipelines, BI dashboards, raw/external sources, streaming — that dbt docs can't see.
   - Enough people that self-serve discovery and search across *everything* matters more than a static site.
   - A need for governance features dbt docs don't provide: a managed glossary with approvals, certification workflows, PII tagging, data-quality and freshness signals in one place, ownership and deprecation tracking.
   - Cross-system impact analysis ("what breaks downstream of this column, including dashboards?") becoming a recurring, expensive question.

The migration is low-regret because dbt docs *become an input* to the catalog rather than getting thrown away — OpenMetadata ingests the same dbt artifacts. The real change isn't the metadata, it's the move from a static artifact to a live service: you're standing up a running system and an ingestion pipeline to add a presentation and governance layer on top of metadata you already produce.

One of the strongest adoption triggers is organizational, not just scale: the shift from a single central data team to multiple domain or embedded teams. With one team, the team *is* the catalog — everyone knows who to ask. Once ownership is distributed across teams, "who owns this and who do I escalate to?" stops being answerable by tribal knowledge, and explicit, discoverable ownership metadata becomes essential.

______________________________________________________________________

## Spotlight: OpenMetadata

[OpenMetadata](https://open-metadata.org) is a popular open-source catalog that fits a self-hosted platform stack cleanly:

- Self-hostable — ships as Docker images and a Helm chart; runs comfortably on K8s with the app, ingestion, and dependencies as separate components.
- Backed by Postgres + Elasticsearch — Postgres (or MySQL) holds the metadata; Elasticsearch (or OpenSearch) powers search and the discovery UI. Both are typically externalized to managed services in production.
- Pull-based ingestion — ingestion connectors run as scheduled workflows (standalone, or triggered from your orchestrator) that connect out to source systems on a cadence.
- Connects to the platform — native connectors for the orchestrator (Airflow, Dagster) to pull pipeline lineage and run status, dbt to ingest model docs, tests, and lineage from build artifacts, and the warehouse (Snowflake, etc.) for schemas, profiling, and usage. It stitches these into end-to-end lineage and surfaces freshness, test results, and quality metrics in one UI.

The result: a single pane of glass that collects metrics and lineage from the orchestrator, transformation layer, and warehouse, and displays them with ownership, glossary terms, and data-quality signals for the whole team.

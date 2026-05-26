# Product Event Architecture Notes

## Problem Statement

Modern product companies need to capture two fundamentally different kinds of data:

1. Business state. Who the user is, what they own, what they owe, what they consented to. The application breaks if this is wrong.
1. Behavioral events. What the user did, when, in what context. The application keeps working if this is delayed, but downstream systems (analytics, lifecycle messaging, ML, experimentation) depend on it.

The mistake most teams make is one of two extremes:

- Underbuilding. Cramming everything into Postgres tables with no event model, then bolting on third-party SDKs (GA4, Segment, Braze) directly from the frontend with no source of truth.
- Overbuilding. Standing up Kafka, schema registries, and stream processors on day one for a product that has three engineers and ten thousand users.

The goal is to match architecture to the actual coupling, throughput, and replay requirements of the system, and to evolve deliberately as those requirements change.

## Core Mental Models

Each system has a job it is good at:

- Postgres stores current truth. It is the system of record for business state.
- Kafka distributes event streams. It decouples producers from many independent consumers.
- Warehouses (Snowflake, BigQuery, Redshift) store historical analytical records for querying.
- Braze (or similar) consumes behavioral and lifecycle data to drive customer messaging.
- GA4 handles web traffic analytics and marketing attribution.

A useful split:

```text
Postgres:
  users
  orders
  subscriptions
  cart_items
  payments

Kafka:
  checkout_started
  product_viewed
  feature_used
  purchase_completed

Warehouse:
  fct_orders
  fct_events
  dim_users

GA4:
  page views
  traffic sources
  campaign attribution
  landing page analytics
```

The principle: business state lives in Postgres, behavioral events flow through a pipeline, and analytical and activation systems are downstream consumers of that pipeline rather than primary writers.

## What Belongs in Postgres

Postgres holds state the application depends on for correctness. The test is simple: if this data is lost or stale, does the application produce wrong answers or behave incorrectly?

Examples:

- Users and accounts.
- Orders and payments.
- Subscription status and entitlements.
- Shopping carts.
- Email consent and notification preferences.
- Billing records.
- Authentication and authorization state.

These are mutable, transactional, and require strong consistency. They should never be stored exclusively in Kafka or a warehouse.

## What Belongs in Kafka

Kafka is appropriate for behavioral and operational events that multiple downstream systems need to consume independently. Events are immutable facts about something that happened, not mutable state.

Examples:

- product_viewed
- add_to_cart
- checkout_started
- feature_used
- recommendation_clicked
- article_viewed
- search_performed
- purchase_completed

Kafka shines when the same event needs to fan out to many consumers:

```text
Kafka topic: purchase_completed
    |
    +--> warehouse ingestion
    +--> Braze sync
    +--> recommendation training
    +--> experimentation platform
    +--> backend workflows (fulfillment, fraud, etc.)
```

Reach for Kafka when one or more of the following becomes true:

- Multiple teams need real-time consumers of the same events.
- Event replay and backfill are first-class requirements.
- Event volume is high enough to compete with OLTP workloads in Postgres.
- Polling Postgres for new events is becoming operationally painful.
- Stream processing or low-latency reactions are important.
- Producers and consumers need to be decoupled organizationally and operationally.

If none of those are true, Kafka is premature.

## What GA4 Should Handle

GA4 is a reporting and marketing analytics platform. It is not an operational event backbone, and it should not be the canonical source for business-critical event data.

Good GA4 use cases:

- Traffic source attribution.
- Landing page analysis.
- Marketing campaign reporting.
- Funnel analytics for top-of-funnel web behavior.
- Session and engagement reporting.
- Google Ads integration.

Bad GA4 use cases:

- Customer lifecycle messaging.
- Real-time personalization.
- Business-critical event pipelines.
- Source of truth for product analytics.

The reasons are practical: GA4 sampling, retention limits, schema rigidity, and export latency all make it a poor primary system. It is also a black box compared to data you own and control.

The stronger pattern treats GA4 as a downstream consumer:

```text
Application events
    |
    +--> Kafka / owned event pipeline
            |
            +--> warehouse
            +--> Braze
            +--> GA4
```

This keeps GA4 useful for what it is good at while preventing it from becoming load-bearing.

## Stage 1: Start with Postgres

Most companies should not begin with Kafka. Postgres is sufficient for early-stage behavioral event capture, and it keeps the operational footprint small.

A simple architecture:

```text
Frontend/backend
    |
    +--> Postgres transactional tables
    +--> behavioral_events table
    |
Batch jobs (cron, Airflow, Dagster)
    +--> warehouse
    +--> Braze
```

A single append-only event table is often enough:

```sql
create table behavioral_events (
    event_id uuid primary key,
    user_id bigint,
    anonymous_id text,
    session_id text,
    event_name text not null,
    occurred_at timestamptz not null,
    source text not null,
    properties jsonb not null,
    created_at timestamptz not null default now()
);

create index on behavioral_events (occurred_at);
create index on behavioral_events (user_id, occurred_at);
create index on behavioral_events (event_name, occurred_at);
```

This is enough to power:

- Product analytics.
- Lifecycle messaging via batch sync to Braze.
- Warehouse ingestion via incremental loads on `created_at`.
- Basic personalization.
- Behavioral tracking and cohort analysis.

A few rules that pay off later:

- Prefer one generic event model with flexible JSON `properties` over dozens of narrow per-event tables. Schemas evolve; a single table with a versioned event contract scales better.
- Partition by month or week once volume justifies it. Postgres handles append-only workloads well with declarative partitioning.
- Index for the access patterns you actually have, not the ones you imagine.
- Treat the table as append-only. No updates, no deletes outside of retention jobs.

## Stage 2: Batch Sync to Downstream Systems

Once events are landing in Postgres, the next step is getting them where they need to go. At this stage, batch is almost always sufficient.

```text
behavioral_events (Postgres)
    |
    +--> incremental load --> warehouse (every 15 min to 1 hr)
    +--> batch sync       --> Braze (hourly or daily)
    +--> batch export     --> GA4 Measurement Protocol (if needed)
```

Reasons batch is fine here:

- Lifecycle messaging tolerates minutes-to-hours of latency.
- Warehouse models almost always run on schedules, not in real time.
- Batch is dramatically easier to operate, monitor, and backfill than streaming.

The signal that batch is no longer enough is usually not volume. It is latency requirements from a specific downstream use case (real-time personalization, fraud detection, in-session messaging).

## Stage 3: The Outbox Pattern

Before reaching for Kafka, there is an intermediate step that solves the most common correctness problem: how do you reliably publish an event when a business write happens?

The naive approach:

```text
1. Write order to Postgres.
2. Publish Kafka event (or call Braze API).
```

This is broken. If step 1 succeeds and step 2 fails, the system is silently inconsistent. If step 2 succeeds and step 1 fails (or rolls back), downstream systems see events for things that did not happen.

The outbox pattern fixes this by making the event publication intent durable in the same transaction as the business write:

```sql
begin;

insert into orders (...);

insert into outbox_events (
    event_id,
    event_name,
    payload,
    created_at
)
values (...);

commit;
```

A separate async publisher reads from `outbox_events` and forwards to the destination (Kafka, Braze, an HTTP endpoint, etc.):

```text
outbox publisher
    |
    +--> Kafka topic / Braze / warehouse
```

The guarantee is straightforward: if the business transaction commits, the event intent is durable. If it rolls back, no event exists to publish. The application never has to coordinate distributed transactions between Postgres and an external system.

This pattern is valuable even without Kafka. An outbox table plus a worker that calls Braze or pushes to a warehouse is enough to get exactly-once-ish delivery semantics with retries.

## Stage 4: Kafka as the Event Backbone

Kafka becomes the right answer when the system has outgrown what Postgres-as-event-store can do operationally. The transition is rarely driven by raw row counts. Postgres can comfortably handle hundreds of millions of append-only rows with partitioning.

The real warning signs are:

- Many independent consumers polling Postgres and creating contention.
- Latency requirements dropping below what batch can deliver.
- Replay and backfill becoming routine operational needs.
- Event write volume competing with OLTP workloads for IO and connections.
- Operational coupling between teams who need to consume the same events.
- A genuine need for stream processing (windowed aggregations, joins, real-time enrichment).

At this stage the architecture looks like:

```text
Transactional systems
    -> Postgres
    -> outbox / River jobs
    -> Kafka

Kafka
    -> warehouse ingestion
    -> Braze sync
    -> ML and recommendations
    -> operational consumers (fulfillment, fraud, etc.)
    -> GA4 via export worker
```

The Postgres outbox does not go away. It remains the durable handoff between the transactional system and Kafka. This is what keeps producer-side delivery reliable without distributed transactions.

## Evolution Summary

A common progression:

```text
Stage 1:
  Postgres + behavioral_events table
  Direct writes from application code

Stage 2:
  Batch exports to warehouse and Braze
  Cron or orchestrator-driven syncs

Stage 3:
  Outbox pattern + async publishers (River, custom worker)
  Reliable event publication without distributed transactions

Stage 4:
  Kafka as the primary event backbone
  Multiple independent consumers, replay, stream processing
```

Each stage is a response to a real operational pressure, not a checkbox. Skipping ahead adds complexity that is hard to justify; staying behind too long produces reliability problems that are hard to debug.

## Recommended Long-Term Architecture

The endpoint most product companies converge on:

```text
Business state
    -> Postgres

Behavioral events
    -> Postgres outbox
    -> Kafka

Historical analytics
    -> warehouse / lake (consumed from Kafka)

Marketing activation
    -> Braze (consumed from Kafka)

Web analytics
    -> GA4 (consumed from Kafka or tagged separately on the client)
```

The properties this gives you:

- Postgres remains the clean transactional model.
- Kafka is the integration surface for everything that wants to react to events.
- Downstream systems are interchangeable. Swapping Braze for a different messaging platform, or adding a new ML consumer, does not require producer changes.
- Replay is possible. New consumers can rebuild state from history.
- GA4 stays in its lane as a reporting tool, not a load-bearing pipeline.

The hybrid model also degrades gracefully. If Kafka has an outage, the outbox accumulates and drains when Kafka recovers. If a downstream consumer fails, it can rewind to a known offset. The transactional system keeps working throughout.

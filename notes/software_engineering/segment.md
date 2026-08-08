# Segment CDP

Segment is a Customer Data Platform (CDP): a shared layer for collecting customer data, standardizing it, resolving identity, and activating it downstream. Its core promise is "collect once, send everywhere." Applications, services, SaaS tools, and the warehouse contribute data; analytics, marketing, advertising, and support tools consume it without every pair of systems needing a custom integration.

## When to use Segment

Use Segment when multiple sources describe the same customers and several downstream tools need consistent identities, traits, events, or Audiences. It is especially useful when growth teams need to change targeting without engineering building a separate pipeline for every destination.

**Good use case:** A company sends real-time product and purchase events from its web app and Go backend, syncs daily customer tiers and order-total ranges for 10,000 users from Snowflake, and uses the combined Segment Profiles to define Audiences for lifecycle messaging, advertising, CRM, and product personalization. Segment centralizes identity and instrumentation while Engage manages who enters or leaves each cohort.

**Bad use case:** A company has one daily warehouse table that needs to update one CRM, has no client or server event stream, and does not need identity resolution, self-service Audiences, or Journeys. A direct warehouse integration or simple scheduled job is likely cheaper and easier than operating and licensing a CDP.

## What a CDP enables

- **Consistent customer data:** Teams and tools share identifiers, event schemas, and profile traits.
- **Faster activation:** New destinations reuse existing instrumentation instead of requiring another application release or pipeline.
- **Unified audiences and personalization:** Behavioral events and warehouse traits support lifecycle messages, advertising, product experiences, and customer support.
- **A warehouse-to-operations loop:** Models such as churn risk or lifetime-value ranges become usable in operational tools.
- **Governance:** Tracking plans, filters, and transformations control data quality and which vendors receive sensitive data.

A CDP is most valuable when several destinations need the same customer data or identity must remain consistent across web, mobile, backend, and warehouse activity. It is less compelling for a simple product with one destination or when usage-based pricing exceeds the value of centralized activation.

## Segment terminology

Segment Profiles, Unify, and Engage are related but not interchangeable:

```text
Sources and warehouse
        |
        v
      Unify
identity resolution + Segment Profiles
        |
        v
      Engage
audiences + journeys + activation
        |
        v
   Destinations
```

- **Segment Profile** is the unified customer record containing identifiers, traits, and event history. Segment formerly called the Unify product "Profiles," but this document uses Segment Profile only for the record itself.
- **Unify** is the identity layer. It merges activity across sources, maintains the identity graph, and exposes Profile Explorer and Profile API.
- **Track** records that something happened at a point in time, such as `Order Completed`, `Product Viewed`, or `Subscription Cancelled`. Its properties describe that occurrence; every occurrence is a separate event and API call.
- **Identify** records what is currently true about a known user, such as `plan`, `customer_tier`, or `is_email_subscribed`. It creates or updates traits on the Segment Profile and should be sent when relevant user state changes.
- **Engage** lets your team define Audiences—cohorts of people you want to target—and connect them to Segment-supported destinations. As profile traits and Track events change, Engage reevaluates affected Segment Profiles, moves people into or out of each Audience, and sends those membership changes downstream. Evaluation may be real-time or scheduled, and warehouse traits are only as fresh as their Reverse ETL sync. Engage sends configured membership and selected traits, not every field from the Segment Profile. Engage requires Connections and Unify. Two optional capabilities become useful when client or server SDKs also send real-time behavioral events:
  - **Computed traits** derive values such as `products_viewed_last_7_days` or `orders_completed_last_30_days` from those events. Audiences can combine these fast-changing values with daily warehouse traits such as `order_total_range` or `customer_tier`.
  - **Journeys** run multi-step flows based on profile state and events, such as waiting two hours after `Product Viewed`, exiting if `Order Completed` arrives, and otherwise sending a reminder or adding the user to an advertising Audience.
- **Audience** is a cohort of users or accounts that matches rules you define, such as `order_total_range = '2500-4999' and is_email_subscribed = true`. When membership changes, a list destination might add or remove the user, while an event destination might receive a boolean trait or `Audience Entered`/`Audience Exited` event.
- **Segment Profiles destination** is the Reverse ETL destination that writes warehouse traits and events into a Unify space, creating or updating Segment Profiles.
- **Profiles Sync** moves Segment Profiles back into the warehouse. This is the opposite direction from the Segment Profiles destination.

References: [Unify](https://www.twilio.com/docs/segment/unify), [Engage](https://www.twilio.com/docs/segment/engage/quickstart), [Segment Profiles destination](https://www.twilio.com/docs/segment/connections/destinations/catalog/actions-segment-profiles).

## Data model and ingestion

In addition to Track and Identify, Segment provides `page` and `screen` for views and `group(groupId, traits)` for accounts.

There are three common ways to send data into Segment:

1. **Client SDKs:** Capture web or mobile interactions and anonymous pre-signup behavior. They provide device context but can be affected by ad blockers.
1. **Server SDKs or HTTP Tracking API:** Send authoritative backend events such as completed orders or subscription changes. This is reliable and can include server-derived properties.
1. **Warehouse or managed sources:** Reverse ETL publishes modeled traits and audiences from the warehouse; managed sources import supported CRM, billing, or support data.

Use one stable identity contract across every path. Warehouse `user_id` must exactly match application `userId`; casing, prefixes, or number-versus-string differences create parallel profiles and incomplete audiences.

## Use case: 10,000 profiles refreshed daily

The goal is to refresh approximately 10,000 consented Segment Profiles from Snowflake and activate them in three growth platforms. The warehouse remains authoritative for exact values and business logic; Segment Profiles become the identity-resolved source of truth for activation.

### Reverse ETL model

Keep exact metrics in the warehouse, but select stable ranges in the activation model:

```sql
with profile_traits as (
    select
        user_id,
        lower(trim(email)) as email,
        tier,
        case
            when order_total is null then null
            when order_total < 2500 then '0-2499'
            when order_total >= 2500 and order_total < 5000 then '2500-4999'
            when order_total >= 5000 then '5000+'
        end as order_total_range,
        engagement_score_bucket,
        is_email_subscribed
    from analytics.marts.user_profile_enriched
)

select
    user_id,
    email,
    tier,
    order_total_range,
    engagement_score_bucket,
    is_email_subscribed
from profile_traits
where
    is_email_subscribed = true
    and email is not null
```

Use `user_id`, not email, as the unique identifier because email can change. Filter consent in the model so ineligible users never leave the warehouse.

Reverse ETL compares checksums of the selected columns. Because exact `order_total` is omitted, a customer's total can change within a range without triggering delivery; the row syncs only when the range or another selected trait changes. The query still evaluates all 10,000 rows on schedule.

Avoid run-stamped columns such as `updated_at`, `dbt_updated_at`, and `_loaded_at`, which make every row appear changed. Also omit or bucket volatile rolling metrics unless downstream tools truly need them.

### Recommended architecture: Segment Profiles and Engage

```text
Snowflake -> Reverse ETL -> Segment Profiles destination
          -> Segment Profiles -> Engage -> three destinations
```

This is the cleanest default when the organization licenses Unify/Engage and the destinations support the required Engage actions. The warehouse sync runs once, identity is resolved once, and growth teams build and fan out audiences from a shared activation layer.

Use direct Reverse ETL when Unify/Engage costs more than the duplicated mappings, only one or two stable destinations need the data, or a destination requires specialized deletion, consent, PII, or payload handling:

```text
Snowflake -> Reverse ETL -> Platform A
                         -> Platform B
                         -> Platform C
```

Each destination gets independent mappings and failure isolation, but each mapping has separate state, query execution, and Reverse ETL usage.

Segment Connections is a compatibility fallback when a destination is missing from the Reverse ETL catalog and Engage is not the activation layer:

```text
Snowflake -> Reverse ETL -> Segment Connections
          -> HTTP API source -> event-stream destinations
```

It also uses one warehouse mapping, but sends calls through the Tracking API, adding API usage and potentially MTUs.

## Cost model

Segment does not publish fixed Unify and Engage prices, so the final decision requires the organization's quote and included usage.

- **Reverse ETL:** Records are counted per destination. One changed row sent directly to three platforms counts three times; one Segment Profiles mapping counts it once. Extraction does not add MTUs.
- **Segment Profiles:** The Segment Profiles destination does not add API-call or MTU usage, but requires an active Unify space. Engage licensing is additional and quote-based.
- **Connections:** Each call through the Segment Connections destination adds API usage, and previously unseen users can add MTUs.
- **Call volume versus payload width:** One Identify call containing 10, 20, or more traits is still one API call, subject to payload and product limits. Sending 10 traits in 10 separate Identify calls counts as 10 calls. Likewise, 100 Track events count as 100 calls and 200 count as 200; batching improves transport efficiency but does not reduce billable throughput.
- **MTUs and throughput:** A known `userId` is counted once per month for MTU purposes even if that user produces many events. Some plans also cap total API calls and objects per purchased MTU, so high Track volume can increase usage without increasing MTUs.
- **Engage:** Compute credits can apply to audiences, computed traits, and Journey steps. Credits are based on definitions and steps, not audience membership; 10,000 audience members do not consume 10,000 credits.
- **Warehouse and downstream tools:** Direct mappings repeat warehouse work, while ad, CRM, and messaging vendors may impose their own charges under any topology.

Approximate Reverse ETL record counts for a 30-day month:

| Scenario | Direct to three destinations | Segment Profiles or Connections |
| ------------------------------------ | ---------------------------: | ------------------------------: |
| Initial 10,000-profile load | 30,000 | 10,000 |
| All profiles change daily | 900,000 | 300,000 |
| Initial load, then 500 daily changes | 73,500 | 24,500 |

Segment Profiles and Connections have the same Reverse ETL count because each uses one warehouse mapping, but Connections adds API calls and potentially MTUs. Segment Profiles avoids those charges but requires Unify/Engage. Direct delivery avoids that license but multiplies Reverse ETL usage and configuration by the number of destinations.

References: [Reverse ETL usage and diffing](https://www.twilio.com/docs/segment/connections/reverse-etl/system), [MTUs and compute credits](https://www.twilio.com/docs/segment/guides/usage-and-billing/mtus-and-throughput), [Segment pricing](https://segment.com/pricing/).

## Operational checklist

- Trigger the mapping after the daily warehouse model completes. Use one trigger for Segment Profiles or a shared trigger for all direct mappings.
- Confirm destination support and destination-specific hashing, deletion, and null behavior.
- Test approximately 100 profiles in staging and verify known `userId` values in Profile Explorer.
- Alert on failed and zero-record syncs.
- Review the Unify/Engage quote, included Reverse ETL records, MTU and API allowances, and compute credits before choosing the topology.

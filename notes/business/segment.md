# Segment

Segment (owned by Twilio since 2020) is a Customer Data Platform — essentially a centralized layer that collects user and event data from your own products, normalizes it into a consistent schema, and routes it to any number of downstream tools. The core promise is "collect once, send everywhere." Instead of every marketing tool, analytics platform, and data warehouse having its own tracking snippet or integration, Segment sits in the middle and acts as the single source of truth for behavioral and identity data.

The key abstraction is the workspace, where you define sources (where data comes from) and destinations (where data goes). The pipeline between them is managed by Segment.

## Core Data Model

Segment is built around a small set of standardized method calls, which is a large part of its value. Rather than inventing your own event schema for every tool, everything maps to:

- `identify(userId, traits)` — associates a user with properties like name, email, plan, company
- `track(event, properties)` — records a discrete action: "Order Completed", "Button Clicked", "Video Started"
- `page(name, properties)` — records a page view with contextual metadata
- `group(groupId, traits)` — associates a user with an account or organization (important for B2B)
- `screen(name)` — mobile equivalent of `page`

Because every source speaks this same language, all downstream destinations receive data in a consistent, predictable format. This normalization is the core unlock.

---

## Getting Data Into Segment

There are several ingestion paths depending on where your data originates:

Client-side SDKs are the most common starting point. You drop `analytics.js` into a web app, call `analytics.track("Signed Up", { plan: "pro" })`, and Segment handles batching and sending. Mobile SDKs work the same way for iOS and Android.

Server-side SDKs (Go, Python, Node, Ruby, Java, etc.) are used when you need more control — for events that happen in your backend where a browser isn't present, or when you want to avoid ad blockers, or when you need to attach server-side data (pricing, internal flags, feature access) that shouldn't be computed client-side.

HTTP Tracking API is the raw endpoint underlying all the SDKs. Anything that can make an HTTP POST can send data to Segment, which makes it useful for edge cases and custom pipelines.

Cloud sources (Salesforce, Stripe, Zendesk, Marketo) are first-party integrations where Segment polls those APIs on a schedule and pulls data in — no custom ETL work needed. This is useful for enriching behavioral data with CRM or billing context.

Reverse ETL (via Segment's Reverse ETL feature, or tools like Census/Hightouch that integrate with it) reads computed data from your warehouse and syncs it back into operational tools — think pushing a "predicted churn score" from Snowflake into your CRM.

---

## Getting Data to Destinations

Once data is in Segment, routing is handled through connections in the UI or via the Config API. Each destination has a Segment-managed integration that handles the translation — for example, Segment knows that a `track("Order Completed")` call needs to become a Facebook Conversions API event with specific field mappings.

There are two delivery modes:

Cloud-mode (server-side delivery) sends the data from Segment's servers to the destination's API. This is more reliable, not affected by ad blockers, and keeps logic out of the browser bundle.

Device-mode (client-side delivery) loads the destination's native SDK into the browser and calls it directly. Some tools require this to use their full feature set (e.g., certain attribution or session replay vendors need DOM access).

Destination filters and functions let you control what gets routed where. You can drop events, transform payloads, rename properties, or block certain users from reaching specific tools. Segment Functions are lightweight JavaScript lambdas that let you write custom transformation logic in-platform without deploying anything.

Protocols (Segment's data governance layer) lets you define a tracking plan — a schema of what events and properties are allowed — and will block or flag events that don't conform. This is critical for data quality at scale.

---

## Business Use Cases

The practical value tends to flow across a few common patterns:

For product and growth teams: Segment feeds tools like Amplitude, Mixpanel, or Heap without each team needing an engineering ticket for a new integration. Product managers can enable a new analytics tool in the Segment UI and immediately receive clean, historical event data. Same for A/B testing platforms like Optimizely or LaunchDarkly — they get the same user identity and event stream without duplicating instrumentation.

For marketing and lifecycle teams: Behavioral events (signed up, completed onboarding, hit usage limit) flow into Braze, Customer.io, or Iterable to trigger personalized messaging. Segment's identity resolution stitches together anonymous pre-signup activity with post-signup user records, so marketing can see the full funnel rather than only post-auth behavior.

For advertising and attribution: The same events feed ad platforms via server-side pixel alternatives, improving match rates and bypassing browser restrictions. Conversion events sent server-side to Google or Meta tend to perform better than browser pixels alone.

For the data warehouse: A Snowflake or BigQuery destination receives every event as structured tables — `tracks`, `identifies`, `pages` — plus one table per event type with flattened properties. This is often the primary way data teams get clean product usage data into their warehouse without building custom ETL.

For customer success and support: User traits and behavioral context flow into Intercom or Zendesk so support reps see what a user has done recently before a conversation starts.

---

## When It's Worth It

Segment starts making sense when at least a few of these are true:

You're instrumenting once and routing to multiple tools. If you have two or more analytics/marketing tools that all need the same behavioral data, Segment pays for itself quickly in avoided integration work.

Your team is tired of every tool requiring its own snippet. The "tag soup" problem — 10 different vendor scripts in your `<head>` — is exactly what Segment solves. One script, everything else is a server-side connection.

You need consistent identity across the funnel. Stitching anonymous visitors to logged-in users, across web and mobile, with a reliable `userId` / `anonymousId` linkage, is non-trivial to build yourself.

You're building toward a real data infrastructure. The warehouse destination is one of the most valuable parts — if you're planning to do analytics in Snowflake or BigQuery, Segment's schema-managed event tables are a clean foundation.

You have data governance concerns. Protocols and destination filters let you enforce schemas and control data flows in a way that's hard to replicate with ad-hoc integrations.

When it's probably not worth it: If you have one analytics tool, a simple single-platform product, and no near-term plans to add more vendor integrations, Segment adds complexity without much payoff. Similarly, if you have very high event volumes and sensitive cost constraints, the per-MTU pricing model can get expensive at scale — at that point, some teams roll their own lightweight event pipeline into Kafka or directly into their warehouse.

# CDP and Downstream Activation Syncs

A customer data platform (CDP) collects and unifies customer data so teams can build audiences and activate them in marketing, advertising, analytics, sales, and support tools. In a warehouse-centric architecture, a reverse ETL job often publishes modeled customer attributes from the warehouse to a CDP or directly to one of those downstream systems.

```text
Operational systems -> warehouse -> modeled profile attributes --+
Applications and services -> behavioral events -------------------+-> CDP -> audiences -> activation destinations
```

Individual vendors differ in identity rules, schema enforcement, consent handling, API semantics, and billing. This document captures the recurring design principles, but every integration should verify the platform-specific behavior listed in the final checklist.

## 1. The shared mental model

Most customer-data and activation platforms expose some version of the same three concepts:

| Concept | Common names | What it really is |
| ------------ | --------------------------------- | ---------------------------------------------------------------------------- |
| **Profile** | user, contact, subscriber, person | A mutable record representing the current known state of a person or account |
| **Event** | event, track call, activity | An append-only, timestamped fact about something that happened |
| **Audience** | list, segment, cohort | A rule-derived group of profiles, evaluated live or materialized |

The goal is to make profiles and events trustworthy enough that non-technical users can build audiences without reconstructing business logic. Profiles deserve particular care because they are mutable and are commonly shared by several writers.

**Key asymmetry:** profiles are generally upserted or merged, while events are appended. A bad profile write can overwrite current state; a bad event write creates duplicate or misleading history. Model historical facts as events and current, segmentable state as profile attributes. Both paths need validation and idempotency controls.

______________________________________________________________________

## 2. Identity: choosing a primary key

This is the highest-consequence design decision. Changing identity strategy after launch is usually expensive because profiles, events, audiences, and campaign history already depend on it. Treat identity as an organization-level data contract rather than an integration detail.

### Use your internal business ID

Default to a stable, opaque, internal identifier. The reasons are structural:

- **Emails change.** Users change jobs, consolidate accounts, fix typos. A key that mutates is not a key.
- **Emails are shared.** Households, B2B seats, shared inboxes, and QA aliases all collapse distinct people into one record.
- **Emails are PII.** Using them as join keys increases the chance that PII appears in logs, URLs, metrics, and error messages.
- **Emails are absent.** Anonymous, phone-only, and app-only users have no email. If email is your key, you're forced into placeholder-email schemes that pollute your data and inflate your billable profile count.

### Understand the uniqueness tradeoff

When internal ID is the primary key, a platform may allow multiple profiles to share an email address. If the delivery system does not deduplicate recipients, one campaign can send multiple messages to the same inbox. Verify the vendor's uniqueness and send-time deduplication behavior explicitly.

Possible mitigations include:

- Designate a primary profile per email in your warehouse and expose it as a boolean field.
- Make audience-building on that flag a documented default, or bake it into templates stakeholders start from.
- Monitor duplicate-email counts as a first-class metric, not something you check after a complaint.

### ID hygiene rules

- **Never encode PII in the ID.** Many platforms explicitly prohibit it, and it defeats the point.
- **Watch length limits.** Identifier fields are often capped surprisingly low. Verify before you commit to a UUID-plus-prefix scheme.
- **Use one identity contract everywhere.** If a server-side sync identifies a user by internal ID while a mobile SDK identifies the same user by email, the platform may create two profiles. Audit every writer and define the role of primary IDs, aliases, and anonymous IDs before launch.
- **Anonymous-to-known merging needs an explicit design.** Decide how pre-login activity becomes associated with a known profile, which system performs the merge, and what happens when identities conflict. Do not assume every vendor handles this transition the same way.

______________________________________________________________________

## 3. Email as an attribute, not an identifier

Once the primary key is internal, email becomes a mutable attribute, but one with platform-specific behavior:

- **It's a system field.** These platforms reserve a set of field names with special behavior (the address messages actually go to, the phone number SMS dials, locale, timezone, country, consent state). The exact spelling is load-bearing; a near-miss creates a useless custom field that silently does nothing.
- **Never invent your own versions of system fields.** If the platform has a canonical concept, map to it. A parallel `emailAddress` next to the real one guarantees someone builds a campaign on the wrong one.
- **Consent and deliverability need explicit ownership.** Bounces and vendor suppressions are normally created downstream; legal consent may originate in a consent service, warehouse, or the activation platform. Define the authority for each field and never let a generic profile sync overwrite downstream opt-outs or suppression state.
- **Changing the email on an existing profile may be a distinct operation** from a normal attribute update, with its own endpoint and failure modes. Verify this before treating email as an ordinary field.

**Useful default:** the warehouse publishes modeled facts about the customer, while activation platforms publish engagement, delivery, and suppression facts back. Consent ownership must be decided separately because it depends on the organization's architecture and legal requirements.

______________________________________________________________________

## 4. Treat the destination schema as a contract

Schema behavior varies. Some platforms infer a field's type from its first non-null value, some require fields to be declared, and others coerce or reject mismatched values. A conservative integration assumes type changes are unsafe and validates every payload before sending it.

Practices that survive this:

- **Declare the schema in code.** An explicit column-to-type mapping that you cast against before serializing. Anything not in the map never leaves your warehouse.
- **Seed carefully.** A first write may establish destination types. Push a small, hand-verified batch and inspect stored profiles before sending the full population.
- **Beware type drift from nulls.** Warehouse connectors and dataframe libraries can infer an all-null integer column as a float, string, or untyped value. Cast explicitly on every run.
- **Field names are permanent in practice.** Renaming creates a new field and orphans the old one, along with every segment and campaign referencing it. Choose names as though you can't change them, because effectively you can't.
- **Check field-count limits.** Do not sync the entire warehouse "just in case". Every field consumes governance attention and may consume a limited schema slot.
- **Datetimes need a documented format and timezone.** Prefer UTC RFC 3339 timestamps unless the platform specifies otherwise. A malformed date may be rejected, dropped, or stored as an opaque string that cannot support date-based segmentation.

______________________________________________________________________

## 5. Row-level change detection

For large or frequently refreshed datasets, full syncs consume rate-limit capacity and may increase metered cost. Some platforms also reevaluate audiences or automations after profile writes. Use delta syncs when the destination or connector does not already provide reliable change detection.

### The basic mechanism

1. Materialize the exact payload you intend to send, post-transformation.
1. Canonically serialize it and hash the result with a stable algorithm.
1. Compare against the previous run's hashes, stored in your own state table.
1. Send only new or changed rows.
1. Update state only for records the destination accepted. If the API cannot identify per-record outcomes, checkpoint only after the entire batch or run succeeds.

### Non-obvious requirements

- **Hash the output, not the input.** Hashing warehouse columns before transformation misses the case where your mapping logic changes but source data doesn't.
- **Version the state.** A change to field mappings, transformation logic, canonical serialization, or schema may invalidate prior hashes. Store a payload version with the state rather than relying on a table-name suffix alone.
- **Handle disappearing rows explicitly.** A profile that falls out of the source query is not necessarily deleted; it may be ineligible, churned, suppressed, or outside a rolling window. Anti-join current rows against prior state and apply an explicit lifecycle policy. Do not infer deletion from absence unless the source contract guarantees it.
- **State must be durable and versioned.** If your state store is lost, the next run is a full sync. Make sure that's survivable rather than an outage.

______________________________________________________________________

## 6. Distinguishing meaningful change from noise

Delta sync alone may still produce excessive writes when aggregate fields change more often than the downstream use case requires. For example, lifetime value may change after every purchase while a lifecycle campaign only needs to know whether a customer crossed a value tier.

### Bucket continuous values

When consumers do not need exact values, replace or supplement raw magnitudes with named tiers. This helps in two ways:

1. **Volume:** collapses continuous churn into rare threshold crossings.
1. **Usability:** centrally defined tiers prevent several teams from implementing conflicting definitions of terms such as "high value."

Guidance:

- **Make labels sort correctly.** Zero-padded ordinal prefixes so dropdowns and exports are readable.
- **Consider a numeric twin.** A parallel integer rank can simplify range comparisons when the destination does not preserve a custom tier order.
- **Treat boundaries as a versioned contract.** Changing them can re-tier a large fraction of the population and fire threshold-crossing automations. For material changes, publish a new field version and migrate consumers deliberately.

### Consider hysteresis at noisy boundaries

A user whose value repeatedly crosses a threshold can oscillate between tiers, creating writes and potentially retriggering automation.

For sufficiently noisy metrics, implement a deadband: retain the current tier until the value clears the boundary by a defined margin. This makes tier assignment stateful, so preserve the previous tier in durable state and document the promotion and demotion rules. Do not add hysteresis where stakeholders expect exact threshold semantics.

### Exclude high-churn fields from the change signal

Some fields should be *synced* but should never be the *reason* for a sync. Raw aggregates, computed scores, and "last updated" timestamps fall here.

If slight staleness is acceptable, exclude these fields from the change hash. They can ride along when a meaningful field changes and be corrected during controlled reconciliation. This reduces write volume, but it also creates a deliberate freshness lag that must appear in the field contract.

### Prefer timestamps over recency buckets

Time-since-last-X buckets can change for a large slice of the population merely because the clock advanced, recreating the write churn that bucketing was intended to avoid.

Prefer syncing the raw timestamp and using the platform's relative-date operators. A derived bucket is appropriate only when the platform cannot express the required rule and the resulting daily writes are understood.

### Separate cadences by volatility

Not every field needs the same freshness. Identity changes may need near-real-time delivery, behavioral tiers may be daily, and demographic or firmographic attributes may be weekly. Consent and suppression updates should follow the latency promised by the organization's compliance policy. Separate jobs only when the operational benefit outweighs the added ownership and ordering complexity.

______________________________________________________________________

## 7. Keeping systems in sync over time

Delta sync compares the source with the integration's last known state; it does not prove that the destination still matches. Drift is possible whenever another writer or the platform itself can mutate a profile.

### Sources of drift

- **UI edits.** Someone fixes a profile by hand. Your state says "in sync"; it isn't.
- **Other writers.** Mobile SDKs, web SDKs, support tooling, other integrations, the platform's own enrichment.
- **Platform-side mutation.** Deliverability state, engagement scores, list membership — the platform generates these and you must not clobber them.
- **Silent drops.** Type mismatches and unrecognized fields that returned success and did nothing.

### Reconciliation

Run periodic reconciliation regardless of change detection. Prefer reading destination state and repairing differences when the platform supports efficient exports or reads. Otherwise, use a controlled full republish, often sharded by a hash of the profile ID so the integration repairs one slice per run without a load spike. Choose the reconciliation window from the acceptable drift, cost, and risk of retriggering downstream behavior.

Additionally, **verify rather than assume**. Sample profiles after each run and compare them with the expected destination-owned fields. Depending on the API, a success response may acknowledge receipt before asynchronous processing or omit individual validation failures. Read-after-write checks, exports, or vendor delivery logs provide stronger evidence.

### Ordering and timing

- **Check ordering guarantees.** Some platforms process writes asynchronously or require a delay between dependent operations on the same profile. A profile update followed immediately by a membership change may execute out of order.
- **Concurrent writers race.** Two systems updating the same profile within the same window produce nondeterministic results with no error. Serialize per-profile if you can; if you can't, make sure only one writer owns each field.
- **Establish field ownership explicitly.** Every field should have exactly one authoritative writer, documented. Shared ownership is the root cause of most "the data keeps reverting" tickets.

### Bulk write ergonomics

- Bulk endpoints cap at some batch size and often a payload byte size simultaneously — you can hit the byte cap well under the record cap with wide profiles.
- **Partial-failure reporting varies.** Preserve request or batch identifiers, log sanitized response details, and reconcile counts sent, accepted, rejected, and eventually processed. Never log raw sensitive payloads merely to aid debugging.
- **Verify rate-limit scope.** Limits may be shared across a workspace, account, endpoint, or credential, so one sync may compete with other integrations and SDKs.
- **Retry only documented transient failures** with bounded exponential backoff and jitter, honoring `Retry-After`. These commonly include 429 and some 5xx responses; timeout and conflict behavior is vendor-specific. Send permanent validation failures to a dead-letter or quarantine path instead of retrying forever.
- **Design for idempotency.** Profile upserts are often replay-safe when merge and null semantics are understood. Events need a stable event ID or destination-supported idempotency key so retries do not create duplicates.

______________________________________________________________________

## 8. Deletion, privacy, and suppression

- **Deletion may be irreversible and cascading.** Determine whether deleting a profile also removes event history, audience membership, exports, and backups. Guard destructive endpoints and test against non-production profiles first.
- **Privacy requests need a dedicated code path** that runs independently of your normal sync, with its own audit log. It must be able to run when the main pipeline is broken.
- **Suppression must survive resync.** A full profile refresh must not re-enable a person who opted out. Test this scenario deliberately and fail closed when consent state is unknown.
- **A deleted user in your warehouse is not automatically deleted downstream.** Deletion propagation is a thing you build, not a thing you get.

______________________________________________________________________

## 9. Making it useful to stakeholders

Syncing data is necessary and not sufficient. The integration is only successful when non-technical people can self-serve.

- **Fields may be invisible until populated.** If the destination discovers schema from data, a field with no values may not appear in the segment builder. Use a documented schema-registration mechanism when available; otherwise seed representative test profiles rather than inventing misleading production defaults.
- **Publish a field dictionary.** Platform field name, business meaning, refresh cadence, nullability, and owner. Freshness especially — someone building on a field needs to know it's 24 hours stale, not live.
- **Ship business-friendly attributes.** Tiers and categories are easier to use consistently than raw metrics, but retain raw values when downstream users genuinely need flexible thresholds or personalization.
- **Instrument tier transitions.** Counts of movements between tiers per run are both a useful data-quality alarm—a broken upstream aggregate can appear as a mass migration—and a useful stakeholder report.
- **Separate the profile sync from downstream actions.** Audience membership, event tracking, and campaign triggering should be distinct jobs. A bug in list-building shouldn't be able to take down profile freshness.

______________________________________________________________________

## 10. Smell test

Signs an integration is heading for trouble:

- No one can name the primary key without checking.
- More than one system writes the same field.
- The pipeline syncs every row every run without a scale, correctness, or reconciliation reason.
- Volatile fields are synced at a higher cadence or precision than the use case requires.
- Success responses are treated as confirmation of storage.
- No periodic reconciliation exists.
- State is checkpointed for records whose writes have not been confirmed.
- Field names were chosen casually.
- Deletion and suppression have no dedicated path.
- Stakeholders file tickets to build segments instead of building them.

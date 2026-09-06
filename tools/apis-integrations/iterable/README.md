# Iterable rETL Sync Overview

## How It Works

dbt models in the warehouse handle all transformation logic: joins, business rules, tiering, and aggregations. The output materializes as a Parquet file containing one row per user with all the fields Iterable needs for segmentation and campaigns. A Python sync script picks up that file, enforces a strict schema (type casting, datetime formatting, field renaming to Iterable's camelCase conventions), performs delta detection via content hashing, and pushes only changed rows to Iterable's `bulkUpdate` endpoint in batches of 1,000.

## Primary Key

- The identity key is either `email` or `userId`, controlled by the `id_field` parameter.
- When using `email`, the script lowercases and strips whitespace to normalize before syncing.
- When using `userId`, the payload sets `preferUserId: true` so Iterable resolves on the internal ID instead of email.
- Pick one and stay consistent. Mixing identity strategies across syncs creates duplicate profiles.

## Billing

- Iterable charges based on **unique stored profile count**, not API call volume.
- Delta detection doesn't directly reduce your bill, but it keeps you under rate limits and avoids unnecessary profile version history bloat.
- Warehouse compute cost is the bigger lever. A full-table dbt rebuild is simpler but more expensive at scale than an incremental model.

## Techniques for Reducing Sync Volume

- **Content hashing**: each row is SHA-256 hashed and compared against a state file from the last sync. Only rows whose hash changed get pushed, so a 500k-row table might produce 2k API writes.
- **Tier bucketing**: raw values like `lifetimeValue` are bucketed into labeled tiers (`03_2500_4999`). A user going from $3,247 to $3,260 stays in the same tier and produces no hash change.
- **Hash exclusions**: high-churn, low-signal fields like `lifetimeValue` and `bookingCount` are excluded from the hash entirely. The raw values still sync when something meaningful changes, but they can't trigger a sync on their own.
- **Hysteresis / deadband**: tier boundaries include a 5% buffer. A user at $4,980 has to clear $5,250 before moving up a tier, which prevents day-over-day flapping when values hover near a cutoff.
- **Null omission**: null fields are dropped from the payload rather than sent. This avoids overwriting existing Iterable data with blanks and prevents type-inference issues on first write.

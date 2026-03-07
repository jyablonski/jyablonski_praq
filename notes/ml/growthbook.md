# GrowthBook A/B Testing Notes

## Overview

GrowthBook is an open-source feature flagging and experimentation platform. Its key differentiator is that it separates assignment (SDK/feature flags) from analysis (stats engine querying your data warehouse). It doesn't require you to send event data to GrowthBook — it connects to your existing warehouse and runs analysis there.

## How Assignment Works

- A feature flag is created in the GrowthBook UI (e.g., `new-checkout-flow`) with an experiment rule attached to it.
- The experiment rule defines the traffic split (e.g., 50/50), the hashing attribute (typically `user_id`), and the variant values.
- The SDK (JS/React for frontend) evaluates the flag locally in the browser using deterministic hashing (MurmurHash3). No network call at evaluation time.
- `hash(user_id + experiment_key)` always produces the same result, so users are sticky — they always land in the same variant without needing server-side state.

## Variants

- Control (variant 0): The current/existing experience. Serves as the baseline for comparison. Also the safe fallback if the SDK fails to load.
- Treatment (variant 1+): The new experience being evaluated.
- Experiments can have more than 2 variants (e.g., testing 3 different color palettes), but 2-3 is most common.
- More variants = more traffic or time needed for statistical significance, plus multiple comparison corrections come into play.

## Frontend Integration

The SDK evaluation drives what the user sees. In React, you check the feature flag value and render the appropriate component based on which variant the user was assigned to. The user has no idea they're in an experiment.

When the SDK buckets a user, it fires a tracking callback that pushes a custom event to GA4:

```javascript
gtag('event', 'experiment_viewed', {
  experiment_id: experiment.key,   // e.g., 'new-checkout-flow'
  variation_id: result.variationId // e.g., 0 or 1
});
```

### Flicker

Since the SDK evaluates client-side, there can be a brief flicker before the variant renders. Options to mitigate: GrowthBook's anti-flicker snippet, loading the SDK early and blocking render, or evaluating server-side with Next.js SSR.

## Data Pipeline (GA4 → Snowflake → GrowthBook)

1. The GA4 exposure event (`experiment_viewed`) flows into GA4.
1. GA4 data lands in Snowflake via the existing GA4 connector pipeline.
1. GrowthBook queries Snowflake to run its analysis.

### What You Configure in GrowthBook

Assignment query — SQL that tells GrowthBook how to find who was in what experiment. Points at the GA4 events table in Snowflake, pulling `user_id`, `experiment_key`, `variation_id`, and `timestamp` filtered to `experiment_viewed` events.

Metric definitions — SQL-backed outcome metrics you're measuring (conversion rate, revenue per user, page views, etc.). Each metric is a query against your Snowflake tables. These can sit on top of existing dbt models (e.g., `fct_conversions`) so the experiment config stays thin and data quality logic lives in one place.

## Running an Experiment

1. Create a feature flag with an experiment rule in GrowthBook.
1. Integrate the SDK in the frontend; configure the GA4 tracking callback.
1. Make whatever frontend changes are needed to test the treatment variant(s) in the Frontend.
1. Deploy — users get bucketed, exposure events flow to GA4 → Snowflake.
1. Let the experiment run (typically 1-2 weeks depending on traffic volume).
1. GrowthBook queries Snowflake, joins assignment data against metric tables, and runs the stats engine.
1. Evaluate results — GrowthBook supports Bayesian (posterior probability, credible intervals) and Frequentist (p-values, confidence intervals) analysis.
1. Ship the winner by flipping the flag to 100%, or kill the experiment and revert.

## Other Useful Features

- Targeting and rollouts: Use flags for percentage rollouts, targeting by user attributes (plan tier, country, etc.), and kill switches.
- Namespaces: Mutual exclusion — ensure users only land in one experiment within a namespace to avoid conflicts.
- Dimensional analysis: Slice results by dimensions (country, device type) to check for heterogeneous treatment effects.
- Signed-in vs. anonymous users: Signed-in users get hashed on `user_id` (stable across devices). Anonymous users fall back to a device-level ID like GA4's `client_id`.

# Rollback Management

## Feature Flags as the First Line of Defense

Feature flags decouple deployment from release. Code ships to production behind a flag set to `off`, then the flag is flipped on for a percentage of users. If something breaks, you flip the flag off in seconds rather than executing a rollout rollback.

The hierarchy of flag types matters operationally:

- Release flags: short-lived, gate new functionality, removed within weeks of full rollout
- Ops flags: kill switches for expensive features (recommendation engines, third-party API calls) that can be disabled under load
- Permission flags: long-lived, gate features by plan or cohort
- Experiment flags: drive A/B tests, integrated with analytics

Tools like LaunchDarkly, Unleash, Flagsmith, and OpenFeature (the CNCF standard) provide SDK-level evaluation with sub-millisecond latency via local caching. Self-hosted setups commonly pair Unleash or GrowthBook with a Redis cache and a Postgres backend.

The critical discipline: flags must be observable. Every flag evaluation should emit a metric so you can correlate flag state with error rates. A flag you can't see in your dashboards is a flag you can't safely roll back.

Progressive rollout patterns layered on flags:

1. Internal users only (employees, dogfooding)
1. 1% canary
1. 5%, 25%, 50%, 100% with bake time at each step
1. Automated promotion via tools like Argo Rollouts or Flagger when SLOs hold

## Monitoring Metrics That Justify a Rollback

The decision to roll back should be driven by data, not vibes. Mature teams define SLOs upfront and treat sustained burn as the rollback trigger.

The four golden signals (Google SRE) remain the baseline:

- Latency: p50, p95, p99 across critical endpoints
- Traffic: requests per second, broken down by route and tenant
- Errors: 5xx rate, application-level error rate, and crucially the ratio of errors to total requests
- Saturation: CPU, memory, connection pool utilization, queue depth

In Kubernetes specifically, additional signals matter:

- Pod restart counts and CrashLoopBackOff events
- Readiness probe failure rates
- HPA scaling behavior (are pods scaling up unexpectedly after deploy?)
- Container OOMKilled events
- Network policy denies and DNS resolution failures

The stack is typically Prometheus for metrics, Grafana for visualization, Loki or Elasticsearch for logs, and Tempo or Jaeger for traces. Pyroscope or Parca for continuous profiling is increasingly common at companies that take performance seriously.

Automated rollback triggers usually look like: error rate exceeds 2x baseline for 5 minutes, OR p99 latency exceeds SLO for 10 minutes, OR pod restart rate exceeds threshold. Argo Rollouts integrates directly with Prometheus queries to evaluate these as part of the promotion gate. If the analysis run fails, the rollout aborts and reverts to the previous ReplicaSet automatically.

The hardest part is distinguishing real degradation from noise. Teams use techniques like comparing the canary cohort to a control cohort with identical traffic shape, rather than comparing canary to historical baseline. This catches issues that would be masked by time-of-day patterns.

## Reverting a PR vs Pushing a Forward Fix

This is one of the most contested decisions in incident response. The right answer depends on blast radius, root cause clarity, and time pressure.

Revert when:

- The cause is unclear and the system is actively degraded
- Users are losing data, money, or access
- A forward fix would take more than ~15 minutes to develop and test
- The change is self-contained (no migrations, no irreversible side effects)
- You are in the middle of an incident and need to stop the bleeding

Forward fix when:

- The bug is well understood and the fix is trivial (one-line change, typo, config value)
- A revert would itself cause problems (data already migrated, dependent services already deployed against the new contract)
- The change is part of a larger sequence and reverting would create a worse state
- You are not in active incident mode and have time to test properly

The cultural norm at strong teams: revert is the default during an incident. The phrase "revert first, debug later" exists for a reason. A revert returns the system to a known-good state, which gives you time and oxygen to actually understand what happened. Forward fixes during incidents have a nasty habit of introducing second-order failures because they were written under pressure.

Mechanically, in a Kubernetes GitOps setup (ArgoCD, Flux), the revert path is:

1. `git revert <commit>` on a new branch
1. Open a PR, get expedited review (most teams have an "incident" label that bypasses normal review SLAs while still requiring approval)
1. Merge, CI builds new image, GitOps controller syncs
1. ArgoCD or Flux applies the previous manifest, K8s rolls pods

This is often slower than `kubectl rollout undo deployment/foo`, but it keeps Git as source of truth, which matters enormously for keeping things in sync. The imperative `rollout undo` should be reserved for true emergencies where every minute counts, with a follow-up commit to reconcile Git state.

## Database Migrations: Where Rollbacks Get Hard

Database migrations are the single biggest source of rollback complexity. Application code is stateless and easy to revert. Schema and data changes are not.

The core principle: migrations must be backward and forward compatible across at least one deploy cycle. This is the expand-contract pattern (also called parallel change):

1. Expand: add the new column, table, or index. Old code ignores it. Deploy this migration first.
1. Migrate: dual-write to old and new schema. Backfill historical data in batches. Both old and new code work.
1. Contract: remove the old column or table only after the new code has been stable in production for days or weeks.

This pattern means at any point in the rollout, you can roll back the application without rolling back the schema. Schema changes are effectively one-way doors; you treat them with that gravity.

Specific patterns to follow:

- Renaming a column? Add the new column, dual-write, backfill, switch reads, then drop old column in a separate deploy.
- Dropping a column? Stop writing to it, deploy and bake, stop reading from it, deploy and bake, then drop.
- Changing a column type? Add a new column with the new type, dual-write with conversion, migrate, switch reads, drop.
- Adding a NOT NULL constraint? Add column as nullable, backfill, deploy code that always writes a value, then add the constraint.

Tools like Django migrations, Alembic, Flyway, Liquibase, and Atlas all support migration versioning, but none of them protect you from a destructive migration that has already run. Postgres-specific tools like `pg_repack` and `pgroll` (from Xata) help with zero-downtime schema changes; pgroll specifically maintains both old and new schemas as virtual views during the transition.

For migration safety in CI, teams use linters like `squawk` (Postgres) or `gh-ost` checks to flag dangerous patterns: `ALTER TABLE` without `IF EXISTS`, missing `CONCURRENTLY` on index creation, locks held longer than a threshold, etc.

In a monorepo with multiple services hitting shared databases, you also need to detect migration conflicts before they merge: two PRs both creating migration `0042_*.py` is a classic footgun. CI checks that scan for number collisions and stale migration heads catch this before it becomes a production problem.

The honest truth: if a migration has already partially run and the application is broken, you usually cannot roll back the schema. You roll forward with a new migration that fixes the state, while reverting the application code if needed. Plan for this case explicitly in your runbooks.

## Putting It Together

The mature rollback story looks like this: feature flags handle 80% of "rollbacks" without any deployment changes. SLO-driven monitoring catches the issues that make it past flags, with automated promotion gates aborting bad rollouts before they reach full traffic. When a true rollback is needed, revert-first culture keeps incidents short, and expand-contract migration discipline ensures schema changes never trap you in a one-way door.

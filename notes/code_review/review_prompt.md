# Prompt

Act as a senior software engineer helping me improve my code review skills.

Create 5 code review exercises in **{MODE}**.

The goal is speed and precision. Each exercise should have exactly 1 major production-impact issue, and optionally 1 secondary issue. Do not include extra ambiguous problems, style distractions, or broad “could be improved” concerns.

Each exercise should be realistic enough to resemble production code, but small enough to review quickly.

Before showing me the exercises, privately decide the answer key for each one:

- Primary issue
- Optional secondary issue
- Category
- Why it matters in production
- Concrete fix

Do not reveal the answer key yet.

## Mode-specific guidance

If `{MODE}` is `Python`, use examples from:

- data pipelines
- FastAPI handlers
- Pydantic models
- SQLAlchemy database writes
- Requests API clients
- background jobs
- caching, queues, retries

Common libraries may include:

- Polars
- FastAPI
- Pydantic
- SQLAlchemy
- Pytest
- Requests

If `{MODE}` is `SQL`, use examples from:

- production analytics queries
- incremental models
- reporting queries
- warehouse transformations
- Postgres queries
- Snowflake-style warehouse queries
- index-sensitive queries
- joins, deduplication, time windows, and aggregations

Issues should focus on:

- silent data corruption
- duplicate or dropped records
- incorrect join grain
- incorrect time boundaries
- non-sargable predicates
- bad index usage
- accidental full table scans
- query patterns that fail at scale
- incorrect null handling
- incorrect aggregation logic
- unsafe backfills or incremental filters
- production locking or transaction impact

If `{MODE}` is `Go`, use examples from:

- HTTP handlers
- gRPC services
- GORM or database/sql queries
- Postgres writes
- webhook handlers
- background workers
- retries
- goroutines and channels
- context cancellation
- concurrency-safe caches
- external API clients

Common libraries may include:

- net/http
- context
- database/sql
- gorm
- grpc
- pgx
- testify
- httptest

Issues should focus on:

- missing context propagation
- missing timeouts
- goroutine leaks
- channel deadlocks
- unsafe shared state
- partial database writes
- webhook idempotency bugs
- bad retry behavior
- transaction misuse
- connection pool exhaustion
- incorrect error handling across service boundaries
- contract violations in gRPC or JSON APIs

If `{MODE}` is `Mixed`, include a balanced mix of Python, SQL, and Go.

## Global issue categories

Across the five exercises, cover at least four of these:

- silent data corruption
- unbounded growth: memory, queues, logs, retries
- hangs, deadlocks, or missing timeouts
- partial failures and inconsistent state
- incorrect behavior under load or concurrency
- contract violations across service or version boundaries
- security and trust-boundary violations
- data loss or duplicate processing
- production performance degradation
- unsafe database behavior

## Exercise format

For each exercise, include only:

1. A short title
1. The code snippet or SQL query
1. 1-2 sentences of production context

Do not include hints.\
Do not include answers.\
Do not include long explanations.\
Do not include intentionally messy code unless the messiness is directly tied to the intended issue.

Size limits:

- Python snippets: under 25 lines
- Go snippets: under 35 lines
- SQL queries: under 40 lines

I will reply with my review notes per exercise, numbered. My notes may be terse.

After I send my notes, grade them against your private answer key.

For each exercise, respond in this compact format:

## Exercise N

**Verdict:** Nailed / Mostly caught / Partially caught / Missed

**What you caught:**

- ...

**What you missed:**

- ...

**False positives:**

- ...

**Expected finding:**

- Primary: ...
- Secondary, if any: ...

**Fix:**
Show a corrected snippet/query or describe the specific fix concretely. Do not say vague things like “add error handling,” “optimize the query,” or “handle concurrency better.” Say exactly what should change.

## Grading rules

- Be strict.
- Do not invent extra issues after the fact.
- Do not reward generic comments unless they identify the actual production risk.
- Do not penalize me for ignoring style, naming, formatting, or test coverage unless that is the intended issue.
- Prioritize security, correctness, data loss, hangs, resource leaks, bad retries, scaling problems, inconsistent state, and production performance.
- Keep feedback concise. No walls of text.
- The intended issue should be crisp enough that a strong reviewer can identify it in 1-3 minutes.

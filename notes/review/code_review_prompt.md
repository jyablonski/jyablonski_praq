# Senior Data Engineer Code Review Drill

Help me sharpen my code review skills so I can be a more focused and effective reviewer during the agentic AI wave, when the volume of code being produced is much higher than it used to be. That means training me to quickly find the issues that actually matter in production, explain their impact clearly, and propose concrete fixes, without getting distracted by noise.

## Session settings

- Focus: {FOCUS} (Mixed, Python, SQL/dbt, Airflow, Terraform, CI/CD). Default: Mixed
- Exercises: 3
- Time budget: 15 minutes total, about 5 minutes per exercise
- Round: {ROUND}. If greater than 1, do not reuse issue types or scenarios from earlier rounds in this conversation

## Environment

The code lives in a company data platform monorepo:

- `dataplat/`: internal shared library (warehouse connections, incremental loading, secrets, retries, schema validation, logging)
- `dags/`: Airflow DAGs and custom operators
- `dbt/`: dbt project on Snowflake
- `infra/`: Terraform (AWS and Snowflake providers)
- `.github/workflows/` and `.pre-commit-config.yaml`: CI/CD

Before the exercises, show a **Shared library reference** block (under 25 lines): signatures plus a one-line docstring for the 3 to 6 `dataplat` utilities the exercises use. Those docstrings are the contract and must be accurate. A bug may come from code misusing a utility's contract, or from a defect inside a utility, but it must be findable from what is shown.

## Layers

Each exercise comes from a different layer:

1. **Shared library** (`dataplat/`): Python utilities used by many pipelines
1. **Pipeline code**: Airflow DAGs and operators, Python transforms (Polars, Pandas, SQLAlchemy, Requests)
1. **Modeling**: dbt models (incremental, snapshots, macros), Snowflake or Postgres SQL
1. **Infrastructure**: Terraform for S3, IAM, Snowflake roles, warehouses, grants, MWAA or ECS
1. **CI/CD**: GitHub Actions workflows, pre-commit hooks, dbt slim CI, deploy jobs

With Focus = Mixed: at least one Python exercise, at least one SQL/dbt exercise, and the third from infrastructure or CI/CD.

## Issue types

Each exercise's primary issue must be a different type:

- **Silent data corruption**: wrong join grain or fanout, null handling, timezone or date boundaries, type coercion
- **Duplicate or dropped records**: incremental filters, late-arriving data, non-idempotent reruns or backfills, retries with side effects
- **Plain bug**: wrong variable, off-by-one, mutable default, swallowed exception, wrong return value
- **Business logic error**: runs fine and looks reasonable, but violates a stated business rule
- **Performance or cost**: full scans, non-sargable predicates, defeated pruning, row-by-row loops, unbounded memory, oversized compute
- **Security or trust boundary**: secrets in logs or CI output, overly broad IAM or grants, untrusted PR code running with secrets, SQL injection in a shared helper
- **Operational failure**: missing timeouts, retries that amplify load, hangs, partial writes, non-idempotent Airflow tasks, CI that silently passes
- **Infrastructure state hazard**: a Terraform change that forces replacement or destroys data, unsafe defaults, drift

For business logic exercises, state the business rule explicitly in the context so the issue is objectively gradable.

## Constraints

- Exactly 1 primary issue with real production impact. Optionally 1 smaller but real secondary issue.
- No other defects. The code should otherwise be clean, idiomatic, and plausible for a mature team.
- No style bait, no TODOs, no names or comments that point at the bug. Comments may only be wrong if the wrong comment is the issue.
- Senior difficulty: prefer issues that only appear on rerun, at scale, at a time boundary, under concurrency, or across component boundaries. Avoid anything a linter or type checker would catch.
- A strong senior DE reading carefully should find the primary issue in under 4 minutes.
- Size limits (excluding the shared library reference): Python under 30 lines, SQL/dbt under 40, Terraform under 35, YAML under 35.

## Answer key

Before writing the exercises, commit to an answer key for each:

- Primary issue and issue type
- Optional secondary issue
- Production impact: what breaks, when, blast radius, how it would be noticed
- Concrete fix
- Prevention: the test, CI check, lint rule, dbt test, or contract change that would catch this class of bug

Do not reveal it. Do not change it after seeing my notes.

## Exercise format

For each exercise, include only:

### Exercise N: short title

`path/to/file.ext`

```lang
code
```

**Context:** 1 to 2 sentences covering what it does, how it runs (schedule, volume, consumers), and the business rule if relevant.

No hints, no difficulty labels, no issue type labels. End with: "Timer starts now. Reply with numbered notes."

## My notes

I will reply with numbered notes, possibly terse, aiming for issue, impact, fix. I may include elapsed time.

## Grading

Score each exercise out of 4:

- **Identification (0 to 2):** 2 = pinpointed the primary issue and its mechanism; 1 = right area but vague or wrong mechanism; 0 = missed
- **Impact (0 to 1):** stated a concrete production consequence
- **Fix (0 to 1):** correct and specific

Bonus +1 for the secondary issue. Minus 1 for each confident claim of a defect that is not real. No penalty for questions or flagged uncertainty.

Respond in this format:

## Exercise N: X/4

**Verdict:** Nailed / Mostly caught / Partially caught / Missed

**Caught:** ...

**Missed:** ...

**False positives:** ...

**Expected:** Primary: ... Secondary: ...

**Fix:** corrected snippet or precise diff

**Prevention:** one line on the guardrail that catches this class of bug

After all three:

**Total:** X/12 (+ bonus)

**Senior signal:** 1 to 2 sentences on the gap between my review and a staff-level review (for example: missed blast radius, ignored reruns, didn't consider downstream consumers).

**Next round:** which layer or issue type to drill next.

## Grading rules

- Be strict. Generic comments ("add error handling", "could be slow") earn nothing unless they name the specific mechanism.
- Do not invent new issues after the fact. If my notes identify a genuine defect that is not in the key, say so honestly and do not count it as a false positive.
- Ignore style, naming, formatting, and test coverage unless that is the intended issue.
- Keep feedback concise. No walls of text.

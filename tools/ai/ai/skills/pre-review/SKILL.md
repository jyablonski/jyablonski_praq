______________________________________________________________________

## name: pre-review description: Reviews staged git changes before commit. Manually invoked to do a final pass over a feature branch — checks repo standards, flags bugs and bad logic, spots DRY opportunities, and reports line-change stats. Use before committing or opening a draft PR. disable-model-invocation: true user-invocable: true

## Staged changes

Change stats (added / removed per file):
!`git diff --cached --numstat`

Full staged diff:
!`git diff --cached`

## Your task

Do a final review pass over the staged changes above before they are committed. This is a quality gate, not a rewrite — report findings only, do not modify any files. Review only what is staged (the `--cached` diff); ignore unstaged work and untracked files. If the staged diff is empty, say so and stop.

Work through these steps in order.

### 1. Report the change size

From the `--numstat` output, compute and report (ignore binary files, which show `-`):

- Lines added
- Lines removed
- Net change (added − removed)
- Total churn (added + removed)
- Files changed

Present as a short summary, then a per-file breakdown if more than ~5 files changed. Flag any single file with >300 lines of churn as worth splitting before review.

### 2. Discover this repo's standards

Don't assume conventions — find them. Look for and respect whatever this repo actually uses:

- Linter / formatter configs: `ruff.toml`, `.flake8`, `pyproject.toml`, `.golangci.yml`, `.sqlfluff`, `.yamllint`, `.editorconfig`, `.pre-commit-config.yaml`
- Project guidance: `AGENTS.md`
- Existing patterns: read 1–2 neighboring files in the same package/module to match local idioms (naming, error handling, import style, test layout)

If a finding is style-related, anchor it to the repo's own configured rule rather than personal preference.

### 3. Review the diff

Group findings by severity. Lead with the most important. Reference every finding by `path:line`. Read surrounding context with Read/Grep when the diff hunk alone is ambiguous (e.g. to judge a DRY opportunity against an existing helper, or to confirm a signature).

Blockers — must fix before commit:

- Real bugs: off-by-one, wrong operator, inverted/incomplete conditionals, unreachable branches
- Broken business logic or logic that contradicts the apparent intent
- Null/None/nil and empty-collection handling gaps
- Security: injection (string-interpolated SQL/commands), hardcoded secrets/credentials, unsafe deserialization
- Resource leaks, unclosed handles, unhandled errors

Should fix — standards & correctness-adjacent:

- Violations of the repo's configured lint/style rules
- Missing or wrong error handling vs. local patterns
- Missing tests for new logic where the repo clearly tests similar code
- Naming / structure inconsistent with neighboring code

DRY & refactor — only where it genuinely reduces duplication or risk:

- Copy-pasted blocks that should be a shared function/helper (point to where the helper exists or should live)
- Repeated literals/config that belong in one place
- Reinvented logic that an existing util in this repo already covers

Nits — optional, clearly labeled as low priority. Keep these brief and few.

### Language-specific checks

Apply the ones relevant to the files in the diff:

- Python — type hints on new public functions, mutable default args, bare `except`, `print` where logging is the norm, unused imports, f-string-built SQL, pandas chained-assignment / silent dtype issues
- Go — every returned error checked and wrapped (`%w`), nil checks before deref, `defer` placement and double-close, `context` propagation, goroutine/channel leaks, exported symbols documented
- SQL — no string-interpolated values (parameterize), no `SELECT *` in shipped queries, `UPDATE`/`DELETE` without `WHERE`, NULL handling across joins, implicit casts, naming + CTE conventions vs. the repo's models
- YAML — valid indentation/structure, no hardcoded secrets, schema-correct for its purpose (CI, dbt, Dagster, Airflow, k8s/Helm manifests), anchors/aliases used correctly

### 4. Output format

```
## Change size
<the stats from step 1>

## Findings
### Blockers
- path:line — <issue and concrete fix>
### Should fix
- ...
### DRY & refactor
- ...
### Nits
- ...

## Verdict
<Ready to commit | Address blockers first> — one line.
```

If a section has no findings, omit it. End with a one-line verdict.

## Boundaries

- Do not modify, stage, unstage, or commit anything. Report only. The user runs the commit.
- Review only staged changes.
- Optimize for precision over recall — a senior engineer is the audience. Don't flag style the repo doesn't enforce, don't restate what the code obviously does, and don't pad with praise. A short, high-signal review beats an exhaustive one.
- When unsure whether something is a real problem, say so explicitly rather than asserting it.

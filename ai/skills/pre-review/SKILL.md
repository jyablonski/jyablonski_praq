______________________________________________________________________

## name: pre-review description: Review a local diff or proposed code change before opening a PR, focusing on correctness, tests, production risk, and maintainability.

# pre-review

Use this skill when the user wants a strict pre-PR review of a code diff, branch, patch, or proposed implementation.

## Goal

Find meaningful issues before a human reviewer sees the PR. Prioritize correctness, missing tests, risky behavior changes, and unnecessary complexity. Avoid low-value style nits unless they affect maintainability.

## Inputs

Use whatever context is available:

- Current diff, staged changes, branch changes, or pasted patch.
- Existing tests and test output.
- Related ticket, implementation plan, or PR description.
- Relevant repository conventions and nearby code.

If only a partial diff is available, review the visible changes and state the limits of the review.

## Review priorities

Review in this order:

1. Correctness bugs and broken behavior.
1. Missing or weak tests.
1. Production risks, rollout risks, migrations, config changes, and backward compatibility.
1. Security, privacy, permissions, secrets, and unsafe logging.
1. Readability, maintainability, and unnecessary complexity.
1. Documentation, comments, and examples that drifted from behavior.

## Workflow

1. Determine the intended behavior from the request, diff, and surrounding code.
1. Compare the implementation against that intent.
1. Inspect changed call paths and likely downstream consumers.
1. Check whether tests cover the changed behavior and important failure paths.
1. Identify risky assumptions and edge cases.
1. Suggest the smallest concrete fixes.

## Output format

Use this structure:

```markdown
## Verdict
<Ready / Needs changes / Needs clarification>

## High-priority findings
- `<path>:<line if known>` — <issue>
  - Why it matters: <impact>
  - Suggested fix: <smallest safe fix>

## Test gaps
- <missing test or assertion>

## Risk notes
- <deployment, data, compatibility, security, or operational risk>

## Low-priority cleanup
- <optional improvement>

## What looks good
- <briefly note strong parts, only if meaningful>
```

If there are no material issues, say so directly and still list any reasonable test or rollout checks.

## Guardrails

- Do not rewrite the whole solution unless the current approach is fundamentally flawed.
- Do not nitpick formatting that should be handled by linters/formatters.
- Do not ask for broad rewrites when a smaller fix is sufficient.
- Do not invent line numbers if unavailable.
- Be direct and specific. Every finding should be actionable.

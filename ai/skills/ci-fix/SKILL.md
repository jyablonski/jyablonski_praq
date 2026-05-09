______________________________________________________________________

## name: ci-fix description: Analyze CI failures in context of the current diff and propose the smallest safe fix.

# ci-fix

Use this skill when the user has failing CI, failing tests, build errors, lint errors, type errors, migration conflicts, deployment checks, or flaky pipeline behavior.

## Goal

Classify the failure, connect it to the relevant code or environment change, and propose the smallest safe fix. Avoid random trial-and-error changes.

## Inputs

Use whatever context is available:

- CI logs, failing command, job name, error output, stack trace, screenshots, or pasted failure.
- Current diff or recent changes.
- Workflow files, build scripts, test configs, Dockerfiles, dependency files, and lockfiles.
- Local reproduction output if provided.

If logs are truncated, use the visible failure and state what additional log section would be useful, but still provide the best diagnosis possible.

## Workflow

1. Identify the exact failing command, job, and error.
1. Classify the failure:
   - real regression
   - missing/incorrect test update
   - lint/format/type issue
   - dependency or lockfile issue
   - environment/config/secrets issue
   - flaky test or timing issue
   - unrelated infrastructure failure
1. Connect the failure to the current diff or explain why it is likely unrelated.
1. Find the smallest safe fix.
1. Provide a local reproduction command when possible.
1. Recommend the test/CI command that should pass after the fix.

## Output format

Use this structure:

````markdown
## Failure summary
<one-paragraph summary>

## Classification
<real regression / test update / lint / dependency / environment / flaky / unrelated infra>

## Most likely root cause
<specific cause and why>

## Evidence
- <log line, file, command, or diff clue>

## Smallest safe fix
1. <step>
2. <step>

## Commands to run
```bash
<local reproduction command>
<verification command>
````

## Follow-up hardening

- \<optional: add regression test, reduce flake, improve workflow output>

```

## Guardrails

- Do not suggest broad rewrites before isolating the failure.
- Do not assume CI is flaky without evidence.
- Do not mask failures by weakening tests, disabling checks, or ignoring errors unless the user explicitly asks and the tradeoff is stated.
- Prefer fixing root cause over adding retries.
- Be explicit when the failure is probably unrelated to the user’s diff.
```

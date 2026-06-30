______________________________________________________________________

## name: docs-sync description: Manual-only skill. Do not invoke automatically. Use only when the user explicitly runs or mentions docs-sync by name. disable-model-invocation: true user-invocable: true

# docs-sync

## Invocation policy

This skill is manual-only.

Use this skill only when the user explicitly invokes it by name, for example:

- `/docs-sync`
- `$docs-sync`
- `run docs-sync`
- `use docs-sync`
- `invoke docs-sync`

Do not use this skill automatically for normal coding tasks, documentation edits, README updates, code review, PR review, changelog work, API changes, config changes, workflow changes, or stale-docs detection unless the user explicitly asks to run `docs-sync`.

If the user asks a general documentation question without explicitly invoking `docs-sync`, answer normally without loading or applying this skill.

## Goal

Keep documentation aligned with actual behavior. Focus on the docs that help future engineers build, run, test, deploy, debug, or use the changed system.

## Inputs

Use whatever context is available:

- Current diff, PR, implementation plan, or changed files.
- Existing docs, README files, runbooks, comments, examples, generated docs, config templates, and changelogs.
- Test commands, deployment commands, migration steps, environment variables, API behavior, and operational procedures.

If the code changed but docs are not present, identify whether docs should be added or whether no docs change is necessary.

## Workflow

1. Determine what behavior, interface, config, workflow, or operational process changed.
1. Find documentation that mentions the changed area.
1. Identify stale, missing, or misleading docs.
1. Draft the smallest accurate documentation update.
1. Keep docs concise and execution-focused.
1. Include commands, examples, or before/after behavior only when useful.

## Documentation targets

Check these when relevant:

- `README.md`
- `docs/`
- runbooks and operational guides
- API docs and OpenAPI specs
- configuration examples
- environment variable docs
- deployment docs
- migration notes
- changelog entries
- inline comments and docstrings
- architecture diagrams
- onboarding guides

## Output format

Use this structure:

```markdown
## Docs impact
<No docs change needed / Docs update recommended / Docs update required>

## Stale or missing docs
- `<path>` — <what is missing or stale>

## Proposed updates
### `<path>`
<draft replacement or new section>

## Notes
- <anything intentionally not documented, generated docs to update, or follow-up command>
```

If directly editing docs, summarize the changes afterward:

```markdown
## Summary
- <doc updated>

## Verification
- <spellcheck, docs build, link check, or not run>
```

## Guardrails

- Do not create verbose docs for trivial internal-only changes.
- Do not document behavior that is not implemented.
- Do not drift into marketing language.
- Prefer concrete commands and examples over abstract descriptions.
- Keep documentation consistent with existing terminology and structure.
- Preserve generated files unless the repo expects them to be edited directly.

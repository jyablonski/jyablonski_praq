______________________________________________________________________

## name: create-plan description: Convert a ticket, issue, bug report, or loose engineering request into a concrete implementation plan before writing code.

# create-plan

Use this skill when the user wants to plan an implementation before coding, especially for tickets, bugs, feature requests, refactors, migrations, or repo changes.

## Goal

Produce a practical engineering plan that reduces ambiguity before code is written. The plan should identify what likely needs to change, what should not change, how to test it, and what risks need attention.

## Inputs

Use whatever context is available:

- User request, ticket, issue, bug report, or design notes.
- Relevant repository files, tests, configs, docs, logs, or recent diffs.
- Existing conventions in the codebase.
- Any constraints the user gave around scope, style, timeline, rollout, or compatibility.

If important information is missing, proceed with explicit assumptions rather than blocking unless the ambiguity makes the plan unsafe or impossible.

## Workflow

1. Restate the target outcome in one or two sentences.
1. Identify the current behavior and the desired behavior.
1. Inspect or infer the likely code paths, files, configs, tests, and docs involved.
1. Separate required changes from optional cleanup.
1. Call out edge cases, compatibility concerns, data/schema impacts, security/privacy concerns, and rollout risks.
1. Define the smallest coherent implementation path.
1. Define the minimum useful test plan.
1. Define what “done” means.

## Output format

Use this structure:

```markdown
## Goal
<what we are trying to ship>

## Assumptions
- <assumption, only if needed>

## Current behavior
<short description>

## Desired behavior
<short description>

## Likely files / areas touched
- `<path>` — <why it matters>

## Implementation plan
1. <step>
2. <step>
3. <step>

## Tests
- <test case or test file>

## Risks / edge cases
- <risk and mitigation>

## Non-goals
- <what should not be changed>

## Definition of done
- <verifiable completion condition>
```

## Guardrails

- Do not write code unless the user explicitly asks.
- Do not over-design. Prefer the smallest safe change that satisfies the request.
- Do not invent repo conventions. Use the repository’s existing patterns when visible.
- Do not hide uncertainty. State assumptions clearly.
- Prefer concrete file paths, commands, tests, and rollout checks over generic advice.

______________________________________________________________________

## name: refactor-safely description: Plan or perform behavior-preserving refactors with explicit safeguards, tests, and rollback awareness.

# refactor-safely

Use this skill when the user wants to simplify, reorganize, rename, extract, consolidate, or clean up code without changing behavior.

## Goal

Improve code structure while preserving behavior. The refactor should be small, reviewable, and protected by tests or clear verification steps.

## Inputs

Use whatever context is available:

- Code to refactor, current diff, or target files.
- Existing tests and behavior examples.
- Public interfaces, API contracts, schemas, configs, CLI flags, or downstream callers.
- Repository style and conventions.

If behavior is not well covered by tests, identify that before making changes.

## Workflow

1. Define the behavior that must remain unchanged.
1. Identify public interfaces and compatibility boundaries.
1. Identify existing tests that protect the behavior.
1. Identify missing characterization tests if coverage is weak.
1. Propose the smallest coherent refactor.
1. Keep unrelated cleanup out of scope.
1. After changes, verify formatting, linting, tests, and any generated code.

## Refactor types

Common safe refactors include:

- Extract function or method.
- Rename internal symbols.
- Remove duplication.
- Split large functions.
- Simplify conditionals.
- Move code without changing imports/API behavior.
- Replace ad hoc logic with existing repository utilities.

Riskier refactors require extra care:

- Changing public interfaces.
- Changing database schemas or migrations.
- Changing serialization formats.
- Changing concurrency behavior.
- Changing dependency injection or lifecycle wiring.
- Changing error handling behavior.

## Output format

When planning, use:

````markdown
## Behavior to preserve
- <behavior or contract>

## Safety checks
- <existing test or command>
- <new characterization test if needed>

## Refactor plan
1. <small step>
2. <small step>

## Out of scope
- <cleanup intentionally avoided>

## Verification
```bash
<commands to run>
````

````

When reviewing or applying a refactor, use:

```markdown
## Summary
<what changed structurally>

## Behavior changes
None expected.

## Safety checks run
- `<command>` — <result if known>

## Remaining risk
- <risk, or “None obvious from the available context.”>
````

## Guardrails

- Do not change behavior unless the user explicitly approves it.
- Do not mix refactors with feature changes.
- Do not expand scope into broad redesign.
- Do not remove tests to make a refactor pass.
- Prefer multiple small refactors over one large diff.
- Preserve public API, schema, config, CLI, and wire-format compatibility unless the user asks otherwise.

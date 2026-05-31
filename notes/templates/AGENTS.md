# AGENTS.md

<!--
Reusable template. Before committing this file to a repo:
- Replace every <placeholder> with an exact, verified, copy-pasteable value.
- Delete any section or line that does not apply to the repo.
- Keep it short. Every low-value line crowds out a high-value one.
-->

## Project overview

<app name> is a <type of app> that <short use case>.
Primary users are <users>. The main runtime flow is <one sentence>.

## Tech stack

- Language: <language and version>
- Frameworks: <frameworks>
- Database: \<database, or remove if none>
- Testing: <test runner>
- Tooling: \<linter, formatter, type checker, codegen, etc.>

## Repository layout

- `<dir>/` <what lives here>
- `<dir>/` <what lives here>
- `<dir>/` <what lives here>

## Local development commands

<!-- Exact invocations including flags. "Run tests" is useless; the real command is not. -->

- Install dependencies: `<command>`
- Run the app: `<command>`
- Run tests: `<command>`
- Run a single test: `<command>`
- Lint: `<command>`
- Format: `<command>`
- Type check: `<command>`

Expensive or destructive commands, do not run unless the task asks for it:

- `<command>`: \<why, e.g. takes 20 minutes, needs a live DB, mutates state>

## Testing expectations

Run the smallest relevant test first, then the broader suite before finishing.
Add or update tests for any behavior change.
Prefer integration tests when changing database, queue, API, or serialization behavior.
Do not remove tests unless the behavior under test is intentionally removed.

## Conventions

<!-- Only non-obvious, project-specific rules. Skip anything a competent agent already does. -->

- \<project-specific rule, e.g. errors return Result and never panic in library code>
- Keep public APIs stable unless the task explicitly calls for a breaking change.
- Mirror existing patterns: for <X>, follow the structure in `<path>`.

## Architecture boundaries

- Keep database access isolated in `<module>`.
- \<other boundary, e.g. no business logic in handlers or controllers>
- Do not introduce new global mutable state.
- Do not add a dependency without a clear reason.

## Security

<!-- Delete lines that do not apply. -->

- Never commit secrets, tokens, credentials, or `.env` files.
- Do not log sensitive user data.
- Validate external input at trust boundaries.
- Use parameterized queries, never string-interpolated SQL.

## Git and PR expectations

- Use semantic commit types: `feat`, `fix`, `chore`, `bug`.
- Before opening a PR, run `<required gate command>`.
- Use the `create-pr` skill to open pull requests.
- Follow the pull request template in the `.github/` folder of the repo.
- PR descriptions should state what changed, why, and how it was tested.

## Definition of done

Before considering a task complete, all of these must pass:

- `<command>`
- `<command>`
- `<command>`

## Agent instructions

Inspect existing patterns before introducing new ones. Prefer minimal, targeted diffs. Do not rewrite unrelated code. Call out any tests or checks that could not be run.

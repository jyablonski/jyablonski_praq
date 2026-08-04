# Local Checks vs CI Checks

## Principle

Local hooks provide fast feedback; protected CI enforces the repository's rules.

Hooks are not an enforcement boundary. A developer can bypass them with `--no-verify` or `SKIP`, forget to install them, or commit through a system that does not have them, such as a dependency bot or the web UI. Merge commits are not categorically exempt: Git and pre-commit support `pre-merge-commit`, but that hook must also be installed and can still be bypassed.

CI is authoritative only when the relevant workflow runs for every merge path and its checks are required by a branch protection rule or repository ruleset. If the repository uses GitHub's merge queue, required workflows must also handle the `merge_group` event. A CI check that is optional, skipped by path filters, or absent from a merge path is not actually enforcing anything.

Rule: anything the repository requires must have a CI gate. A local hook is a convenience that should run the same implementation or a deliberately documented subset of that gate.

## Tiering

There is no universal two-second cutoff. Keep commit-time checks fast enough that developers leave them enabled, measure them in the actual repository, and move checks to `pre-push`, an explicit local command, or CI as they become expensive. As a rough target, commit hooks should feel nearly instantaneous and should avoid network access, service dependencies, and whole-repository setup.

| Check | Pre-commit | Pre-push or manual | CI | Notes |
| ------------------------------------------------------------ | ---------- | ------------------ | --- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| Formatter and simple file normalization | ✅ | — | ✅ | Run fix mode locally and check mode in CI |
| Syntax, conflict-marker, whitespace, and basic config checks | ✅ | — | ✅ | Usually file-local and deterministic |
| Fast lint on staged files | ✅ | — | ✅ | Use the same rules and version in both places |
| Type checking | ⚠️ | ✅ | ✅ | Placement depends on repository size and whether project dependencies are required |
| Full lint, dead-code analysis, and generated-file checks | ❌ | ✅ | ✅ | Often need whole-project context |
| Fast unit tests for affected code | ⚠️ | ✅ | ✅ | Useful only when selection is reliable and runtime is predictable |
| Full unit, integration, end-to-end, and build checks | ❌ | ⚠️ | ✅ | CI provides a clean, controlled environment |
| Dependency, vulnerability, SBOM, and license checks | ❌ | ⚠️ | ✅ | May require the lockfile, external advisory data, or network access |
| Secret detection | ✅ | — | ✅ | Fast detectors are useful locally, but CI and provider-side scanning remain necessary |
| `dbt parse` and manifest validation | ⚠️ | ✅ | ✅ | `dbt parse` does not connect to the warehouse, but parsing may still require the adapter, packages, profile, and referenced environment variables |

`pre-push` is a useful middle tier for checks that are too slow for every commit but cheap enough to run before consuming CI capacity. It remains local and bypassable, so it cannot replace CI. Keep an explicit command such as `make check` or `just check` for developers who want to reproduce the complete CI gate before pushing.

## Preventing Drift

The most confusing failure mode is not a check that exists only in CI; it is nominally the same check running with different commands, versions, configuration, inputs, or environments. “Passed locally, failed in CI” is sometimes legitimate, but accidental drift makes both signals less credible.

- Option A — `.pre-commit-config.yaml` owns the check. CI runs `pre-commit run --all-files`, so the hook revision, arguments, and file filters have one owner. This works best for self-contained hooks whose managed environments contain everything they need.

- Option B — the project task runner owns the check. `make lint-check`, `just lint-check`, or an equivalent script is called by both the hook and CI. This works well for mixed-language repositories and tools that must run inside the project's locked environment.

Choose one owner per check; do not duplicate its command-line arguments and version pins. Pin tool versions through hook revisions, lockfiles, tool manifests, or one bootstrap mechanism; do not use floating versions such as `@latest` in an enforced check. Pin third-party CI actions as well, preferably to immutable commit SHAs where the platform supports it.

Parity includes more than the tool version. Keep the working directory, config discovery, generated inputs, language version, build tags, environment variables, and dependency groups aligned. CI may intentionally test additional operating systems or runtimes, but the common local command should match at least one CI job.

## Managed Hook Environments vs the Project Environment

Pre-commit creates and caches isolated environments for many supported hook languages. Isolation is an advantage for self-contained tools because the hook revision and `additional_dependencies` describe the environment without requiring a project bootstrap.

Current pre-commit versions call the non-isolated hook language `unsupported`; it was named `system` before pre-commit 4.4, and `system` is currently a legacy alias. An `unsupported` hook receives no managed environment, cannot use `additional_dependencies` to provision one, and resolves its entry through the environment in which Git launched the hook.

### Why this matters for mypy

An isolated mypy installation does not automatically see the project's installed packages or stub packages. By default, missing imports produce errors and are treated as `Any` for subsequent analysis; if those import errors are suppressed, the hook can pass while providing substantially weaker checking than CI. Either fully reproduce the required dependencies with the hook's managed environment or run mypy through the project's locked environment.

```yaml
minimum_pre_commit_version: "4.4.0"
repos:
  - repo: local
    hooks:
      - id: mypy
        name: mypy
        entry: uv run --locked mypy
        language: unsupported
        pass_filenames: false
        always_run: true
        stages: [pre-push, manual]
```

`repo: local` means the hook definition lives in the repository; `language: unsupported` means pre-commit does not create an environment for it. These separate settings are often paired.

The same decision applies to Go and other ecosystems. `language: golang` installs a hook repository with `go install ./...` inside an isolated `GOPATH`, which is reproducible when the hook revision owns the tool version. If the repository already pins and installs that tool through a Go tools module, task runner, or bootstrap script, calling the project-owned command avoids a second version pin.

Use a managed hook environment when the hook is self-contained and its revision plus declared dependencies fully define its behavior. Use the project environment when the tool needs project dependencies, plugins, build metadata, or a version already owned by the repository. Tools such as SQLFluff with a dbt templater are project-dependent even if their basic mode is self-contained; `terraform fmt` requires a Terraform executable unless the selected hook implementation explicitly provisions one.

The project environment requires additional setup. Route entries through the project's environment manager or task runner instead of assuming an activated shell, because GUI Git clients and IDEs may launch hooks with a different `PATH`. Provide one bootstrap command, and make missing prerequisites fail clearly rather than silently weakening a check.

## Fix Mode vs Check Mode

Local formatters can modify files; CI must report a diff and fail without committing changes. Examples include `ruff format --check`, `terraform fmt -check -recursive`, and a small wrapper around `gofmt -l` that prints any unformatted files and exits nonzero. Do not assume every formatter returns a failing status merely because it printed a diff.

Pre-commit's `pre-commit` stage operates on staged file contents, temporarily hiding unstaged changes. CI should normally validate the complete repository with `pre-commit run --all-files` or the equivalent full-scope task so a new rule or tool version also checks existing files. Very large monorepos can use selective checks, but only when dependency and configuration changes correctly expand the affected set and a periodic full run catches selection mistakes.

Auto-fix automation is a workflow choice, not a substitute for validation. If a bot pushes changes, ensure the new commit runs the complete required checks, does not overwrite concurrent work, and complies with the repository's signing and authorship policy. On GitHub, pushes made with a workflow's default `GITHUB_TOKEN` generally do not trigger another workflow run, so an auto-fix job needs an explicit and carefully secured design.

## CI Job Design

Keep lint and static analysis in jobs separate from tests and builds when they have different setup, permissions, caches, or failure ownership. Separate jobs provide readable required-check names, keep linters away from unnecessary service credentials, and allow independent work to run in parallel.

Do not make tests depend on lint only to save compute. Running them in parallel reports all failures in one cycle. Add `needs` only when a downstream job consumes an upstream artifact or is expensive enough that deliberately gating it saves meaningful cost.

Use stable job names for required checks, grant the minimum token permissions, and avoid giving lint jobs secrets they do not need. Treat caches as performance optimizations rather than required inputs for correctness. If workflows use path filters, confirm that every required check still reaches a terminal result; a skipped required workflow can otherwise leave a pull request waiting indefinitely.

Run deterministic checks on pull requests and on any merge-queue or protected-branch path used by the repository. Network-dependent security checks need an explicit failure policy for advisory-service outages. Flaky checks should be fixed or made non-blocking until a failure reliably identifies a repository problem.

For example:

```yaml
jobs:
  lint:
    # Checkout and pinned toolchain setup omitted.
    steps:
      - run: make lint-check
  test:
    # Runs in parallel with lint.
    steps:
      - run: make test
  build:
    needs: [lint, test]
    steps:
      - run: make build
```

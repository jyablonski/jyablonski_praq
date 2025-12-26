# Selective Test Execution in Large Codebases

When test suites grow beyond 20-25 minutes, the cost of running everything on every PR becomes painful — slow developer feedback, wasted CI compute, and people skipping tests locally. Selective test execution strategies aim to run only the tests that could possibly be affected by a given change.

## Core Strategies

Dependency graph analysis is the most sophisticated approach. Build tools construct a graph of which modules depend on which others based on imports and explicit declarations. When files change, the tool traverses the graph to identify all potentially affected code and runs only those tests. This is what tools like Bazel, Buck2, and Pants do natively.

Test impact analysis (TIA) takes a different angle — instrument test runs to record which tests touch which source files via coverage or tracing. Store that mapping, then on a PR, look up which tests historically exercised the changed files. Microsoft has published extensively on this from their Azure DevOps work.

File-path heuristics are simpler but effective for well-structured repos. Use naming conventions and directory structure to scope test runs — if `services/billing/` changed, only run tests in `services/billing/tests/`. Misses cross-cutting changes but easy to implement.

Affected target detection in monorepos is a variant for JS/TS ecosystems. Tools like Nx, Turborepo, and Lerna detect which packages are affected by changes and scope test runs accordingly.

## Standard Pattern: Fast PR Feedback, Full Suite on Merge

Regardless of tooling, the industry-standard approach is:

- PR builds: Run selective tests based on what changed (`--changed-since=origin/main`)
- Merge to main: Run the full test suite

Selective testing optimizes for fast feedback during development, but it's making a bet that your dependency analysis is complete. Running the full suite on merge is your safety net — it catches anything the graph missed (dynamic imports, reflection, config-driven behavior). It also establishes a clean baseline for future `--changed-since` comparisons.

Some teams also run full suites nightly as an extra backstop.

## Tools That Implement This

[Bazel](https://bazel.build/) — Open-source, originally from Google (internal name: Blaze). The most widely adopted. Polyglot by design, supports Python, Go, Java, C++, and more via rule sets. Steep learning curve but extremely powerful for massive monorepos.

Buck2 — Meta's equivalent, recently rewritten in Rust. Same core concepts as Bazel with Meta's flavor. Also polyglot.

[Pants](https://www.pantsbuild.org/stable/docs/python/overview/enabling-python-support) — Started at Twitter, now independently maintained. Explicitly aimed at Python and Go (plus Java/Scala). More approachable than Bazel with better out-of-the-box ergonomics. Can infer dependencies from imports automatically.

Nx / Turborepo — Focused on JavaScript/TypeScript monorepos. Lighter weight than Bazel/Pants but effective for their ecosystem.

## When This Investment Makes Sense

Under 60 seconds: Not worth it. The overhead of maintaining BUILD files exceeds the savings.

5-15 minutes: Consider simpler strategies first — path-based filtering, parallelizing across CI runners, test splitting.

20+ minutes and growing: This is where dependency-aware test selection pays off. Developer feedback loops are suffering, CI costs are adding up, and people are skipping tests locally.

Team size matters too — 50 engineers waiting 30 minutes each for CI is enormous aggregate waste. A small team with a few PRs per day can tolerate more.

## Pants: A Practical Example for Python and Go

Pants is a good fit if you're working primarily in Python and Go. It has first-class support for both and emphasizes developer ergonomics over configuration complexity.

### What You Add to Your Repo

A `pants.toml` at the root for global configuration:

```toml
[GLOBAL]
pants_version = "2.20.0"
backend_packages = [
    "pants.backend.python",
    "pants.backend.experimental.go",
]

[python]
interpreter_constraints = [">=3.10"]

[source]
root_patterns = ["src", "tests"]
```

BUILD files in each directory declaring what lives there. For Python source:

```
python_sources()
```

For Python tests:

```
python_tests()
```

For Go packages:

```
go_package()
```

For your go.mod:

```
go_mod(name="mod")
```

Pants infers dependencies from imports automatically, so most BUILD files are just one or two lines.

### Adoption Path

1. Install Pants
2. Run `pants tailor` to auto-generate BUILD files based on your existing structure
3. Verify `pants test ::` produces the same results as your current test runner
4. Update CI to use `pants test --changed-since=origin/main` for PR builds
5. Keep `pants test ::` for merges to main

### Example CI Configuration (GitHub Actions)

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0 # Needed for --changed-since to work

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Run tests
        run: |
          if [ "${{ github.event_name }}" == "pull_request" ]; then
            pants test --changed-since=origin/main
          else
            pants test ::
          fi
```

### When You Need More in BUILD Files

Explicit dependencies for things that can't be inferred:

```
python_sources(
    dependencies=[
        "src/billing:lib",
    ],
)
```

Test configuration:

```
python_tests(
    timeout=120,
)
```

Multiple targets in one directory:

```
python_sources(
    name="lib",
    sources=["processor.py", "utils.py"],
)

python_sources(
    name="cli",
    sources=["main.py"],
    dependencies=[":lib"],
)
```

## Tradeoffs

Simpler heuristics (path-based filtering) are easy to implement but might miss cross-cutting changes or run too much.

Dependency-graph approaches (Bazel, Pants) are precise but require tooling investment and ongoing BUILD file maintenance.

The right choice depends on your test suite duration, team size, and how much pain you're currently experiencing.

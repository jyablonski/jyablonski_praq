______________________________________________________________________

## name: create-pr description: Manual-only skill. Do not invoke automatically. Use only when the user explicitly runs or mentions create-pr by name. disable-model-invocation: true user-invocable: true

# create-pr

## Invocation policy

This skill is manual-only.

Use this skill only when the user explicitly invokes it by name, for example:

- `/create-pr`
- `$create-pr`
- `run create-pr`
- `use create-pr`
- `invoke create-pr`

Do not use this skill automatically for normal coding tasks, git tasks, GitHub tasks, documentation tasks, review tasks, or PR-related discussion unless the user explicitly asks to run `create-pr`.

If the user asks a general question about pull requests without explicitly invoking `create-pr`, answer normally without loading or applying this skill.

## When to use this skill

Use this skill when the user wants you to open a draft PR for the current branch.

Do not commit changes.
Do not push changes.
Assume the user handles those steps unless they explicitly ask otherwise.

## Workflow

### Step 1: Inspect branch context

Run these commands in parallel to understand what will go into the PR:

```bash
git branch --show-current
git status --short --branch
git log -1 --pretty=format:%s%n%n%b
git diff --stat origin/main...HEAD
```

If the repo uses a different default base branch, detect it from `origin/HEAD` and use that instead of `main`.

### Step 2: Write the PR title

The title must match this semantic PR title format:

```text
type: lowercase description
```

Allowed types:

- `feat`
- `fix`
- `chore`

Use the type rules below strictly:

- Use `feat` for anything that adds new functionality, user-facing behavior, product functionality, API behavior, CLI behavior, UI behavior, or meaningful new software capability.
- Use `fix` only for a bug fix that corrects broken, incorrect, or unintended behavior. This should be rare.
- Use `chore` for everything else, including refactors, documentation, tests, CI, build changes, dependency updates, formatting, cleanup, internal tooling, config changes, infrastructure changes, and maintenance work.

Do not use `docs`, `test`, `build`, or `ci` as PR title types. Those changes should use `chore` unless they are part of a new feature or a bug fix.

When in doubt, omit the scope. Never copy scopes from existing commit history. Scopes should only be added in a monorepo context w/ multiples services.

The description must start with a lowercase letter and stay concise.

Examples:

- `feat: add user timezone endpoint`
- `feat: add project validation command`
- `fix(frontend): correct trace propagation in server actions`
- `chore: improve local validation workflow`
- `chore: simplify release workflow`
- `chore: update deployment notes`

### Step 3: Write the PR body

Follow `.github/pull_request_template.md` if it exists.

Keep the body brief:

- `Description`: 1-2 sentences max explaining what changed and why at a high level
- `Added`, `Updated`, `Deleted`: 3-5 bullets max total across all sections
- Omit any section that does not apply
- Focus on what changed and why, not implementation detail

Example:

```markdown
## Description

One-two sentence high-level summary.

### Updated

- Short bullet
- Short bullet
```

### Step 4: Create the draft PR

Use `gh pr create --draft` with the detected base branch, the current branch as head, and the semantic title/body you prepared.

Example:

```bash
gh pr create --draft --title "type(scope): description" --body "$(cat <<'EOF'
## Description

Brief explanation.

### Updated

- Item
EOF
)"
```

### Step 5: Return the PR URL

Print the PR URL so the user can open it.

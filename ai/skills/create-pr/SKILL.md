______________________________________________________________________

## name: create-pr description: Create a draft GitHub pull request for the current branch with a semantic title and a concise body that follows the repository pull request template. Use when the user is ready to open a draft PR and does not want Codex to commit or push changes. user_invocable: true

## When to use this skill

Use this skill when the user wants Codex to open a draft PR for the current branch.

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

The title must match the semantic PR title format used by the repository:

```text
type(scope): lowercase description
```

Allowed types:

- `feat`
- `fix`
- `docs`
- `test`
- `build`
- `ci`
- `chore`

Scope is optional but recommended when there is a clear area such as `infra`, `backend`, `frontend`, `dbt`, `dagster`, or a service name.

The description must start with a lowercase letter and stay concise.

Examples:

- `feat(backend): add user timezone endpoint`
- `fix(frontend): correct trace propagation in server actions`
- `chore(infra): improve local validation workflow`

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

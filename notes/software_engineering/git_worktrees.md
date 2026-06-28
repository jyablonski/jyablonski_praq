# Git Worktrees

## What they are

A branch is just a pointer to a commit. Normally `git checkout` mutates your one working directory in place, so only one branch is "live" at a time.

A worktree breaks that assumption. It lets you have multiple working directories on disk, all backed by the same `.git` object store, each with its own checked-out branch, index, HEAD, and uncommitted changes.

Your original clone is not special — it is simply the first worktree ("the main worktree"). Everything else is a linked worktree hanging off the same repo.

## How they work

```bash
git worktree add ../app-feature feature-x      # existing branch
git worktree add -b feature-y ../app-feature-y # new branch in one step
git worktree list                              # see all worktrees
git worktree remove ../app-feature             # clean up
git worktree prune                             # clear stale admin files
```

Key properties:

- Objects/history are SHARED. Creating a worktree is cheap; history isn't copied.
- Working files and index are ISOLATED per worktree.
- A given branch can be checked out in AT MOST ONE worktree at a time. Git refuses a second checkout of the same branch.
- A fresh worktree is a clean checkout: gitignored files (`.env`, local config) are NOT present. Plan to copy or regenerate them.
- Delete with `git worktree remove`, not `rm -rf` (that leaves dangling files until you `prune`).

## Why this matters for AI agents

The scarce resource is WORKING DIRECTORIES, not branches or IDE windows. An agent needs a real directory to read, write, build, and run in. Worktrees give each agent its own sandbox.

Two distinct benefits — keep them separate:

1. PARALLELISM: N agents in N worktrees run at once without colliding. Only valuable if code generation is actually your bottleneck.
1. ISOLATION: the agent works in its own directory, your checkout stays live, and a bad run is `git worktree remove` instead of unwinding a dirty tree. This holds even with a single agent and zero parallelism.

For most solo, human-reviewed changes, ISOLATION is the real win. Parallelism is the headline that often doesn't apply.

## Enabling it in AI tools (as of mid-2026, verify against your version)

- Claude Code: native `--worktree` / `-w` flag per session; `isolation: worktree` in a subagent's frontmatter; `.worktreeinclude` to copy gitignored files into new worktrees.
- Codex app: pick "Worktree" mode when creating a thread; "Handoff" moves a thread between Local and Worktree.
- Codex CLI: create the worktree manually, then launch `codex` inside it. Set `CODEX_HOME` for per-worktree session/config.
- AGENTS.md / CLAUDE.md: defines CONVENTIONS inside a worktree (branch naming, "always PR", run tests) — it does not turn worktrees on.

## When to use them — good cases

GOOD 1 — Long-running agent task. The agent iterates for 10-20 min (edit, test, fix). A worktree keeps your main checkout free the whole time instead of locking you out.

GOOD 2 — Risky or exploratory change. Spikes, dependency bumps, maybe-doomed refactors. Clean abort: delete the worktree and the entire mess goes with it. Your main tree never saw it.

GOOD 3 — Test someone else's branch mid-task. Run a failing PR in a separate directory while your own uncommitted work sits undisturbed. No `git stash` dance, no lost context.

## When NOT to use them — bad cases

BAD 1 — Quick change you'll babysit. A 5-minute edit you watch synchronously, no uncommitted work to protect. The worktree is pure ceremony. Better: plain `git checkout -b`, or let the agent work in place.

BAD 2 — Parallel agents just to produce more code. If generation isn't your bottleneck, fanning out agents only floods the review queue — the actually-expensive, serial step. Better: one agent, one scoped change, careful human review.

BAD 3 — Two competing agents you plan to merge. Rival implementations of the same logic are substitutive, not additive. Merging them conflicts everywhere or produces an incoherent Frankenstein. Better: generate both if you must, then PICK A WINNER and hand-port the good bits. `git merge` is the wrong tool to combine them.

## Rule of thumb

Reach for a worktree when isolation saves you real friction — lockout, stash-juggling, or messy cleanup. Skip it when you don't need isolation, or when you're using it to chase parallelism you don't actually want. Branch when the work is short and you're watching it; worktree when it has duration, risk, or collides with state you care about.

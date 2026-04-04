## Git Worktrees

### What are they?

Normally, a git repo has one working directory tied to one checked-out branch. If you want to work on a different branch simultaneously, you either stash your changes, commit a WIP, or clone the repo again. Worktrees solve this by letting you check out multiple branches from the same repo at the same time, each in its own directory on disk.

```bash
git worktree add ../my-repo-feature feature-branch
git worktree add ../my-repo-hotfix hotfix/auth-bug
git worktree list
```

What you end up with:

```
my-repo/              ← main worktree (original clone)
my-repo-feature/      ← linked worktree, on feature-branch
my-repo-hotfix/       ← linked worktree, on hotfix/auth-bug
```

All three share the same `.git` object store, so they're not separate clones. The packed objects, refs, commit history -- all shared. Only the working tree (the checked-out files) and the `HEAD` differ per worktree. This means no extra disk overhead for the git history, and operations like `git log` work identically across all of them.

A few constraints worth knowing: you can't have the same branch checked out in two worktrees simultaneously. Git enforces this because two worktrees writing to the same branch ref would cause chaos. Each linked worktree gets a file under `.git/worktrees/<name>/` tracking its HEAD, index, and lock state.

Cleanup is just:

```bash
git worktree remove ../my-repo-feature
git worktree prune  # cleans up stale metadata
```

______________________________________________________________________

### How LLMs are using this for parallelism

This is where it gets interesting. The core problem LLM coding agents have is that they're stateful about the filesystem -- if you ask Claude Code or a similar agent to work on something, it's reading and writing files in one working directory. If you want it to try two different approaches concurrently, or work on two tickets at once, you have a conflict.

Worktrees solve this cleanly because each agent instance gets its own isolated working tree but shares the same repo history. The pattern looks like this:

**Approach 1: Parallel task execution**

You have 5 GitHub issues to work through. Instead of running them serially, an orchestrator:

1. Creates 5 worktrees, one per issue, each on a fresh branch
1. Spawns 5 agent instances, each pointed at its own worktree directory
1. Each agent reads/writes/runs tests completely independently
1. Orchestrator collects results, creates PRs, tears down worktrees

No agent steps on another's files. No locking. No coordination needed at the filesystem level.

**Approach 2: Speculative/exploratory branching**

This is used when the solution space is uncertain. You want to try three different architectural approaches to a refactor:

1. Three worktrees, three agents, same starting point
1. Each agent pursues a different approach independently
1. A judge/orchestrator reviews all three outputs and picks the best one (or synthesizes across them)

This is essentially Monte Carlo tree search applied to code generation -- run N branches in parallel, evaluate, keep the best.

**Approach 3: Reviewer/implementer separation**

One worktree for the implementing agent, a separate worktree for a reviewing agent. The reviewer can check out the implementation branch in its own worktree and run analysis without disturbing the implementer's working state. This maps well to how Claude Code's multi-agent mode works when you have a subagent doing implementation and a parent agent doing orchestration.

______________________________________________________________________

### Why not just use separate clones?

You could. But worktrees have meaningful advantages in the agent context:

- shared object store means `git fetch` in one place is visible everywhere immediately
- branch awareness is centralized -- the orchestrator can see all branch states from the main worktree
- lighter weight -- no redundant `.git` directories or re-downloaded history
- cleaner mental model for the orchestrator: one repo, N views into it

The pattern is showing up prominently in Claude Code's documented multi-agent workflows, and tools like Aider and Amp are building around it too. It's a case where a 20-year-old git feature turns out to be the right primitive for a genuinely new use case.

# GitHub Merge Queue

## Why "Update branch" stops scaling

GitHub's "Update branch" button (rebase or merge `main` into your PR branch) is the simpler precursor to a merge queue. It exists for the same reason: catch incompatibilities between your PR and what's currently on `main` before merging. The flow is: someone else merges, your PR's base is now stale, you click "Update branch," CI re-runs against the new base, you merge.

This works fine on small repos and small teams:

- Low merge frequency means your branch rarely goes stale before you can merge it
- CI is usually fast enough that re-running after an update isn't painful
- Few enough devs that coordinating "I'm merging next, hold on" via Slack is realistic
- Fewer cross-cutting modules means semantic conflicts are rare to begin with

It falls apart on monorepos with dozens of developers and services:

- Livelock on slow CI. You click "Update branch," CI starts, takes 15 minutes. In that window, someone else merges. Now your branch is stale again the moment your CI finishes. You update, re-run, get scooped again. Busy devs always win the merge race against slower CI, and PRs from people who can't sit and babysit them never land.
- Manual coordination cost. With 30+ devs, "who's merging next" becomes a Slack conversation. People forget to update, settings drift (e.g. "Require branches to be up to date" gets turned off because it's annoying), and stale merges sneak through and break `main`.
- CI cost explodes. Every "Update branch" click is a full CI run. On a slow monorepo suite that's expensive, and it multiplies across every PR that has to update multiple times because of merge races.
- Tight race window still exists. If two PRs both pass CI and hit merge within the few-second window before either fast-forward completes, neither tested the combined state. Rare on small teams, much more likely with 30+ devs hammering the merge button.

The merge queue solves all four: it serializes the merge point automatically (no Slack coordination, no race window), eliminates the livelock (your queue position is locked once you enter), tests the combined state on the queue branch, and only runs CI on that queue branch (not on every speculative update).

## What Merge Queues Are

A merge queue serializes the merge point on a protected branch. Instead of PRs merging directly to `main` as soon as they're approved and green, they enter a queue where CI runs against the *combined* state of `main + everything ahead of them in the queue + their own changes*. Only after that combined-state CI passes does the PR fast-forward onto `main\`.

## The Problem They Solve

When two PRs both pass CI independently against `main`, that doesn't mean they pass CI together. CI on PR A tested "main + A." CI on PR B tested "main + B." Neither tested "main + A + B." If A and B touch overlapping code, or have semantic conflicts that aren't textual conflicts, you can merge both green PRs and end up with broken `main`.

Classic example: A renames `getUser` to `getUserByID` and updates all callers. B adds a new caller of `getUser` in a different file. Both PRs pass CI. Both merge. `main` is now broken because B's new caller references a function that no longer exists. No textual conflict, both PRs were green, `main` is red.

The queue solves this by testing the combined state before allowing the merge to actually happen. `main` is guaranteed green because nothing merges to `main` without first being tested against everything ahead of it.

## Walkthrough: two PRs to a Go backend

Setup: trunk-based dev, `main` protected with merge queue required, service deploys via image push + ArgoCD reconciliation. CI runs unit, integration, and e2e against the queue branch.

### T+0:00 Alice opens PR #501

Adds gRPC endpoint `GetLeadStatus`. Touches `internal/leads/service.go` and `proto/leads.proto`. PR CI passes. Approved.

### T+0:00 Bob opens PR #502

Refactors lead classification, extracts `ClassifyLead` from `service.go`. Also touches `internal/leads/service.go`. PR CI passes. Approved.

Both branched off `main` around the same time. Both touch `service.go` but in different functions, so no textual conflict.

### T+0:03 Alice clicks "Merge when ready"

Alice enters the queue. GitHub creates `gh-readonly-queue/main/pr-501-<sha>` containing `main + Alice`. Queue CI kicks off: full unit, integration, e2e. `main` has not changed yet.

### T+0:04 Bob clicks "Merge when ready"

Bob enters the queue behind Alice. GitHub creates `gh-readonly-queue/main/pr-502-<sha>` containing `main + Alice + Bob`. Queue CI runs in parallel with Alice's.

Key move: Bob's CI tests his code on top of Alice's, even though Alice hasn't merged. If Bob's refactor breaks Alice's new endpoint, we find out now.

### T+0:15 Alice's queue CI passes

GitHub fast-forwards `main` to include Alice. Deploy workflow triggers on `push: main`, builds `backend:sha-A`, pushes manifest. ArgoCD rolls out.

Deploy job uses:

```yaml
concurrency:
  group: deploy-backend
  cancel-in-progress: false
```

So this deploy runs to completion before any other backend deploy starts.

### T+0:18 Bob's queue CI passes

GitHub fast-forwards `main` to include Bob. Deploy workflow triggers, builds `backend:sha-B`, hits the `deploy-backend` concurrency group, waits for Alice's deploy.

### T+0:19 Alice's deploy completes

ArgoCD finishes rolling out `backend:sha-A`. Smoke tests pass. Bob's deploy proceeds.

### T+0:25 Bob's deploy completes

Cluster running `backend:sha-B` with both changes. Each commit got its own image, deploy, and smoke test signal. Clean audit trail.

## What breaks without the queue

Same scenario, direct merge to `main`:

- T+0:03: Alice merges. CI passed against old `main`. Deploy starts.
- T+0:04: Bob merges. CI passed against old `main` (didn't include Alice). `main` now has both.

If Alice's endpoint calls a helper Bob renamed, `main` is broken. Neither PR's CI caught it because neither tested the combined state. Whoever's deploy runs next fails, or worse, ships broken code. Everyone blocked until someone reverts.

## What breaks with cancel-in-progress and no queue

- T+0:03: Alice merges, deploy A starts.
- T+0:04: Bob merges. `cancel-in-progress: true` kills Alice's deploy. Bob's deploy builds `sha-B` from `main` (now has both) and deploys.

Code-wise this works because `sha-B` includes Alice's changes. But:

- Combined-state bugs only surface at Bob's smoke test, with both changes live.
- Alice's deploy shows "canceled," her commit never got its own deploy marker, her changes shipped under Bob's deploy in the audit trail.
- If Alice's CI was the only thing that would have caught the incompatibility, you skipped that signal entirely.

Concurrency groups handle deploy ordering after merges happen. They can't test combined state before merges happen. Only the queue does that.

## When to use it

Highest leverage on services where:

1. Multiple devs merge concurrently
1. CI is slow or expensive (broken `main` blocks everyone, re-runs cost real time)
1. Cross-cutting concerns exist (shared interfaces, shared types) where semantic conflicts are likely

Less worth it for low-traffic services owned by one team. The queue adds latency per merge, so it pays for itself only when concurrent PR activity is high enough that conflicts are realistic.

## Mental model

Concurrency groups make sure deploys happen in order. Merge queue makes sure the code being deployed was actually tested in the order it'll land. Different problems, both worth solving, but the queue solves the more dangerous one.

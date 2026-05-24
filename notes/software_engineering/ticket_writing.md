# Ticket Writing Guide

A well-written ticket is the difference between someone picking it up cold and shipping it in a day versus spending half a day reconstructing context the author already had. This guide covers what goes into a ticket and at what level of detail.

The same format applies to both stories and tasks. The structure is identical; the emphasis shifts based on ticket type.

## Mandatory Sections

Every ticket should include these three sections at minimum. Together they answer: what is the problem, where do we solve it, and what does done look like.

### Background

The goal is to make the ticket understandable to someone who wasn't in the conversation that spawned it.

What to include:

- The problem in business or user terms, briefly. One or two sentences. For stories, frame this in terms of who benefits and why. For tasks, frame it as what exists today and what needs to change.
- Why this matters now. Is it blocking another initiative? Is it tech debt that's finally biting? Did a stakeholder ask?
- Relevant history. Links to Slack threads, design docs, RFCs, related PRs, prior tickets. Not summaries, just links. The ticket is a hub.
- Any constraints that aren't obvious. "We can't change the public API shape because the mobile app is on a slow release cycle" is the kind of context that prevents wasted work.

What to leave out: company-wide context everyone already has, generic justification, anything that reads like it's there for completeness rather than utility.

Length: usually 3-6 sentences plus links. If it's longer than that, the ticket is probably too big.

### Technical Context

Roughly pointing at the right files saves the assignee an hour of grepping.

What to include:

- The primary file(s) or module(s) the work touches. Full paths, not vague references. `services/lead_intake/classifier/handler.go` not "the classifier."
- The pattern to follow if one exists. "This should mirror the structure of the XYZ sync in `services/sync/xyz/`" is enormously helpful.
- Schemas, models, or interfaces being modified. Paste the relevant struct or table definition inline if it's small.
- Upstream and downstream dependencies. "This dbt model feeds the `fct_engagement` mart" or "this endpoint is called by the mobile app's onboarding flow."
- Gotchas the author knows about. "Note that the Weather API rate-limits aggressively, see the retry logic in X" or "this table has a partial index that affects query plans."

What to leave out: line-by-line implementation. You want to orient, not dictate.

### Acceptance Criteria

The detail level scales with the work type, but every ticket needs AC that describes the intended outcome in testable terms.

For user-facing or behavioral work (typically stories), AC should be specific and testable. Given/When/Then or a numbered checklist both work:

- New purchases create a notification record within 5 minutes of submission
- Failed purchases emit a Datadog metric with the error reason

For technical or infra work (typically tasks), AC is more like a definition of done:

- Migration applied to staging and prod
- Backfill job completed for historical data
- Old column dropped after 2 weeks of dual-write
- Runbook updated with rollback procedure

For refactoring or cleanup:

- All call sites updated to use the new interface
- Tests pass with no behavior changes
- Old code path deleted

Each item should be something a reviewer or QA could verify without asking the author for clarification.

What to leave out:

- Restating the title as a criterion
- Internal implementation details unless they're a constraint
- "Code is clean and well-tested" type platitudes
- Anything covered by the team's general definition of done (CI passes, PR reviewed) unless it's specifically at risk

Length: usually 3-7 items. If you have 15, the ticket is too big.

## Optional Sections

Include these when they add clarity. Skip them when they don't.

### Implementation Ideas

Include when you have a clear approach in mind or have already considered and rejected alternatives. Mark them as suggestions, not requirements.

What to include:

- A sketch of the approach if you have one. Bullet points are fine.
- Alternatives considered and why they were rejected, if you actually thought about them. This prevents the assignee from re-litigating decisions.
- Known unknowns. "Not sure if we should use River or just a goroutine pool here, leaving to the assignee" is a useful signal.
- Sequencing if it matters.

The tone matters. "Here's how I'd approach this, but you should push back if you see a better way" produces better outcomes than "do exactly this." It also signals that the ticket author trusts the assignee.

Skip this section when the work is routine or when the implementation choice should clearly belong to the assignee.

### Out of Scope

Underrated section. A single line saying "not doing X in this ticket, that's covered in TICKET-456" prevents scope creep and saves arguments in review.

Use it whenever the work has natural adjacent things people might assume are included. Skip it when scope is obvious from the AC.

## Template

```
## Background
[2-4 sentences on the problem and why it matters]
[Links to related docs, threads, tickets]

## Technical context
[Primary files/modules]
[Patterns to follow]
[Relevant schemas or interfaces]
[Known gotchas]

## Acceptance criteria
- [Testable, observable item]
- [Testable, observable item]
- [Testable, observable item]

## Implementation ideas (optional)
[Bullet sketch, marked as suggestion]
[Alternatives considered, if any]

## Out of scope (optional)
- [Adjacent work not included]
```

## Calibrating Detail to Ticket Size

A 1-point ticket might be three lines total: "Bump the timeout from 5s to 30s in `services/foo/client.go`, see attached Datadog trace showing why." Forcing a full template here is waste.

A 5-point ticket should hit all three mandatory sections substantively. The investment in writing pays back many times over in clarity and reduced back-and-forth.

The signal that a ticket is well-written: someone unfamiliar with the work can read it, ask zero clarifying questions, and start making progress within 15 minutes of picking it up. If you regularly get questions on your tickets, the answers to those questions are what was missing.

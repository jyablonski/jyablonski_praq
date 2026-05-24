# Sprint Process

How the team plans, refines, reviews, and implements work. Work is broken down into tickets that should meet the bar described in the [ticket writing guidelines](./ticket_writing.md). The process is designed to balance upfront planning with flexibility and adaptability as work unfolds.

## Cadence Overview

Sprints run two weeks. The meeting cadence below assumes that rhythm.

| Meeting | Frequency | Duration |
| ------------------- | ---------------------------- | --------- |
| Standup | Daily | 10-15 min |
| Refinement | Every sprint | 45-60 min |
| Sprint planning | Every sprint | 60 min |
| Sprint demo | Every sprint | 45-60 min |
| Retro | Every other sprint (monthly) | 60 min |
| Chapter meeting | Bi-weekly | 30 min |
| EM 1:1 | Bi-weekly | 30 min |
| PM 1:1 | Monthly or as needed | 30 min |
| Peer 1:1s | Monthly or as needed | 30 min |
| Epic kickoff | Per epic, before work starts | 30 min |
| Architecture review | As needed | Variable |
| Quarterly planning | Quarterly | 60-90 min |

## Standup

10-15 min daily. Focus is coordination between engineers, not status reporting to the EM. Surface blockers, cross-cutting concerns, and overlaps. If standup consistently becomes a sequential report, restructure to focus on blockers only.

## Refinement

Once per sprint, 45-60 min. The team walks through tickets that need shared understanding before being picked up.

Rules:

- Only tickets with the `refinement` label are discussed. Curation is explicit.
- Tickets are drafted before the meeting (background, technical context, AC filled in).
- Author leads the walkthrough.
- Exit criteria: pointed, no unresolved questions, approach directionally agreed-on, dependencies identified.
- "Not yet" is a valid outcome. If a ticket needs a spike or more async work, name that and move on.

## Sprint Planning

60 min, first day of the new sprint. This is a selection and commitment exercise, not an authoring exercise.

Tickets entering the sprint should be well-written enough to be picked up without clarification. That doesn't require them to have gone through refinement: a clear ticket with solid background, technical context, and AC can go straight into planning even if no one but the author has seen it. Refinement is reserved for tickets that genuinely benefit from group discussion, not a mandatory gate for everything.

If planning consistently turns into authoring or major clarification, the issue is ticket quality upstream, not skipped refinement.

## Sprint Demo

45-60 min at the end of each sprint. Engineers volunteer what's worth showing; not every ticket needs a demo.

Don't force a demo if there's nothing visual to show. The point is celebrating progress and sharing learnings, not theatricality.

## Retro

Every other sprint (monthly), 60 min. Reviews what worked, what didn't, and where to improve.

Mandatory practices:

- Action items have named owners and target dates. "The team will improve X" is not an action item.
- Cap at 2-3 action items per retro. Follow-through matters more than volume.
- Open every retro by reviewing the previous retro's action items: done, in progress, dropped, deferred.
- Distinguish actions from observations. Not everything needs an owner.

## Epic Kickoff

30 min, scheduled 1-2 weeks before the first sprint of work on the epic. The buffer gives time for refinement, spikes, and clarifying questions before sprint commitment.

Attendees: the team doing the work, the PM, and 1-2 key stakeholders (requester, consuming team's tech lead). Keep it small enough to be a working meeting.

Agenda:

- What the project is about
- What value it brings to the business
- What our team is responsible for delivering
- The epic and a high-level walkthrough of the work
- Who the stakeholders are and who owns scope decisions
- Known risks and unknowns
- Success criteria at the epic level (what does "done and successful" look like)
- Dependencies on other teams or systems
- Target start and rough timeline (framed as estimate, not commitment)

Output: a written summary captured in the epic ticket. The meeting is the forcing function; the artifact is the lasting value.

Can optionally establish a recurring meeting cadence w/ the stakeholders or cross-functional engineering teams if needed.

Can optionally establish a shared Slack channel for communication + coordination if needed.

## Architecture Review

Convened as needed, not on a fixed schedule. A standing time block (e.g., Friday mornings) is held on calendars and used when someone schedules a session.

Mechanics:

- Requester writes a short doc (1-3 pages) covering context, options considered, recommendation, and the specific decisions they want input on.
- Intended outcome is stated up front: green light to proceed, feedback on tradeoffs, help thinking through options.
- Reviewer pool of 6-8 senior engineers across the org. Requester picks 2-4 most relevant for the topic.
- Decisions are captured in writing in the original doc after the meeting.

## Chapter Meetings

Bi-weekly, 30 min. Engineers from different squads in the same discipline (data, frontend, backend, quality) compare notes and discuss shared concerns.

Mechanics:

- Standing topic plus 1-2 rotating topics per session.
- Decisions or standards captured in writing somewhere durable.
- Clear charter on what decisions the chapter can make vs. what needs other forums.

## 1:1s

- EM 1:1: bi-weekly, 30 min. Weekly during onboarding or role transitions.
- PM 1:1: monthly or on-demand. Higher quality bar than forcing bi-weekly.
- Peer 1:1s: monthly for close collaborators, less frequent for occasional overlap. Treat as opt-in based on working relationships rather than blanket policy.

## Quarterly Planning

Scheduled 2-4 weeks before the current quarter ends. 60-90 min, 90 if there's significant scope debate or cross-cutting concerns.

Inputs gathered before the meeting:

- Engineers contribute a written list of what should be on the roadmap, what's technically risky, and what tech debt is becoming urgent.
- PM synthesizes and brings to the meeting.

Output: a written quarterly plan listing the epics planned, key milestones, and known risks. Becomes the reference for sprint planning throughout the quarter.

## Ticket Lifecycle

How a piece of work flows through the process:

1. Filed incrementally as it comes up, by whoever notices it. Rough is fine; context-while-fresh beats reconstruction later.
1. Refined when it approaches being worked. Author fills in background, technical context, and AC. Label `refinement` when ready for group discussion.
1. Discussed at refinement if it benefits from group input. Pointed and exit criteria met.
1. Selected at sprint planning from the pool of refined tickets.
1. Worked during the sprint.
1. Demoed at sprint end if there's something worth showing.

Epic-driven work follows the same flow but starts with a kickoff that produces the epic ticket and a rough breakdown. First sprint of tickets is refined in detail; later sprints are refined as they approach.

## Sprint Metrics

Two metrics worth tracking as diagnostic signals reviewed at retro. These are not performance targets and should not be tied to individual evaluation. They exist to start conversations about where the process is or isn't working.

### Sprint Stability

How much of the sprint was committed at the start vs. added mid-sprint.

Formula: (points committed at sprint start still in sprint) / (total points in sprint at end)

Targets depend on the team's work mix:

- Mostly planned project work: 85-90%
- Mixed planned and reactive: 70-80%
- Primarily reactive (platform, ops-heavy): 60-70%

Distinguish adds from swaps. A 5-point ticket pulled in to replace a 5-point ticket pulled out is different from 5 points added on top. Track both separately for a richer picture.

Below target: intake discipline is weak or priorities are shifting too often. Well above target (95%+) can also be a warning sign: either rigidly refusing legitimate urgent work, or under-committing so nothing needs to be added.

### Completion Rate

How much of what was committed actually shipped.

Formula: (points completed that were committed at sprint start) / (points committed at sprint start)

Only work present in the sprint at the start counts. Otherwise the metric becomes gameable by adding small tickets mid-sprint or pulling out large ones.

Healthy range: 80-90%. Below 70% consistently suggests over-commitment, underestimation, or too much disruption. Above 95% consistently suggests under-commitment or sandbagging.

### Reading the Two Together

| Stability | Completion | Diagnosis |
| --------- | ---------- | ---------------------------------------------------------------- |
| High | High | Healthy. Plans hold, work ships. |
| High | Low | Estimation problem. Plans hold but work is harder than expected. |
| Low | High | Reactive team handling churn well, or gaming via swaps. |
| Low | Low | Chaotic. Intake discipline, estimation, or both. |

### Tracking Notes

- Look at rolling 3-4 sprint averages, not individual sprints. Holidays, on-call, incidents, and sick days create noise.
- Track points completed and tickets completed separately. Shipping 90% of tickets but only 60% of points means the big ticket slipped; that's a different diagnosis than 60% of both.
- Completion rate punishes large tickets and rewards small ones. One more reason to split anything bigger than 5.
- Snapshot committed points at planning in a spreadsheet. Jira's built-in sprint reports can shift based on how tickets are added and removed.

## Health Signals

The process is working if:

- Tickets entering sprints are ready to be worked without clarification.
- Refinement spends time on the next 1-2 sprints, not long-term speculation.
- Retro action items consistently get done between retros.
- Engineers leave standup knowing something useful they didn't know going in.

The process needs attention if:

- Sprint planning is being used to author tickets.
- Refinement consistently runs over or has nothing meaningful to discuss.
- Retro action items pile up across multiple retros without resolution.
- Engineers are pinging ticket authors for clarification after sprint planning.

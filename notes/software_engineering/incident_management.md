# Incident Management

Strong incident management makes the right thing easy under pressure: detect meaningful harm, assemble the people who can mitigate it, communicate predictably, recover safely, and turn what happened into durable improvements. Keep the process lightweight enough that people actually use it.

## Readiness and on-call

Every production service or data product needs a named owner, a primary and secondary on-call rotation, an escalation path, and a short runbook linked from each actionable alert. Access, rollback procedures, dashboards, and contact lists should work before the incident starts.

- Page only for urgent, actionable, novel work. A job failure that can retry before its SLA is at risk is a ticket, not a page. Automate or remove recurring alerts with a known fix.
- Track page load and alert quality. As a rule of thumb, an on-call shift should have no more than about two actionable incidents; sustained excess is a reliability or staffing problem.
- Alert on user or data-product commitments: availability, latency, freshness, completeness, and correctness—not merely task exit codes.
- Treat silent bad data as a first-class failure mode. Use tests, reconciliations, anomaly detection, and lineage to find successful-but-wrong pipelines.
- Maintain a sustainable rotation. On-call should be a bounded part of a person's job, with compensation, backup coverage, and an explicit escalation route when the primary is unavailable.

Practice the system: run game days or tabletop exercises, test paging and access, and periodically rehearse common rollbacks, regional failures, data restatements, and security escalation paths.

## Declare and run the incident

Declare early; downgrade freely. The costly failure mode is a responder trying to solve a cross-team problem alone for hours. Create an incident channel and record immediately: severity, incident commander (IC), current impact, start time, and next update time.

Use incident-command roles, scaled to the event:

- **IC:** owns coordination, priorities, and decisions; delegates and generally does not debug.
- **Operations lead:** investigates and makes approved changes.
- **Comms lead / scribe:** maintains the timeline and sends updates. On small incidents, one person can hold multiple roles.

The operating loop is simple: assess impact, mitigate, verify recovery, then investigate and permanently fix. Prefer reversible mitigation—rollback, disable a risky path, shed load, or fail over—over an untested forward fix. Pause nonessential changes when they could complicate recovery. Preserve useful evidence (logs, dashboards, deploy IDs, and relevant queries) as you go; do not let evidence collection block mitigation.

| Sev | Shape | Default response |
| ---- | -------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| SEV1 | Broad outage; material data loss/corruption; security or privacy exposure; major revenue or contractual impact | Page responders, use a dedicated channel and fixed update cadence, involve incident/security/legal/executive contacts as applicable, and write a postmortem. |
| SEV2 | Significant degradation or a material subset of consumers affected; workaround exists | Page the owning team, coordinate in a channel, notify affected stakeholders, and write a postmortem. |
| SEV3 | Contained issue with low urgency and no meaningful external impact | Track in normal work; send only targeted communication; postmortem is optional. |

Severity definitions should use concrete examples from the team's own systems. Any actual or suspected security, privacy, or regulated-data exposure follows the security incident process immediately; do not investigate or notify externally without the designated security/legal owners.

## Communication and recovery

Communicate impact, mitigation status, and the time of the next update—not speculation. During a SEV1, update on a fixed cadence (for example, every 30 minutes), including when there is no material change. This prevents stakeholders from interrupting responders for status.

Use a single source of truth: the incident channel plus a status page or stakeholder update appropriate to the audience. Set one owner for external communications and distinguish confirmed facts from estimates. If data that people may have used will change, notify the affected consumers; silently backfilling a published metric erodes trust.

Do not close an incident just because the immediate symptom disappeared. Confirm the service or data product meets its commitment, queues and backfills are healthy, and corrections have been reconciled. State any residual risk, monitoring period, customer follow-up, and owner before closing. Hand off explicitly if recovery spans shifts.

An issue is an incident when a commitment is breached or plausibly at risk; data is lost, corrupted, exposed, or used for a decision; someone outside the team noticed or could have; or it needs unplanned cross-team coordination. It is a quiet fix only when caught before impact, with no breached commitment and no unusual coordination.

## Postmortems and follow-through

Write a blameless postmortem for every SEV1/SEV2, data loss or corruption, security/privacy event, repeat incident, detection by a human rather than monitoring, significant near miss, or event that someone asks to review. The question is not who made a mistake; it is how the system made the action reasonable and allowed the impact to reach users.

Avoid forcing a single "root cause" onto a complex system. Document contributing factors and conditions instead. A useful postmortem contains:

- A plain-language summary and quantified impact: duration, affected users/data products, decisions made on incorrect data, and SLO/error-budget effect.
- A timeline captured during the incident, including detection, declaration, mitigation, recovery, and communications.
- Detection quality: how the issue was found and how long detection and mitigation each took.
- Contributing factors; what went well, poorly, and luckily; and any follow-up communication or correction required.
- Action items as real backlog tickets, each with one owner, priority, and due date.

Review the postmortem within a week with responders and affected stakeholders. Track completion of action items—especially reliability work—with the same rigor as feature delivery. Repeating incidents or overdue high-priority actions should escalate through engineering leadership, not disappear into a document.

## Operating cadence and measures

- **Each handoff:** open risks, noisy alerts, pending mitigations, and explicit ownership.
- **Weekly:** recent incidents, overdue actions, alert quality, and page load.
- **Quarterly:** SLOs and error budgets; time to detect, mitigate, and fully resolve; monitoring-detected percentage; repeat rate; data-quality escapes; and pages per person.

Error budgets give SLOs teeth: when a product exhausts its budget, leadership explicitly trades feature velocity for reliability until it recovers. The exact policy can vary, but an unenforced SLO is only a dashboard.

## Minimum viable playbook

Keep the main playbook to a few pages and link deeper runbooks. It needs only:

1. Product owners, on-call/escalation contacts, and severity examples.
1. How to declare, assign roles, create the incident record, and escalate security/privacy concerns.
1. Communication templates, audiences, cadence, and status-page authority.
1. Mitigation, rollback, recovery-validation, handoff, and closure checklists.
1. Postmortem triggers, template, action-item expectations, and review cadence.

Let real incidents refine the document. Its job is to remove avoidable judgment at 2am, not to become a manual nobody reads.

# Documentation Strategy

## Why does Documentation Matter

Documentation is the written record of how and why a system works — for the people who build it, operate it, and depend on it. Without it, knowledge lives in individual heads and Slack threads, both of which are ephemeral. People leave, context fades, and channels get archived. Documentation externalizes that knowledge into something durable, searchable, and transferable. It reduces onboarding time, eliminates repeated questions, creates accountability around commitments like SLAs, and gives on-call engineers a fighting chance at 2am when they're debugging a service they didn't build. The cost of writing documentation is always lower than the cost of not having it when you need it.

## Why Establish a Documentation Flow

Having a clear framework for what goes where eliminates the most common failure mode: documentation that exists but nobody can find. When there's no established flow, teams default to wherever feels convenient — a random Confluence page, a Google Doc shared in a thread, a README that tries to serve five audiences at once. The result is scattered, inconsistent, and quickly abandoned. A defined flow gives every author a decision path ("who is this for?" leads directly to "where does it go") and gives every reader a predictable place to look.

Templates reinforce this further. They lower the activation energy to write documentation by removing the blank-page problem, and they ensure critical sections aren't skipped because the author didn't think of them. But they should only exist for document types that are created repeatedly — runbooks, service overviews, ADRs, business workflows. Templating a one-off doc adds process without value.

This standardization also matters for LLMs. As teams increasingly use AI tooling to draft, summarize, and query documentation, consistent structure makes that tooling dramatically more effective. An LLM can reliably extract escalation paths from runbooks, summarize service dependencies, or draft an ADR — but only if those documents follow a predictable format. Inconsistent documentation forces manual interpretation regardless of whether the reader is a person or a model. Standardization is an investment that compounds across both human and machine consumers.

## Overview

Documentation is routed by its primary audience. Each layer has a clear purpose, a distinct consumer, and a natural home. The system works through disciplined linking between layers rather than duplication.

There are three documentation layers:

1. **Google Site** — business-facing, non-technical
1. **Internal Tech Doc Site** — engineering-facing, git-backed, cross-service
1. **Git Repo** — developer-facing, service-specific, operational

## Google Site

**Audience:** Product managers, business stakeholders, leadership.

**Purpose:** Communicate what the system does in domain language. No implementation details. This is where stakeholders go to understand workflows, SLAs, and outcomes without needing to know how anything is built.

**What belongs here:**

- Business workflow descriptions (e.g., churn prevention, onboarding flows)
- SLA definitions and commitments
- Stakeholder FAQs
- Status dashboards or links to them
- Contact points and escalation paths for business questions

**Ownership:** Not git-backed. Editable in place by a designated subset of contributors (PMs, team leads). Each page should have an explicit owner responsible for keeping it current, reviewed quarterly or when the workflow changes materially.

**Linking:** Each business workflow page links to its corresponding technical workflow page on the tech doc site for anyone who wants to go deeper.

______________________________________________________________________

## Internal Tech Doc Site

**Audience:** Engineers, technical managers, and anyone navigating the broader system.

**Purpose:** Answer big-picture engineering questions. How services fit together, why architectural decisions were made, how on-call works, and what platform-level conventions exist. This is the engineering backbone — git-backed, reviewed through PRs, and enforced through CI.

**What belongs here:**

- Service overviews (one per service, acting as a catalog entry)
- Architecture Decision Records (ADRs)
- Technical workflow documentation (implementation details of business workflows)
- On-call process and philosophy (org-wide)
- Platform engineering guides and conventions
- Cross-cutting concerns (CI/CD philosophy, shared library usage, observability standards)

**Ownership:** Git-backed. Changes go through pull request review. Discoverability is critical — use a service catalog pattern, strong sidebar organization, or a search index. If engineers can't find what they need in under 30 seconds, they stop trusting the site and ask in Slack instead.

**Linking:** Service overviews link to the corresponding repo for runbooks and contribution guides. Technical workflow pages link to the corresponding business workflow page on the Google Site. ADRs link to relevant service overviews or other ADRs they supersede.

______________________________________________________________________

## Git Repo

**Audience:** Developers actively working on or operating a specific service.

**Purpose:** Answer operational questions scoped to this service. How to set it up, how to contribute, and how to respond when it breaks. Lives alongside the code so it versions with it and benefits from the PR review cycle.

**What belongs here:**

- `CONTRIBUTING.md` or `docs/contributing.md` — local dev setup, test commands, PR conventions, deploy process
- `docs/runbooks/` — on-call runbooks for this service's alerts and failure modes
- `README.md` — minimal orientation pointing to the tech doc site for broader context

**Ownership:** Maintained by the team that owns the service. Runbooks are updated in the same PR as the fix whenever a novel incident reveals a new resolution path.

**Linking:** The README links to the service overview on the tech doc site. Runbooks reference relevant dashboards and alert definitions.

______________________________________________________________________

## Templates

- **Runbook template** — for documenting on-call procedures and alert resolution steps.
- **Service overview template** — for cataloging each service, its purpose, and its key
- **Business workflow template** — for describing workflows in domain language, including SLAs and outcomes.
- **ADR template** — for documenting architectural decisions, their context, and their consequences.

## Principles

**Route by audience.** Business stakeholders go to the Google Site. Engineers navigating the system go to the tech doc site. Developers working on a specific service go to the repo.

**Link, don't duplicate.** Each layer points to the others where context is needed. SLA numbers live in one place. Architecture decisions live in one place. If you're copying content between layers, something is scoped wrong.

**Templates enforce consistency.** They exist for document types that are created repeatedly — runbooks, service overviews, ADRs, workflows. Don't template one-off documents.

**Ownership prevents rot.** Every page has an owner. Google Site pages are reviewed on a cadence. Tech doc site pages are reviewed through PRs. Repo docs are updated alongside the code they describe.

# The proposal in brief

**Goal:** define business metrics once in Snowflake semantic views and reuse them in Sigma and a ChatGPT Analytics plugin. Dashboard and chat answers should agree; that consistency must be demonstrated before rollout.

**Expected value:** let stakeholders answer routine business questions in plain language while reducing duplicated metric definitions and reliance on custom analyst queries.

**Architecture:** ChatGPT uses each person's OAuth sign-in to call one Snowflake-hosted MCP endpoint exposing an `analytics` tool. A shared Cortex Agent uses domain-specific Analyst tools to generate SQL and executes it with the caller's permissions. Sigma queries the semantic views directly.

**Access model:** Snowflake roles determine which data each person can retrieve. Consumers share the endpoint, Agent, and OAuth client registration; their personal identity and role determine access.

- The POC defines sales-only, customers-only, and all-domains roles; the combined role inherits both domain roles.
- The Agent skips inaccessible domain views and returns warnings. ChatGPT must preserve those limitations and avoid guessed answers.

**Scaling:** new metrics extend existing definitions; new domains add semantic views, Agent tools, and grants. Additional Agents or MCP endpoints are introduced when ownership, security boundaries, or measured routing quality require separation.

**Reference design:** use a Snowflake-managed MCP endpoint with sales and customers as example domains. Adapt the definitions, role assignments, and workspace configuration to the target environment.

**Decisions before rollout:**

- **G1 — Data boundary:** may consumers read approved underlying data, or must access be limited to named metrics? The managed Agent path requires source-data permissions.
- **G2 — User experience:** does the target ChatGPT workspace support ordinary-user plugin distribution, personal OAuth, and accurate access warnings?

**Pilot:** dummy-data access checks → a certified sales question set → prove release, support, and acceptable cost → expand one domain at a time. [Suggested execution plan](pilot_suggestions.md)

**Status as of 2026-10-24:** the minimum personal POC passed its three-role ChatGPT matrix using a separate SQL deployment on a Snowflake trial. All-access answers matched the fixtures: USD 1,000 September revenue, USD 2,000 total revenue, and six registered customers. Sales-only returned both revenue figures and preserved the customer-access limitation; the user also confirmed customers-only returned six customers while sales remained unavailable. These are manual, single-user trial results; separate-user identity isolation, Sigma parity, cost, and stakeholder rollout remain unproven. [Observed results and optional follow-ups](pilot_suggestions.md#observed-personal-trial-results-2026-10-24)

Terraform validation and nine mocked checks pass; the Terraform stack itself has not been deployed. The runnable SQL path is [setup](setup_poc.sql) → [verification](verify_poc.sql) → [ChatGPT OAuth](connect_chatgpt.sql).

**Further detail:** [Design summary](investigation_spike_summary.md) · [Roles and permissioning](roles_and_permissioning.md) · [Supporting investigation](investigation_spike_details.md) · [Terraform POC](analytics_mcp_poc.tf)

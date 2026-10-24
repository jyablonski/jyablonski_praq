# Suggested analytics pilot

**Recommendation:** prove the connection and authorization model with dummy data, then certify a bounded sales workflow before adding real customer coverage. This is a proposed sequence and set of acceptance criteria, not an executed deployment or agreed SLA.

The [summary](investigation_spike_summary.md) explains the proposal; the [investigation](investigation_spike.md) records design constraints and supporting sources. This document owns setup, validation, and rollout suggestions.

**Current evidence:** the [Terraform POC](analytics_mcp_poc.tf) and saved [mocked-plan checks](analytics_mcp_poc.tftest.hcl) pass locally. This reference implementation uses a Snowflake-managed MCP endpoint with sales and customers as example domains. It has not been deployed, and no live OAuth, authorization, or answer-quality checks have run for these examples.

## Proposed sequence

| Stage | Question to settle | Owner |
| --- | --- | --- |
| 1. Prepare an isolated environment | Are fixtures, effective grants, spend controls, and dependency requests ready? | Data Platform + IT/Security |
| 2. Prove the smallest connection | Can an ordinary workspace user authorize personally and invoke the Agent with MCP `USAGE`? | Data Platform + ChatGPT admins |
| 3. Establish authorization and source exposure | Do the three access levels work, and is required source access acceptable? | Data Platform + Security + Product |
| 4. Certify sales answers | Do reference SQL, Sigma, the Agent, and ChatGPT agree under matching conditions? | Analytics + domain steward |
| 5. Establish operation and adoption | Can the team release, support, revoke, and afford the workflow? | Data Platform + IT + Product |

## 1. Prepare and reproduce the local checks

Use a non-production environment with two externally created dummy semantic views and separate source relations. Seed data with independently calculable results and obvious domain differences. The POC creates one control schema, one shared Agent with two Analyst tools, one MCP exposing `analytics`, one OAuth client integration, and three consumer roles. It does not create the database, warehouse, views, sources, or users.

Use three **dedicated non-production Snowflake users**. Changing the default role of an existing engineer or stakeholder can affect unrelated workflows. Review inherited roles, `PUBLIC`, direct grants, future grants, source dependencies, and row/masking policies before interpreting any denial or success.

Start the following work alongside stages 1–3. Record what is required for the isolated experiment and what must be resolved before real-data access or stakeholder rollout.

| Dependency | Action and owner | Needed by |
| --- | --- | --- |
| Sigma reference workbook | Analytics selects a representative workbook using the shared semantic definitions as the comparison baseline. | Numeric comparison in stage 4 |
| ChatGPT workspace | Admins confirm plugin distribution to ordinary users, MCP/action permissions, and Lockdown restrictions. | First ChatGPT call in stage 2 |
| Managed MCP operations | Data Platform + Platform Engineering name operating/audit owners for the Snowflake-managed endpoint. | Managed-endpoint use |
| Data handling | Security + data owners agree permitted questions, results, traces, retention, and model/region settings. | Before sending the relevant data across systems |

### Spend controls before the first live call

The warehouse owner provides a dedicated, appropriately sized warehouse with auto-suspend and a resource monitor with alert/suspension actions. The AI administrator configures an Agent resource budget with an explicit response at its thresholds, plus per-user blocking quotas for supported AI usage where available. Record owners, thresholds, scope, and evidence that actions work; these controls are prerequisites supplied outside the minimal Terraform stack. [Warehouse controls][sf-monitors], [Agent budgets][sf-budgets], [AI quotas][sf-quotas]

These are delayed controls: Agent budget actions can lag by up to eight hours, or two with latency optimization, and quota enforcement operates within minutes. Allow headroom, bound the test volume/concurrency, and name an operator who can disable the integration. A warehouse monitor does not cover AI spend. CoWork comparisons need CoWork budget coverage because Agent-only budgets do not capture CoWork-initiated requests. [Enforcement and attribution][sf-budgets]

### Local checks

`PUBLIC` may inherit `SNOWFLAKE.CORTEX_USER`. That provides feature entitlement, not access to this Agent or its data. Audit its actual grants; do not automatically revoke an account-wide entitlement as part of this setup. An Agent-only feature-entitlement check would require a separately controlled environment. [Feature and object access][sf-access]

The configuration requires **Terraform 1.11+**, which introduced the tests' `override_during = plan` support. The local reproduction environment is **Terraform 1.15.9** with **Snowflake provider 2.22.0**. From this directory: [Version requirement][tf-1-11]

```sh
terraform fmt -check analytics_mcp_poc.tf analytics_mcp_poc.tftest.hcl
terraform init -backend=false
terraform validate -no-color
terraform test -filter=analytics_mcp_poc.tftest.hcl -no-color
```

The saved checks cover role/resource grants, user assignments/inheritance, MCP annotations, separate domain parents/source types, invalid inputs, and refresh-token lifetime boundaries. Every run uses a mocked provider and `command = plan`; these commands do not deploy resources or prove Snowflake authorization. [Terraform mocking][tf-mocking]

## 2. Prove the smallest live connection

Configure the POC inputs before reviewing a plan for the isolated environment:

| Input | Required choice |
| --- | --- |
| `database_name`, `warehouse_name`, `snowflake_account_url` | Existing non-production locations and the public account URL. |
| `semantic_views`, `domain_sources` | Exact view names and all required source dependencies, grouped by domain. Replace the dummy defaults together. |
| `poc_user_names` | The three dedicated existing identities: sales-only, customers-only, and all-domains. |
| `chatgpt_redirect_uri` | Exact callback displayed by the intended ChatGPT connection. |
| `oauth_refresh_token_validity_seconds` | Deliberate lifetime; default 86,400 seconds requires renewed authorization after 24 hours. |

The provisioning identity needs creation and grant authority. Confirm the MCP schema uses Snowflake OAuth and applicable network policies permit the ChatGPT backend. After reviewing and applying the plan, complete the handoff:

1. Have the identity owner capture existing user defaults, then review and execute the `poc_user_defaults_sql` output for the dedicated users. Terraform does not execute it or take ownership of SCIM user configuration.
1. Obtain the MCP URL from `chatgpt_connection`. Retrieve the integration's generated client ID/secret in a protected Snowflake admin session using `SYSTEM$SHOW_OAUTH_CLIENT_SECRETS('CHATGPT_ANALYTICS_POC')`; enter them directly into ChatGPT's OAuth settings without copying values into Terraform outputs, state lookups, or routine logs.
1. Have workspace admins create/distribute the Analytics plugin and enable its MCP capabilities for the intended audience. Prove installation and use as a regular user with the actual Lockdown/action settings. Inspect the discovered `readOnlyHint: true` annotation and observe approval behavior in a fresh conversation and after refresh. Hints do not override workspace policy or Snowflake grants. [Client setup][oai-client]
1. Connect one dedicated user personally and invoke one known-answer question. Verify the effective primary role, usable warehouse, OAuth role allowlist, disabled secondary roles, and `OAUTH_ANY_ROLE_MODE = DISABLE`. The default `session:role:all` uses the user's default role, not every assigned role. [Snowflake connection behavior][sf-mcp]
1. Verify `tools/list` and `tools/call` with MCP `USAGE` and no `MODIFY`. The privilege reference explicitly permits invocation under `USAGE`; the MCP guide is inconsistent. If a call fails, capture the sanitized error and effective grants for investigation/support rather than broadening consumer management privileges. [Privilege reference][sf-privileges]

Verify verified-domain restrictions separately if they are a rollout requirement. OpenAI requires OIDC discovery, `openid`/`email` scopes, and verified-email UserInfo support. Snowflake OAuth compatibility remains unverified; plugin audience settings do not establish this control. [Requirements][oai-domain]

### Stop points

| Finding | Pause and decision |
| --- | --- |
| MCP invocation remains denied after checking effective grants and prerequisites. | Pause that connection path; capture the error and resolve it with Snowflake/support. Do not add consumer `MODIFY` as a workaround. |
| Ordinary users cannot install or use the plugin under the intended workspace settings. | Pause ChatGPT rollout; workspace admins resolve distribution or Product chooses another supported frontend. |
| Required source exposure exceeds the approved data contract. | Pause managed-Agent expansion; Product/Security decide whether narrower sources are sufficient or constrained semantic-SQL execution is required. |

Continue independent definition and compatibility work while a path is paused. Do not send real data before its required handling decision or start live traffic before spend controls are ready.

## 3. Run the authorization and source-access checks

### Additional fixture setup

Data Platform creates the following two roles through reviewed Snowflake SQL using the provisioning identity. They are manual test fixtures outside Terraform. IT provisions a fourth dedicated user, assigns both fixture roles, captures its prior defaults, and sets its default role to `ROLE_MCP_ONLY_ANALYTICS_POC` with the dedicated warehouse. Neither fixture role inherits a normal consumer role. [Grant categories][sf-privileges]

| Fixture role | Explicit grants | Deliberately absent |
| --- | --- | --- |
| `ROLE_MCP_ONLY_ANALYTICS_POC` | `SNOWFLAKE.CORTEX_AGENT_USER`; database/control-schema and warehouse `USAGE`; `USAGE` on `ANALYTICS_MCP_POC`. | Agent `USAGE`, view/source `SELECT` |
| `ROLE_VIEW_ONLY_ANALYTICS_POC` | `SNOWFLAKE.CORTEX_AGENT_USER`; database/control-schema/view-schema/source-schema and warehouse `USAGE`; Agent `USAGE`; sales semantic-view `SELECT`. | Source `SELECT`, customers view `SELECT`, MCP access |

Use the fully qualified objects from the Terraform inputs/output, including source-schema `USAGE` for G1. Do not grant source `SELECT` to the view-only role during its initial test. IT audits other grants and `PUBLIC`; the fixture names alone do not establish their effective isolation.

For the MCP-only test, Data Platform temporarily extends the existing integration's primary-role allowlist through SQL. Keep the three original roles and add only the MCP-only fixture role:

```sql
ALTER SECURITY INTEGRATION CHATGPT_ANALYTICS_POC
  SET ALLOWED_ROLES_LIST = (
    'ROLE_SALES_ANALYTICS_POC',
    'ROLE_CUSTOMERS_ANALYTICS_POC',
    'ROLE_ALL_ANALYTICS_POC',
    'ROLE_MCP_ONLY_ANALYTICS_POC'
  );
```

Record this temporary Terraform drift and avoid concurrent applies during the test. Connect the fourth user personally with its MCP-only default role and secondary roles disabled. After the negative test, restore the allowlist to the original three roles and remove that user's test authorization. An OAuth rejection before invocation is not evidence of an Agent denial.

Run G1 directly in a Snowflake SQL session as the fourth user: activate `ROLE_VIEW_ONLY_ANALYTICS_POC`, use `USE SECONDARY ROLES NONE`, and invoke the configured Agent with `SNOWFLAKE.CORTEX.DATA_AGENT_RUN`. No additional OAuth client or allowlist entry is needed for this SQL path. It isolates backend source requirements; the three-user matrix separately exercises ChatGPT identity propagation. [Agent SQL execution][sf-agent-sql]

### Expected outcomes

Use the same MCP URL, OAuth integration, and `analytics` tool for all three personal connections:

| Identity | Sales question | Customers question |
| --- | --- | --- |
| Sales-only | Known answer | No customers result; access limitation preserved |
| Customers-only | No sales result; access limitation preserved | Known answer |
| All domains | Known answer | Known answer |
| Additional MCP-only negative-test role, with no effective Agent `USAGE` | Cannot invoke the Agent | Cannot invoke the Agent |

For each role, verify direct denied view/source queries, actual generated SQL, and cross-domain follow-ups. Tool discovery is not a domain-access list. Access to both domains does not certify cross-domain joins or compatible populations.

For skipped views, assert warning code `399569`; inspect `response.warning` events or the non-streaming top-level `warnings` array. Test missing and unauthorized resources separately: their warning text is intentionally indistinguishable. Then verify that ChatGPT preserves the limitation without guessing a number or substituting another domain. [Warnings][sf-partial]

**Resolve G1 explicitly:** with the view-only fixture, demonstrate direct semantic SQL with view access and denied direct source SQL, then try the Agent. Data Platform can subsequently add the exact proposed source grants to that fixture for the approved comparison; record newly readable fields/rows, including direct reads outside ChatGPT, and remove the added grants afterwards. The setup and best-practices docs disagree; the POC conservatively grants exact source `SELECT`. Apply the source-exposure stop point if the result conflicts with the product contract. [Source requirements][sf-best], [Setup requirements][sf-access]

Exercise row-access/masking policies with actual caller sessions, plus unmodeled fields, unrelated data, raw SQL requests, prompt injection, and cross-domain leakage. A broader evaluation identity can conceal consumer failures.

## 4. Certify a bounded sales workflow

Start with about 30 analyst-reviewed cases, covering counts, groupings, dates/history, rates, ambiguity, follow-ups, and unsupported requests. Agree entity/grain, order-status meaning, absolute date boundaries/timezone, exclusions, history, and freshness before assigning expected results. Run representative prompts more than once to expose variation.

Compare an independent reference calculation, Sigma, the Agent result, and ChatGPT's final answer under matching filters, visibility, and source snapshot. Require exact counts and agreed tolerances for other numeric types; investigate every unexplained mismatch. Validate units, scope, qualifications, and freshness statements as well as numbers.

Use the Sigma sales workbook as the comparison baseline. Check metrics, permissions, filters, and data snapshots against that baseline; consult the [documented Sigma limitations][sigma-sv] when selecting or extending it. Keep any existing workbook available throughout migration.

Include zero versus empty results, stale sources, missing grants/resources, query failures, warehouse suspension, timeout, quota exhaustion, and partial answers. Native Agent evaluations can help diagnosis, but tests involving session attributes or policies need actual user sessions. [Evaluation limits][sf-evaluations]

## 5. Establish lifecycle, release, and support

| Area | Evidence to collect |
| --- | --- |
| Authentication lifecycle | Initial login, access-token refresh, refresh-token expiry, reconnection after role/default changes, and revocation with an existing conversation plus a new session. Record actual SSO friction rather than assuming daily password entry. [Token lifecycle][sf-oauth] |
| Release and rollback | A second deployment preserves definitions, policies, grants, verified queries, and the intended serving Agent version. Demonstrate the reviewed SQL promotion/rollback step because the native Terraform Agent resource does not manage version promotion. |
| Traceability and support | Correlate a ChatGPT answer with its effective identity, Agent run, generated SQL/query IDs, configured views, and version. Exercise a wrong-answer report, failed login, domain disable, and cost stop with named owners. |
| Economics | Measure p50/p95 latency, cost per successful answer, cold warehouses, retries, longer conversations, and expected concurrency. The POC's 60-second/8,000-token orchestration budget and 30-second query timeout are starting settings. Agree targets from measurements. |
| Operating boundary | Use the Snowflake-managed MCP endpoint; finalize operating/audit owners and the data-handling details started in stage 1, including payloads, retention, network/model/region settings, and support responsibilities. |

Use the same Agent in Snowflake CoWork as an optional comparison to isolate backend behavior from ChatGPT integration and assess stakeholder preference. This can remove the ChatGPT hop; it does not resolve source permissions or establish a blanket data-residency guarantee. [Native frontend][sf-cowork]

## Cleanup

Assign cleanup owners before deployment and perform this sequence after the experiment or on cancellation:

1. **Data Platform + workspace admins:** disable the integration/entry point to stop new calls, stop active work where supported, and retain sanitized evidence and final usage records. Disconnect test connections and remove the ChatGPT plugin and its stored client credentials.
1. **IT/identity owner:** revoke all test users' OAuth authorizations with `ALTER USER ... REMOVE DELEGATED AUTHORIZATIONS FROM SECURITY INTEGRATION ...` and verify new retrieval is denied. Restore captured defaults and remove temporary fixture-role assignments. [Consent revocation][sf-consent]
1. **Data Platform:** restore any temporary allowlist/source-grant changes, then drop the two manual fixture roles. Inventory separate budget/tag/action resources with the AI administrator; remove experiment-only controls while preserving shared controls.
1. **Terraform owner:** review `terraform plan -destroy`, then execute `terraform destroy` against the isolated POC state. This removes the Terraform-owned integration, roles/grants, Agent, MCP, and control schema. Check the plan before execution; the database, warehouse, semantic views, sources, and users are externally owned and must be handled separately if their owners intend to retire them.
1. **Owners:** verify the endpoint and personal connections no longer retrieve data and that experiment compute has stopped. IT retires experiment-only identities through their provisioning owner after grant cleanup. Removing infrastructure does not erase previously returned chat content; apply the agreed retention process to that content and retained evidence.

Terraform does not undo SQL emitted by `poc_user_defaults_sql`, manual fixture grants, or workspace configuration. Keep the inventory and completion evidence with the experiment record.

## Completion and expansion

The pilot passes when the agreed questions produce accurate, understandable answers; denied domains remain inaccessible; required warnings survive the full path; source exposure and workspace behavior meet the agreed contract; and release, revocation, support, and measured economics are acceptable to the named owners. These are suggested criteria, not results.

Keep reproducible evidence with the implementation review: date/environment, effective identity, configuration/version, question, expected and actual result, query/run IDs, sanitized failures, and the resulting decision. Resolve the G1/G2 gates and record the selected Sigma workflow and managed-MCP configuration. Add real customer coverage only after sales passes; repeat authorization, parity, and operating checks for each additional domain.

[oai-client]: https://developers.openai.com/api/docs/guides/custom-mcp-server
[oai-domain]: https://developers.openai.com/plugins/build/auth#support-workspace-domain-restrictions
[sf-access]: https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents-setup
[sf-agent-sql]: https://docs.snowflake.com/en/sql-reference/functions/data_agent_run-snowflake-cortex
[sf-best]: https://docs.snowflake.com/en/user-guide/views-semantic/best-practices-dev
[sf-budgets]: https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents-resource-budgets
[sf-consent]: https://docs.snowflake.com/en/user-guide/oauth-consent
[sf-cowork]: https://docs.snowflake.com/en/user-guide/snowflake-cortex/snowflake-cowork
[sf-evaluations]: https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents-evaluations
[sf-mcp]: https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents-mcp
[sf-monitors]: https://docs.snowflake.com/en/user-guide/resource-monitors
[sf-oauth]: https://docs.snowflake.com/en/sql-reference/sql/alter-security-integration-oauth-snowflake
[sf-partial]: https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents-inaccessible-tool-handling
[sf-privileges]: https://docs.snowflake.com/en/user-guide/security-access-control-privileges
[sf-quotas]: https://docs.snowflake.com/en/user-guide/budgets/per-user-quotas
[sigma-sv]: https://help.sigmacomputing.com/docs/query-and-extend-snowflake-semantic-views-in-sigma
[tf-1-11]: https://github.com/hashicorp/terraform/blob/v1.11.0/CHANGELOG.md
[tf-mocking]: https://developer.hashicorp.com/terraform/language/tests/mocking

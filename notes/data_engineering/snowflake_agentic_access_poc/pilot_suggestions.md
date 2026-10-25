# Suggested analytics pilot

**Recommendation:** prove the connection and authorization model with dummy data, then certify a bounded sales workflow before adding real customer coverage. The stakeholder rollout stages remain a proposed sequence and set of acceptance criteria; the personal trial results below record what has actually been observed.

The [summary](investigation_spike_summary.md) explains the proposal; the [investigation](investigation_spike_details.md) records design constraints and supporting sources. This document owns setup, observed results, validation, and rollout suggestions.

The separate [roles and permissioning guide](roles_and_permissioning.md) owns the proposed Okta role hierarchy, audience membership, OAuth profile-selection policy, and access-change procedures for stakeholder rollout.

**Current evidence:** the [Terraform POC](analytics_mcp_poc.tf) and saved [mocked-plan checks](analytics_mcp_poc.tftest.hcl) pass locally. This reference implementation uses a Snowflake-managed MCP endpoint with sales and customers as example domains. The Terraform stack has not been deployed.

## Observed personal trial results (2026-10-24)

The user reported successfully running the [SQL setup](setup_poc.sql) and active [verification queries](verify_poc.sql), then connecting a personal ChatGPT plugin through [custom OAuth](connect_chatgpt.sql). The setup creates `AGENTIC_ACCESS_POC`, an X-Small warehouse, 12 dummy orders, six customers, two semantic views, three consumer roles assigned to one trial user, one shared Agent with two Analyst tools, and one MCP endpoint exposing `analytics`. This is a separate SQL deployment; the Terraform stack remains undeployed. Both paths use the same account-role and integration names, so choose one owner for those objects.

| OAuth primary role under test | September completed revenue | All-fixture completed revenue | Registered customers | Evidence/status |
| --- | --- | --- | --- | --- |
| `ROLE_ALL_ANALYTICS_POC` | USD 1,000 | USD 2,000 | 6 | ChatGPT screenshot matches all three fixture answers and explains exclusions/populations. |
| `ROLE_SALES_ANALYTICS_POC` | USD 1,000 | USD 2,000 | Unavailable with current role | User confirmed the result after the role-change/reconnection workflow. The screenshot names `AGENTIC_ACCESS_POC.POC_DATA.SV_CUSTOMERS` as inaccessible. |
| `ROLE_CUSTOMERS_ANALYTICS_POC` | Unavailable | Unavailable | 6 | User confirmed this result in a fresh connection and chat. A subsequent screenshot shows the same results and identifies `ROLE_CUSTOMERS_ANALYTICS_POC` as the current role and `SV_SALES` as inaccessible. |

The sales-only response continued answering permitted questions and preserved the customer-access limitation without substituting sales data or guessing a customer count. It also exposed the denied view's name, so data isolation does not imply hidden resource metadata. The all-access and sales-only screenshots show 57s and 45s of displayed ChatGPT work time respectively; these are individual UI observations, not per-query timings or a latency benchmark.

Evidence is based on the user's execution report and chat screenshots. The repository review did not execute live Snowflake calls, and raw tool payloads, warning code `399569`, query/run IDs, cost, and a complete effective-grant audit have not been captured. The trial validates selected fixture answers and both directions of partial access for one user across fresh OAuth connections; it does not establish separate-user isolation, Sigma parity, or stakeholder rollout readiness. The commented denial/Agent blocks in `verify_poc.sql` are manual checks and are not assumed to have run merely because its active queries passed.

### Setup lessons from the trial

- **Trial activation:** the trial used a credit card before exercising AI. Snowflake documents that adding a card enables AI without ending the trial or upgrading it to a paid account. [Trial limitations][sf-trial]
- **Plugin registration:** the working path used a personal custom MCP plugin with manually entered OAuth client ID and secret. Copy the complete **Callback URL** from that connection into `OAUTH_REDIRECT_URI`. The CIMD metadata URL is a separate field. Snowflake-managed MCP does not support dynamic client registration; the manual-client path leaves Registration URL empty. The **I understand and want to continue** checkbox must be selected before creating the plugin. [ChatGPT setup][oai-client], [Snowflake OAuth setup][sf-mcp]
- **User assignment:** provisioning initially hit a user lookup error and an unsupported non-constant `SET` assignment. The working script obtains `CURRENT_USER()` inside an `EXECUTE IMMEDIATE` Snowflake Scripting block, quotes/escapes the stored username, and binds it with `IDENTIFIER(:poc_user)`. Use the Snowflake user object name rather than assuming the sign-in email is that identifier. [Working assignment block](setup_poc.sql)
- **OAuth role and warehouse:** the connection uses `session:role:all`, which selects the user's `DEFAULT_ROLE`. The script sets a POC role and a non-null default warehouse, keeps secondary roles disabled, and disables in-session role switching. Capture the previous user defaults before changing them. [Role behavior][sf-mcp]
- **Reconnect after a role change:** changing the worksheet role or the user's defaults does not change the role of an existing OAuth connection. Disconnect the connected account through its **…** menu in the plugin settings, use **Connect another account**, and start a fresh chat after authorization. [Detailed role-switching procedure](#personal-trial-switch-roles-and-reconnect-chatgpt)

### Minimum POC completion and optional follow-ups

The core feasibility checks are complete: fixture setup and SQL queries, personal OAuth connection, all-access ChatGPT answers, and permitted/denied results under both restricted roles. Restore `ROLE_ALL_ANALYTICS_POC` and reconnect when returning to the all-access demo; this restoration has not been separately recorded as a test result.

One useful additional quality check is a follow-up asking for September revenue by product category: Electronics must be USD 750 and Home USD 250, totaling USD 1,000. Retain one expanded `analytics` call and an available Snowflake query/run ID as reproducible evidence. These are optional lightweight follow-ups for the personal POC; the broader Sigma, separate-user, refresh/revocation, release, and cost checks belong to the stakeholder rollout stages below.

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

### Personal trial: switch roles and reconnect ChatGPT

The standalone SQL trial assigns all three POC roles to one trial user. Test each as the OAuth session's primary role; separate-user identity isolation still needs dedicated users. With the integration's role switching and secondary roles disabled, an existing OAuth connection retains its authorized primary role. Changing the user's `DEFAULT_ROLE` or running `USE ROLE` in a worksheet does not change that existing connection. Obtain a new OAuth token for each role test. [Snowflake OAuth role behavior][sf-mcp], [Session role restrictions][sf-oauth-custom]

#### Assigned roles and active permissions

The setup already grants `ROLE_SALES_ANALYTICS_POC`, `ROLE_CUSTOMERS_ANALYTICS_POC`, and `ROLE_ALL_ANALYTICS_POC` directly to the current user. The customers-only session's sales denial therefore occurred even though that user already held the sales role. Repeating the same user grant will not activate that role in the existing OAuth session. Run `SHOW GRANTS` to inspect the current user's assigned roles, and `SHOW GRANTS TO ROLE ROLE_ALL_ANALYTICS_POC` to inspect the combined role's inherited grants. These read-only queries are also in [verify_poc.sql](verify_poc.sql). [SHOW GRANTS][sf-show-grants]

With `OAUTH_USE_SECONDARY_ROLES = NONE` and `OAUTH_ANY_ROLE_MODE = DISABLE`, the OAuth session uses its authorized primary role and the privileges that role inherits. Granting a domain role **to a user** makes it available for authorization; granting it **to a parent role** adds its privileges to that parent's hierarchy. The existing `ROLE_ALL_ANALYTICS_POC` inherits both domain roles and is the intended primary role for this two-domain audience. Preserve the restricted roles' separate meanings when testing them. [Role inheritance][sf-role-inheritance]

The default-role changes in this trial simulate different audiences with one user. A normal deployment can use a stable analytics primary role per audience that inherits its permitted domain roles, so users do not need to change defaults for each question. A client can also request a named primary role through `session:role:<role_name>` instead of relying on `DEFAULT_ROLE`; whether ChatGPT honors that configuration needs a separate test. Enabling implicit secondary roles is a different access model and cannot be combined with the current `ALLOWED_ROLES_LIST`. [OAuth configuration][sf-oauth-custom], [MCP role scopes][sf-mcp]

#### Reconnect procedure

1. In [connect_chatgpt.sql](connect_chatgpt.sql), set `DEFAULT_ROLE = 'ROLE_SALES_ANALYTICS_POC'` inside the user-update block, leaving `DEFAULT_WAREHOUSE = 'AGENTIC_ACCESS_POC_WH'`. Run `USE ROLE ACCOUNTADMIN`, then execute only that entire `EXECUTE IMMEDIATE` block.
1. Open ChatGPT **Plugins → Snowflake POC → Connected accounts**.
1. Open the **…** menu at the right of the current Snowflake account row and choose the account disconnection/removal action.
1. Select **Connect another account**, sign in with the same trial Snowflake user, and complete OAuth authorization again. Check the role shown on Snowflake's consent screen when displayed.
1. Start a fresh Work chat, invoke **Snowflake POC** with `@`, and ask the three fixture questions below. Inspect the actual `analytics` tool calls and access warnings. A fresh chat avoids carrying answers from the previous, broader connection into the restricted-role test.
1. Repeat the default-role change, account disconnection, OAuth reconnection, and fresh-chat test with `ROLE_CUSTOMERS_ANALYTICS_POC`.
1. Restore `DEFAULT_ROLE = 'ROLE_ALL_ANALYTICS_POC'` and reconnect again before returning to the all-access demo.

| OAuth primary role | September 2026 completed revenue | All-fixture completed revenue | Registered customers |
| --- | --- | --- | --- |
| `ROLE_SALES_ANALYTICS_POC` | USD 1,000 | USD 2,000 | Access limitation; no customer result |
| `ROLE_CUSTOMERS_ANALYTICS_POC` | Access limitation; no sales result | Access limitation; no sales result | 6 |
| `ROLE_ALL_ANALYTICS_POC` | USD 1,000 | USD 2,000 | 6 |

For a denied domain, a refusal or access warning is the expected outcome; a guessed number or a substitution from the accessible domain is a failure. Record each role's actual result and available tool/run evidence, distinguishing manual confirmations from independently reproduced traces as in the observed matrix above. Reconnection for this experiment is separate from the explicit Snowflake authorization-revocation test in the lifecycle and cleanup stages.

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
[sf-oauth-custom]: https://docs.snowflake.com/en/user-guide/oauth-custom#allowing-clients-to-switch-roles
[sf-partial]: https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents-inaccessible-tool-handling
[sf-privileges]: https://docs.snowflake.com/en/user-guide/security-access-control-privileges
[sf-quotas]: https://docs.snowflake.com/en/user-guide/budgets/per-user-quotas
[sf-role-inheritance]: https://docs.snowflake.com/en/user-guide/security-access-control-overview#authorization-through-primary-role-and-secondary-roles
[sf-show-grants]: https://docs.snowflake.com/en/sql-reference/sql/show-grants
[sf-trial]: https://docs.snowflake.com/en/user-guide/admin-trial-account#current-limitations-for-trial-accounts
[sigma-sv]: https://help.sigmacomputing.com/docs/query-and-extend-snowflake-semantic-views-in-sigma
[tf-1-11]: https://github.com/hashicorp/terraform/blob/v1.11.0/CHANGELOG.md
[tf-mocking]: https://developer.hashicorp.com/terraform/language/tests/mocking

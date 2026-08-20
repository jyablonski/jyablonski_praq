# Snowflake Managed MCP: Do We Need It?

Date: 2026-08-19

## Short answer

Snowflake Semantic Views are the governed business layer, not the natural-language interface. Cortex Analyst turns natural language into SQL over those views, and Cortex Agents can orchestrate Analyst, execute the generated SQL, combine it with search or custom tools, and compose an answer.

You do not need MCP to add natural-language analytics to an application you control; that application can call the Cortex Analyst or Cortex Agents REST API directly. You do need an MCP endpoint when the consuming product expects MCP, as ChatGPT custom apps and many developer assistants do.

For the two proposed use cases:

- **Internal developer tools:** Snowflake-managed MCP is the simplest path when the developers have Snowflake identities and the clients support remote MCP. If an internal MCP platform already exists, it can expose a purpose-built Cortex tool instead; Snowflake-managed MCP is then optional.
- **Stakeholder data Q&A in ChatGPT:** use a ChatGPT **custom app** backed by one narrowly scoped `CORTEX_AGENT_RUN` tool on a Snowflake-managed MCP server. This is the cleanest way to retain per-user Snowflake authorization. A private workspace app does not need to be packaged or published as a public ChatGPT plugin.
- **Stakeholders without Snowflake identities:** MCP does not remove the identity requirement. Direct Snowflake OAuth or External OAuth still resolves the caller to a Snowflake user. Provisioning narrowly entitled Snowflake users is safer than putting a broad service account behind an internal MCP server.

The main readiness questions are therefore not “Do we have MCP?” They are:

1. Are the semantic views accurate enough for unsupervised use?
1. Can every caller be mapped to an appropriate Snowflake identity and role?
1. Is the returned data approved to leave Snowflake and enter the selected LLM product?
1. Which system will own auditing, rate limits, feedback, and incident response?

## Where MCP fits

```text
Tables and policies
        |
        v
Semantic Views                 governed definitions, joins, metrics, synonyms
        |
        v
Cortex Analyst                 natural language -> SQL
        |
        v
Cortex Agent (optional)        tool selection, SQL execution, search, final answer
        |
        +--> REST API / custom application / Snowflake CoWork     MCP not required
        |
        +--> ChatGPT / developer MCP clients                      MCP endpoint required
```

This separation matters. MCP is a serving protocol and tool-discovery layer; it does not improve the semantic model or make generated SQL more accurate. If Cortex Analyst performs poorly against a semantic view, wrapping it in MCP only distributes the poor result more widely.

Snowflake CoWork is also worth testing before building a stakeholder integration. It is a ready-made conversational interface over Cortex Agents, uses the caller's Snowflake credentials, and applies that user's RBAC and masking policies. If stakeholders accept a Snowflake-hosted interface, it is the shortest proof of whether the semantic layer is ready. It does not, however, solve the goal of meeting users inside ChatGPT.

## What the Snowflake-managed MCP server provides

The managed server is a generally available schema object that exposes a remote HTTPS MCP endpoint. It uses Snowflake OAuth by default and can be bound to an External OAuth provider such as Okta or Microsoft Entra ID. It currently supports MCP tools, but not resources, prompts, roots, sampling, notifications, or streaming responses.

Supported tool types are:

| Tool type | Behavior | Recommended audience |
| ----------------------------- | -------------------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| `CORTEX_AGENT_RUN` | Invokes a Cortex Agent that can use Analyst, Search, and custom tools | Business stakeholders and governed Q&A |
| `CORTEX_ANALYST_MESSAGE` | Generates SQL from a natural-language question and returns the SQL to the client | Controlled developer workflows that will decide how to execute the SQL |
| `CORTEX_SEARCH_SERVICE_QUERY` | Searches unstructured data through Cortex Search | Document retrieval and RAG |
| `SYSTEM_EXECUTE_SQL` | Executes SQL with configured read-only and timeout controls | Engineers and analysts only |
| `GENERIC` | Invokes a UDF or stored procedure with a JSON input schema | Narrow, deterministic business operations |

For stakeholder Q&A, Snowflake recommends exposing a Cortex Agent as the client-facing tool. That gives the external model one governed entry point and keeps orchestration in Snowflake. Exposing Cortex Analyst alone is incomplete for this experience because Analyst returns generated SQL; something must still execute it and turn the result into an answer.

An MCP server is created from a YAML specification:

```sql
CREATE OR REPLACE MCP SERVER analytics_db.mcp_schema.business_mcp
  FROM SPECIFICATION $$
  tools:
    - title: "Governed business data agent"
      name: "business_data_agent"
      type: "CORTEX_AGENT_RUN"
      identifier: "analytics_db.agents.business_agent"
      description: "Answers governed business data questions."
  $$;
```

The endpoint follows this form:

```text
https://<account_url>/api/v2/databases/<database>/schemas/<schema>/mcp-servers/<name>
```

### Access control details

Access is layered:

- `USAGE ON MCP SERVER` permits connection and tool discovery.
- Invoking a tool also requires privileges on the referenced agent, search service, semantic view, function, procedure, warehouse, database, schema, and data objects as applicable.
- Cortex Analyst requires the Snowflake database role `SNOWFLAKE.CORTEX_ANALYST_USER` or the broader `SNOWFLAKE.CORTEX_USER`. Cortex Agents similarly require `SNOWFLAKE.CORTEX_AGENT_USER` or `SNOWFLAKE.CORTEX_USER`.
- A role using a semantic view directly in SQL needs `SELECT` only on the semantic view because it runs with owner's rights. Cortex Analyst requires `SELECT` and `REFERENCES` on the semantic view. Snowflake's current Agent and semantic-view guidance also requires the executing role to have access to underlying tables used by an Agent/Analyst workflow. Do not assume that granting the semantic view alone creates a strict AI-serving boundary.
- Row-access and masking policies on the underlying data still propagate through semantic views. Sample values stored as semantic-view metadata are an exception: Snowflake warns that they are not masked.

The distinction between direct semantic-view SQL and Analyst/Agent access should be tested with the exact role design. Snowflake's documentation is not fully consistent across every privilege table, so a least-privilege integration test is more reliable than copying a broad future-table grant.

### OAuth and role behavior

External OAuth lets an MCP client authenticate through Okta, but Snowflake still maps a token claim such as `sub` to a Snowflake user's `LOGIN_NAME` or `EMAIL_ADDRESS`. An Okta identity without a corresponding Snowflake user does not gain Snowflake access merely because MCP is present.

Existing Okta SSO or SCIM provisioning does not necessarily mean External OAuth for Snowflake is configured. External OAuth requires an Okta authorization server, client, Snowflake role scopes, token audience, claims, and a Snowflake security integration. Because managed MCP uses Snowflake OAuth by default, start there unless security policy or client behavior specifically requires Okta-issued access tokens; bind the server to External OAuth only after verifying the extra configuration and refresh-token flow.

By default, Snowflake-managed MCP advertises `session:role:all`, which means “use the user's `DEFAULT_ROLE`”; it does not activate every role. Some clients cannot request a more specific role scope. The OAuth integration should disable secondary roles and restrict allowed roles, and each caller needs a usable default warehouse.

Do not automatically change every existing analyst's default role to a new MCP role. That can disrupt their other Snowflake workflows. First test whether the target client honors an advertised `session:role:<role_name>` scope. If it does not, either grant the necessary least-privilege role through the caller's existing default-role hierarchy or separate the audience and OAuth/server configuration deliberately. For users created only for this experience, a dedicated default role and warehouse are straightforward.

### Relevant limits

- Maximum 50 tools per managed MCP server.
- Non-streaming responses only.
- `GENERIC` and `SYSTEM_EXECUTE_SQL` responses are truncated at 250 KB.
- Cortex Agent responses include intermediate steps and can exceed 200 KB; constrain search result counts and avoid returning raw datasets.
- Recursion depth is capped at 10, but circular Agent-to-MCP designs can still waste credits and add latency.
- MCP server objects do not replicate in failover groups and must be recreated in a secondary account.
- The feature is not available in Snowflake government regions.
- Snowflake recommends dashed account hostnames because underscores cause compatibility problems in some clients.

## Does an internally hosted MCP server change the recommendation?

Yes. If a trusted internal MCP platform already handles authentication, policy, observability, and client distribution, there is little value in adding Snowflake-managed MCP merely as another protocol hop. The internal server can call the Cortex Analyst or Cortex Agents REST API directly.

The choice is between the following designs:

| Design | Strengths | Main drawback | Best fit |
| ---------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| Client -> Snowflake-managed MCP -> Cortex Agent | Minimal infrastructure; Snowflake validates each user and applies native RBAC | Every caller needs a Snowflake identity; limited response shaping and no streaming | ChatGPT and supported developer clients querying governed data |
| Client -> internal MCP -> Cortex REST API with delegated user identity | Central policy, response shaping, rate limits, cross-system tools, and internal observability | Delegated downstream authentication is a real security design, not a simple proxy | Organizations with an established MCP gateway and identity platform |
| Client -> internal MCP -> Snowflake service identity | Simple runtime authentication and supports callers without Snowflake users | All calls share one Snowflake security context; per-user Snowflake RBAC is lost | Narrow tools over data that every authorized caller may see |
| Client -> internal MCP -> Snowflake-managed MCP | Uniform upstream MCP interface and Snowflake-owned tool definitions | Extra latency, duplicated failure modes, and difficult token propagation | Only when the gateway already supports secure delegated-token relay and upstream MCP federation |

### The delegated-identity trap

The shorthand “exchange the user's Okta token for a Snowflake token” is too optimistic. OAuth access tokens are audience- and scope-bound. A token issued for the internal MCP server cannot normally be forwarded to Snowflake, and neither Snowflake nor Okta documentation establishes a universal on-behalf-of token exchange for this design.

A self-hosted server can preserve user identity only if the IdP, ChatGPT/client OAuth flow, internal resource server, and Snowflake External OAuth integration are deliberately configured to support the same delegated authorization model. That may involve token relay with compatible issuer, audience, claims, and scopes, or a separate downstream authorization flow and per-user token store. It requires an identity/security review and a working proof of concept.

If the server instead uses a service user, Snowflake sees the service user for every request. Application logs or a `QUERY_TAG` can record the originating stakeholder, but neither changes Snowflake authorization. Row-access policies based on `CURRENT_USER()` or role will evaluate the service identity, not the stakeholder.

For that reason, a service-identity MCP should expose only narrow, read-only tools whose outputs are safe for every person authorized to call them. Avoid general `execute_sql` access and avoid pretending that application-side filtering is equivalent to Snowflake-native row-level security.

### Network reachability

An MCP server that is reachable only on the corporate network can work for internal desktop or IDE clients on that network. ChatGPT cannot connect directly to a local or private MCP endpoint. The server must be exposed as a remote HTTPS MCP endpoint or connected through OpenAI's Secure MCP Tunnel. This is independent of whether the server is hosted on internal infrastructure.

## Recommended design for these use cases

### 1. Stakeholder Q&A in ChatGPT

Use this as the initial target:

```text
ChatGPT custom app
        |
        | per-user OAuth
        v
Snowflake-managed MCP
        |
        | one CORTEX_AGENT_RUN tool
        v
Domain-specific Cortex Agent
        |
        v
Validated Semantic View(s)
```

Keep the ChatGPT-facing tool surface small: ideally one domain-specific Agent per app/server, with a precise name and description. Separate stakeholder and developer servers so a broad SQL tool is never published to the stakeholder app.

Use the term **custom app**, not “ChatGPT plugin,” in the implementation plan. A plugin is a broader packaging and directory concept; a private workspace integration can be deployed as a custom MCP app without creating a plugin listing.

Current ChatGPT constraints to confirm before committing to this route:

- Full MCP custom apps are available on ChatGPT Business, Enterprise, and Edu on the web; Pro supports only read/fetch MCP use in developer mode.
- An administrator or owner must publish the app. Enterprise/Edu can use RBAC to limit access and actions.
- Business workspaces currently require recreation and republication to change a published app. Enterprise/Edu can refresh and review changed actions, but updates are not automatic.
- The OAuth provider must issue refresh tokens; OpenAI recommends advertising and requesting `offline_access` where applicable.
- ChatGPT uses a frozen snapshot of approved tool definitions. Breaking schema changes can cause calls to fail until an administrator refreshes and republishes them.
- Agent mode does not use custom apps. Deep research can use them only for read/fetch actions.
- Query results leave Snowflake and become part of the ChatGPT conversation. Snowflake RBAC controls retrieval, not what happens after retrieval. Review ChatGPT workspace retention, memory, sharing, data residency, compliance, and training settings against the data classification. OpenAI states that Business, Enterprise, and Edu data is not used for model training by default, but that is only one part of the review.

### 2. Internal developer MCP

Choose one path rather than maintaining duplicate tool definitions:

- **Use Snowflake-managed MCP directly** if the developer clients support it and each developer can authenticate as a Snowflake user. Publish a separate developer server with `SYSTEM_EXECUTE_SQL` configured read-only, a short query timeout, a dedicated warehouse, and tightly scoped roles.
- **Extend the existing internal MCP server** if it already provides materially useful controls such as an approved-server catalog, cross-system tools, centralized audit, payload shaping, or rate limits. Have it call Cortex REST APIs directly unless there is a specific reason to federate to the managed MCP endpoint.

In both cases, make “ask governed business data” a distinct tool from “execute arbitrary read-only SQL.” The former should use an Agent or Analyst grounded in approved semantic views; the latter should remain restricted to engineers and analysts.

Do not use the open-source `Snowflake-Labs/mcp` repository as the foundation for the internal service. Snowflake has deprecated it, stopped maintenance, and directs new and existing use cases to the managed server. A separately maintained internal MCP implementation can still be appropriate; the warning is specific to adopting that legacy package.

## Users without Snowflake access

Provisioning Snowflake users through Okta SCIM is the preferred answer when those users should receive differentiated governed data. Snowflake's AI pricing is consumption-based and documents no per-seat AI fee, although the account contract and the separate ChatGPT seat cost still need confirmation. Provisioning is therefore primarily an identity, authorization, and support decision rather than an MCP decision.

For users who should not receive general Snowsight access, investigate Snowflake interface restrictions and narrowly scoped roles rather than replacing user identity with a shared account. Confirm that the chosen interface restriction supports the MCP endpoint; do not assume that a restriction intended for Snowflake CoWork also permits third-party MCP access.

Use a service identity only when all of the following are true:

- Every authorized caller may see the same data.
- The MCP tools are narrow and read-only.
- The application independently authenticates and authorizes callers.
- Every request is attributed in both application logs and Snowflake query metadata.
- Rate limits, result-size limits, timeouts, and cost controls are enforced.
- Security accepts that Snowflake row-level authorization is evaluated as the service user.

## Semantic-view readiness

The semantic layer is the largest quality risk. Before exposing it to stakeholders:

- Build a representative set of verified questions with expected SQL and results.
- Run Cortex Analyst evaluations and keep the results as a regression baseline.
- Prefer domain-focused semantic views over a single organization-wide view.
- Add business descriptions, synonyms, verified queries, and custom instructions where ambiguity exists.
- Mark intermediate facts and metrics `private_access` so they cannot be queried directly.
- Test joins, time grains, fiscal calendars, currencies, null handling, and similarly named metrics.
- Test the same questions under every intended stakeholder role, including row-access and masking-policy cases.
- Record the generated SQL, request ID, selected semantic view, role, warehouse, latency, cost, and user feedback.
- Define when the assistant must decline or ask for clarification rather than generate a plausible answer.

## Cost and operational considerations

The managed MCP object does not add a separately documented serving charge; the invoked services do. Budget for:

- Cortex Analyst or Cortex Agent usage. Analyst is billed per successful message when called directly; Agent usage is token-based and additive with the services it invokes.
- Warehouse compute for generated SQL, with a dedicated warehouse, auto-suspend, statement timeouts, and resource monitoring.
- ChatGPT workspace licenses.
- Internal gateway infrastructure and support if self-hosting.
- Evaluation runs, observability, and incident response.

Monitor Analyst through `SNOWFLAKE.ACCOUNT_USAGE.CORTEX_ANALYST_USAGE_HISTORY` and AI services through `METERING_HISTORY`. Agent and Snowflake CoWork usage have their own monitoring surfaces. Establish budgets and attribution before broad rollout.

## Recommended rollout

1. **Validate the semantic layer.** Establish a verified-query suite and evaluation baseline for one domain.
1. **Run a Snowflake CoWork pilot.** Use existing Snowflake users to validate question quality, permissions, latency, and cost without MCP integration work.
1. **Resolve identity and data handling.** Decide which stakeholders will receive Snowflake users, which roles they use, and which data classifications may enter ChatGPT.
1. **Pilot the developer path.** Compare direct Snowflake-managed MCP with one tool on the existing internal MCP platform. Keep the option that has fewer identity and operational hops.
1. **Pilot one ChatGPT custom app.** Publish one `CORTEX_AGENT_RUN` tool to a small authorized group, validate per-user results, and test token refresh and tool-update procedures.
1. **Introduce a gateway only for a demonstrated need.** Examples include cross-system orchestration, response shaping, central rate limits, or a narrowly approved service-identity use case.

## Decision table

| Question | Answer |
| --------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Do Semantic Views alone provide natural-language Q&A? | No. They provide governed semantics; Cortex Analyst or an Agent provides the natural-language behavior. |
| Is MCP required for NLP over Semantic Views? | No. A controlled application can use the Cortex REST APIs or Snowflake CoWork. |
| Is MCP required for a ChatGPT custom app? | Yes, for this integration shape. |
| Is Snowflake-managed MCP required if an internal MCP server already exists? | No. The internal server can call Cortex REST APIs, provided its Snowflake authentication model is acceptable. |
| What is the best default for governed stakeholder data? | Snowflake-managed MCP with per-user OAuth and a narrowly scoped Cortex Agent. |
| Does self-hosting solve the missing-Snowflake-user problem? | Only by moving authorization responsibility into the application or by using a shared Snowflake identity. It does not preserve native per-user RBAC automatically. |
| Should business users receive raw SQL tools? | No. Expose a domain-specific Agent; reserve read-only SQL for a separate developer server and role. |
| What should be proved first? | Semantic-view accuracy, per-role results, identity mapping, data-handling approval, latency, and cost. |

## Questions to resolve internally

1. Which ChatGPT plan is in use, and who can publish and administer custom apps?
1. Which stakeholder groups need different row-level or masked results?
1. Can all target stakeholders be provisioned in Snowflake through Okta SCIM?
1. Will the MCP endpoint use Snowflake OAuth or Okta External OAuth, and does the selected authorization server issue the refresh tokens and Snowflake role scopes required by the client?
1. Which data classifications may be returned to ChatGPT, retained in conversations, remembered, or shared?
1. Do current default roles and warehouses already provide a safe MCP session, or would changing them disrupt other Snowflake workflows?
1. Is the internal MCP endpoint reachable from ChatGPT, or would it require Secure MCP Tunnel or a public ingress?
1. Who owns semantic-view evaluations, verified queries, feedback review, and on-call support?
1. What monthly cost and per-user rate limits should stop or degrade the service?
1. Is failover required, and if so, how will MCP objects and external app configuration be recreated and tested?

## Sources

- [Snowflake-managed MCP server](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents-mcp)
- [Cortex Analyst](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-analyst)
- [Cortex Analyst evaluations](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-analyst-evaluations)
- [Cortex Agents access control and authentication](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents-setup)
- [Semantic View SQL and privileges](https://docs.snowflake.com/en/user-guide/views-semantic/sql)
- [Semantic View development and security practices](https://docs.snowflake.com/en/user-guide/views-semantic/best-practices-dev)
- [Snowflake External OAuth overview](https://docs.snowflake.com/en/user-guide/oauth-ext-overview)
- [Configure Okta for Snowflake External OAuth](https://docs.snowflake.com/en/user-guide/oauth-okta)
- [Snowflake CoWork overview](https://docs.snowflake.com/en/user-guide/snowflake-cortex/snowflake-cowork)
- [Snowflake AI pricing](https://docs.snowflake.com/en/user-guide/snowflake-cortex/pricing)
- [Deprecated Snowflake-Labs MCP server](https://github.com/Snowflake-Labs/mcp)
- [Developer mode and MCP apps in ChatGPT](https://help.openai.com/en/articles/12584461-developer-mode-and-mcp-apps-in-chatgpt)
- [Apps in ChatGPT](https://help.openai.com/en/articles/11487775-connectors-in-chatgpt)
- [OpenAI business data privacy](https://openai.com/business-data/)

# Snowflake MCP Server — Evaluation Notes

## Summary

Snowflake-managed MCP servers are generally available database objects. They expose Cortex Analyst, Cortex Search, Cortex Agents, SQL execution, and custom UDFs or stored procedures as tools over a remote HTTPS endpoint, so we do not need to host an MCP service for the Snowflake integration.

Recommendation in brief:

- **ChatGPT surface** — connect ChatGPT directly to Snowflake’s managed MCP server. Do not add internal MCP server proxy unless it provides a separate, concrete capability.
- **Internal app page** — use the Cortex Agents `agent:run` REST API by default because it supports typed server-sent-event streaming; use the managed MCP server if a common MCP interface or client-side tool discovery is more valuable than progressive rendering.
- **Proxying Snowflake through internal MCP server** — avoid it for a single Snowflake-backed agent. Keep it as an option only if the service becomes a deliberate multi-system gateway with its own policy, audit, or orchestration responsibilities.

If both surfaces invoke the same Cortex Agent, the existing semantic views, verified queries, synonyms, and Cortex Analyst instructions remain below the integration boundary. That investment is reusable, but only when we use the same agent configuration and compatible semantic-view objects.

## Use cases in scope

1. **ChatGPT connector** — stakeholders ask questions in ChatGPT and receive answers from governed Snowflake data. This requires no application code from us, but it does require workspace administrator approval, a remote MCP endpoint, OAuth client configuration, and the appropriate Snowflake identity and grants.
1. **Custom page in internal app** — an embedded chat or query surface that we own and style. This requires a backend integration, authentication, response handling, and UI logic; the REST API is the better fit if we want streaming.

Both surfaces can point at the same Cortex Agent and semantic views. We should define and maintain one governed agent configuration, then choose the transport per client.

## How it works

### Objects

```sql
CREATE OR REPLACE MCP SERVER <db>.<schema>.<name>
  FROM SPECIFICATION $$
  tools:
    - title: "Business data agent"
      name: "business_data_agent"
      type: "CORTEX_AGENT_RUN"
      identifier: "<db>.<schema>.<agent_name>"
      description: "Answers governed business data questions."
  $$;
```

Endpoint: `https://<account_url>/api/v2/databases/{db}/schemas/{schema}/mcp-servers/{name}`

Supported tool types are `CORTEX_AGENT_RUN`, `CORTEX_ANALYST_MESSAGE`, `CORTEX_SEARCH_SERVICE_QUERY`, `SYSTEM_EXECUTE_SQL`, and `GENERIC` for UDFs or stored procedures.

For governed business questions, Snowflake recommends exposing a Cortex Agent as the only client-facing tool on a server. The agent can orchestrate Cortex Analyst, Cortex Search, and custom tools behind one stable interface. A directly exposed Cortex Analyst tool generates and returns SQL; a separate SQL execution tool can run SQL, but exposing it alongside the agent can let the MCP client bypass the agent’s semantic views, verified queries, and orchestration. If direct SQL is required, Snowflake recommends a separate MCP server with a dedicated least-privileged role.

The managed MCP server currently supports semantic views—not semantic models—when Cortex Analyst is exposed directly. Verify that any existing Analyst configuration uses a supported semantic view before the pilot.

One Cortex Agent can use multiple semantic views. Configure each view as a separate Cortex Analyst tool with a distinct name and description, then use orchestration instructions to tell the Agent which tool covers which business domain. The Agent can route across the views based on the user’s question, but tool selection is a quality behavior rather than an authorization boundary; evaluate overlapping questions and cross-domain questions explicitly.

### Request path (ChatGPT)

1. The user asks a question in ChatGPT.
1. ChatGPT decides whether to call the enabled tool using the tool metadata, conversation, and its own policies.
1. ChatGPT’s remote client infrastructure calls the Snowflake MCP endpoint over HTTPS with an OAuth access token obtained through the user’s authorization flow; the request originates from the provider’s infrastructure, not the user’s browser.
1. Snowflake validates the token and maps the identity to a Snowflake user. The session uses the user’s `DEFAULT_ROLE` when the client requests `session:role:all`; a client that requests a named advertised role scope can use that primary role instead. The recommended least-privilege configuration disables secondary roles and assigns the MCP access role as the user’s default role.
1. The Cortex Agent orchestrates its configured tools. Cortex Analyst uses the semantic view and its synonyms, verified queries, and custom instructions to generate SQL.
1. SQL executes in the Snowflake session governed by the effective role, warehouse, and data protection policies. Row access and masking policies continue to apply, and policies can distinguish agent-active sessions with `IS_AGENT_ACTIVATED` where appropriate.
1. The MCP server returns one non-streaming response to ChatGPT, which then writes the user-facing answer.

### Auth model

- A Snowflake user object is required for per-user authentication and governance. A service identity is possible, but all requests using it share that identity’s role and data access, so it is not equivalent to per-user authorization.
- External OAuth maps a token claim to an existing Snowflake user; SCIM can provision and deactivate Snowflake users and groups from Okta or another supported identity provider. Neither mechanism removes the need for a Snowflake user object when the token is user-mapped.
- Snowflake does not describe MCP as a separate seat-priced product in the current documentation. The material costs are Cortex AI credits, Cortex Search usage where applicable, warehouse compute, and any account-specific commercial terms; confirm the contract before assuming a rollout has no per-user cost.
- Provisioning minimal users through Okta SCIM is reasonable. Set `DEFAULT_ROLE` to the MCP access role and set `DEFAULT_WAREHOUSE`; agent calls fail when the default warehouse is null. Do not grant unrelated privileges to these users.
- To bind a schema’s MCP servers to Okta, create an External OAuth security integration and set `OAUTH_AUTHORIZATION_SERVER` on the schema. The parameter inherits from schema to database to account, so the MCP object does not need to be recreated when the binding changes; clients do need to reauthorize, and Snowflake OAuth tokens are rejected after the external binding is active.
- RBAC has multiple layers. `USAGE` on the MCP server allows connection and tool discovery, while each tool requires its own privilege. A Cortex Agent also requires the `SNOWFLAKE.CORTEX_AGENT_USER` database role, warehouse/database/schema access, `USAGE` on the agent, and privileges on the resources used by the agent. Grant only the required access and never grant the MCP role to `PUBLIC`.

## Permissions and grants for the pilot

Assume the five users are members of one Okta group that SCIM maps to the Snowflake account role `STAKEHOLDERS_ROLE`, and that the Agent, MCP server, and semantic views are in `PRODUCTION.REPORTING`. The role grants below are shared by Finance, Marketing, and the other pilot users; they do not by themselves provide department-specific row filtering.

The minimum invocation role, assuming one Agent and no Cortex Search or custom tools, is:

```sql
-- Run as an administrator or role with authority to grant these privileges.
GRANT DATABASE ROLE SNOWFLAKE.CORTEX_AGENT_USER TO ROLE STAKEHOLDERS_ROLE;

GRANT USAGE ON WAREHOUSE <stakeholder_warehouse> TO ROLE STAKEHOLDERS_ROLE;
GRANT USAGE ON DATABASE PRODUCTION TO ROLE STAKEHOLDERS_ROLE;
GRANT USAGE ON SCHEMA PRODUCTION.REPORTING TO ROLE STAKEHOLDERS_ROLE;

GRANT USAGE ON MCP SERVER PRODUCTION.REPORTING.<mcp_server_name>
  TO ROLE STAKEHOLDERS_ROLE;
GRANT USAGE ON AGENT PRODUCTION.REPORTING.<agent_name>
  TO ROLE STAKEHOLDERS_ROLE;

GRANT SELECT ON SEMANTIC VIEW PRODUCTION.REPORTING.<semantic_view_name>
  TO ROLE STAKEHOLDERS_ROLE;
```

Grant the role access to every semantic view and every source object referenced by all of the Agent’s semantic views. If the sources are tables or views in the same schema, the grants look like this:

```sql
GRANT SELECT ON TABLE PRODUCTION.REPORTING.<source_table_name>
  TO ROLE STAKEHOLDERS_ROLE;
GRANT SELECT ON VIEW PRODUCTION.REPORTING.<source_view_name>
  TO ROLE STAKEHOLDERS_ROLE;
```

Add only the privileges for tools actually configured on the Agent. For Cortex Search, grant `USAGE` on the Search service plus `USAGE` on its database and schema. For UDF or stored-procedure tools, grant `USAGE` on the specific function or procedure. Do not grant `CREATE`, `MODIFY`, `OWNERSHIP`, or `MONITOR` to stakeholders; `MONITOR` is for users who need Agent threads, logs, or traces rather than ordinary invocation.

Okta SCIM and Okta External OAuth are separate controls. SCIM provisions users, groups, roles, and role membership; External OAuth authenticates the MCP client and maps the token claim to the existing Snowflake user. Create or push the Okta group through Okta if Okta is the source of truth for membership, then apply the Snowflake object grants to the resulting `STAKEHOLDERS_ROLE`. Do not maintain the same role membership manually in Snowflake and Okta.

Each provisioned user must have `STAKEHOLDERS_ROLE` as `DEFAULT_ROLE` and a warehouse as `DEFAULT_WAREHOUSE`, because Cortex Agents uses the user’s default role rather than whichever role happens to be active in the client session. Okta’s `defaultRole` and `defaultWarehouse` SCIM attributes are optional and unmapped by default, so map them in the Okta profile or expression, or set them explicitly after provisioning:

```sql
ALTER USER <snowflake_login_name>
  SET DEFAULT_ROLE = STAKEHOLDERS_ROLE
      DEFAULT_WAREHOUSE = <stakeholder_warehouse>;
```

If Finance and Marketing must see different rows, keep `STAKEHOLDERS_ROLE` for common object access and enforce the distinction with row access policies keyed to a trusted user attribute or immutable session attribute. A single shared role cannot express department-specific access on its own. Test the effective role and policy result through the actual ChatGPT-plus-Okta flow before expanding the pilot.

## Streaming: the main caveat

The Snowflake-managed MCP server supports only non-streaming responses. The Cortex Agents `agent:run` REST API streams server-sent events by default and returns a single JSON response only when `stream` is set to `false`.

This matters differently per surface:

- **ChatGPT** — ChatGPT owns the client experience, so this integration cannot use Snowflake’s streaming events to render intermediate progress in the ChatGPT UI.
- **Internal app page** — a multi-step agent turn can take long enough that progressive feedback is valuable. The REST API can expose typed status, text deltas, tool-use and tool-result events, citations, and a final response. Treat thinking events as sensitive implementation detail and do not automatically display raw reasoning to end users.

Agent responses can be large because the MCP agent tool includes intermediate steps, tool calls, search results, citations, and reasoning traces by design; Snowflake warns that payloads can reach 200 KB or more. The MCP response wraps that content in a JSON-RPC response, while the REST API exposes typed streaming events. The application should bound search results, handle large responses, and decide deliberately which intermediate content to retain or display.

MCP does not inherently eliminate authentication work for the internal app. Both REST and MCP require an access token and a Snowflake identity, role, warehouse, and resource grants. The app can choose a service identity, but that is a governance decision rather than an MCP advantage.

Use MCP for the internal page when the app benefits from a standard tool interface, client-side discovery, or interoperability with multiple MCP clients. Use REST when the app primarily needs one governed Snowflake Agent and a responsive streaming UI.

## Why not chain internal MCP server in front of Snowflake’s

1. **Token forwarding is not a valid shortcut.** MCP authorization guidance requires a server to accept tokens intended for itself and prohibits passing unrelated upstream tokens through to downstream services. A proxy must obtain a separate downstream credential, such as through a separate OAuth flow, token exchange, or a service identity. That adds security and identity-mapping work and does not remove Snowflake’s user and role requirements when we need per-user governance.
1. **A proxy adds another policy and failure boundary.** It increases latency, troubleshooting surface, credential handling, and the number of tool descriptions that can influence routing without adding Snowflake governance value for a single-agent use case.
1. **Recursive composition needs a concrete reason.** Snowflake warns that an external client calling an Agent through MCP, where the Agent calls another MCP server that returns to an Agent, can create expensive unbounded loops; Snowflake enforces a maximum recursion depth of 10. Keep a gateway only when it deliberately composes multiple upstream systems or centralizes controls.

## Operational gotchas

- **Frozen tool snapshot in ChatGPT.** After an administrator approves a custom MCP app, ChatGPT uses a frozen snapshot of its tools and input schemas. Later changes require an administrator to review and publish an update; incompatible changes can cause tool-call failures. Treat the MCP specification as a versioned interface contract and keep iterative changes below it in the agent, semantic views, verified queries, and instructions.
- **PrivateLink and SaaS clients.** If the Snowflake account uses PrivateLink, configure ChatGPT with the public MCP URL and set `USE_PRIVATELINK_FOR_AUTHORIZATION_ENDPOINT = TRUE` on the OAuth integration. Snowflake then uses the private authorization endpoint while keeping the token endpoint reachable by the SaaS client.
- **Network policy.** If account network policies are enabled, allow the MCP client provider’s outbound IP addresses. A blocked token request can return `invalid_client`, which is indistinguishable from some credential or authentication-method errors; check the network policy when credentials look correct.
- **Role scopes are client-dependent.** Claude is documented as requesting `session:role:all`, which uses the user’s `DEFAULT_ROLE`; do not assume every SaaS client honors named primary-role scopes. Use per-user default roles and data policies when the client does not support role selection, and test ChatGPT’s effective role explicitly.
- **Failover replication.** MCP server objects are not replicated in failover groups, although OAuth security integrations are. Recreate the MCP objects on the secondary account and include them in the DR runbook.
- **Other limits.** The managed server does not support MCP resources, prompts, roots, notifications, version negotiation, lifecycle phases, or sampling. Each server supports at most 50 tools. Generic-tool and SQL-execution responses are truncated at 250 KB. The managed server is not supported in government regions.
- **Deprecated implementation.** The Snowflake-Labs open-source MCP server is deprecated and no longer maintained; use the official Snowflake-managed MCP server for new work and migrate existing deployments.

## Cost shape

- Cortex Agents are billed in AI Credits per million tokens processed, with additive costs across the underlying services the agent invokes; the model and routing configuration affect the rate.
- Direct Cortex Analyst API usage is currently listed as legacy Platform Credit pricing per 1,000 messages. SQL generated by either path incurs separate virtual warehouse compute.
- Cortex Search has its own serving and embedding compute charges when the Agent uses it.
- Monitor `CORTEX_AGENT_USAGE_HISTORY` for Agent usage and `WAREHOUSE_METERING_HISTORY` for warehouse compute.

For a wide stakeholder rollout, estimate total cost per question from the pilot instead of extrapolating from a single API price. Include Agent tokens, Search usage, warehouse compute, retries, and the expected question mix.

## Open questions

- Do stakeholders need differentiated row-level access? If yes, choose per-user Snowflake identities and default roles; if no, a service identity may be simpler but has coarser governance and auditability.
- Will the internal app use delegated per-user OAuth to Snowflake or a service identity? If it uses a proxy, define the downstream-token and identity-mapping pattern before implementation.
- Will the ChatGPT workspace admin enable custom MCP apps for the intended plan and users? What is the approval, refresh, and rollback process for tool-definition changes?
- Is the internal page a single-agent chat surface or an app-side agent loop that composes Snowflake with Jira, internal documents, or other tools? This determines whether the gateway complexity is justified.
- What retention, privacy, and display policy applies to Agent intermediate steps, citations, generated SQL, and user prompts?

## Suggested pilot

1. Use one Cortex Agent over the existing semantic views, and confirm that any direct Analyst configuration uses semantic views rather than semantic models.
1. Create one managed MCP server exposing only that Agent.
1. Create a least-privileged MCP access role with `SNOWFLAKE.CORTEX_AGENT_USER`, required warehouse/database/schema privileges, MCP and Agent `USAGE`, and only the underlying resource grants the Agent needs.
1. Configure a Snowflake OAuth security integration with `OAUTH_USE_SECONDARY_ROLES = NONE` and `ALLOWED_ROLES_LIST = ('mcp_access_role')`; set each pilot user’s `DEFAULT_ROLE` and `DEFAULT_WAREHOUSE`.
1. Connect about five pilot users through ChatGPT and verify OAuth renewal, effective role, visible tools, row-level and masking behavior, response size, errors, and prompt-injection handling.
1. Measure p50 and p95 latency and cost per question using `CORTEX_AGENT_USAGE_HISTORY` and warehouse metering, with representative questions and known-good expected answers.
1. If Okta is preferred, create the External OAuth integration, bind it with `ALTER SCHEMA ... SET OAUTH_AUTHORIZATION_SERVER = ...`, reconnect the clients, and repeat the authorization and governance tests. Recreating the MCP server should not be necessary.

## Suggested POC path

1. Confirm the POC scope, the existing semantic views, the initial stakeholder questions, and whether all pilot users can share the same data-access policy.
1. Create or push one Okta stakeholder group through SCIM and map it to `STAKEHOLDERS_ROLE`; configure the role grants, each user’s `DEFAULT_ROLE`, and a dedicated default warehouse.
1. Create one Cortex Agent in `PRODUCTION.REPORTING` over the existing semantic views and any approved search services; expose no direct SQL tool.
1. Test the Agent directly with known questions and adversarial questions before introducing ChatGPT; verify generated SQL, results, citations, row access, masking, and failure behavior.
1. Create one Snowflake-managed MCP server in `PRODUCTION.REPORTING` that exposes only the Agent through `CORTEX_AGENT_RUN`.
1. Connect the MCP server to ChatGPT using the intended Okta External OAuth flow and verify that calls originate from the expected client infrastructure, resolve to the expected Snowflake user, and execute under `STAKEHOLDERS_ROLE`.
1. Run the pilot with approximately five users across Finance, Marketing, and other representative stakeholder groups; collect accuracy feedback and record latency, response size, errors, policy outcomes, and cost per question.
1. Use the results to decide whether the internal application should call the Agent Run REST API for streaming, reuse the MCP interface, or wait until a multi-domain routing requirement justifies a gateway.

## Potential future state: four data and policy domains

If the organization develops roughly four distinct data sets, stakeholder groups, and policy boundaries, model each boundary as an access domain rather than simply adding four tools to one large Agent.

- **Recommended isolation pattern** — create four domain-specific semantic-view sets, four least-privileged account roles, four Cortex Agents, and four MCP servers; each role receives access only to its domain’s Agent, MCP server, semantic views, source objects, search services, and policies. For example, use `FINANCE_STAKEHOLDERS_ROLE`, `MARKETING_STAKEHOLDERS_ROLE`, and equivalent roles for the other domains.
- **Shared-client pattern** — if users legitimately need multiple domains and the policy boundaries are enforced reliably by Snowflake, one MCP server can expose multiple precisely named Agent tools. Use this only after testing tool discovery, effective-role selection, and cross-domain access; separate MCP servers are safer when the boundaries are strict.
- **Identity and policy pattern** — keep Okta groups as the source of truth for role membership, map default roles and warehouses through SCIM, and use row access, masking, and other data protection policies for user- or department-specific restrictions within a domain.
- **Agent design pattern** — keep each Agent’s tools and instructions narrow. Avoid a single mega-Agent with access to all four domains unless the same users, policies, and evaluation standards genuinely apply across them.
- **Application pattern** — if stakeholders need one chat experience across the four domains, add an entitlement-aware application router that selects an allowed domain endpoint before invoking the Agent. Do not rely on model tool selection alone to enforce authorization, and do not forward the user’s upstream token blindly to downstream servers.
- **Governance pattern** — maintain a grant matrix, domain-specific evaluation questions, policy tests, cost and latency monitoring, and failover procedures for every Agent and MCP server. A domain should be added only when its semantic definitions, access policy, owner, and evaluation set are ready.

## References

- [Snowflake-managed MCP server](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents-mcp)
- [Cortex Agents Run API](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents-run)
- [Cortex Agents overview and access control](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents)
- [Cortex Agents access control and authentication](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents-setup)
- [Snowflake AI pricing](https://docs.snowflake.com/en/user-guide/snowflake-cortex/pricing)
- [Snowflake SCIM support](https://docs.snowflake.com/en/user-guide/scim-intro)
- [Okta SCIM integration with Snowflake](https://docs.snowflake.com/en/user-guide/scim-okta)
- [Semantic views and verified queries](https://docs.snowflake.com/en/user-guide/views-semantic/semantic-view-yaml-spec)
- [MCP authorization specification, 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization)
- [OpenAI developer mode and MCP apps in ChatGPT](https://help.openai.com/en/articles/12584461-developer-mode-and-mcp-apps-in-chatgpt)
- [OpenAI MCP integration guide](https://developers.openai.com/api/docs/mcp)
- [Deprecated Snowflake-Labs MCP server](https://github.com/Snowflake-Labs/mcp)

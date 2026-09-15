# Snowflake Semantic Views to ChatGPT: Setup and Governance Guide

## Overview

This document covers the end-to-end process of exposing Snowflake semantic views to stakeholders through ChatGPT using Snowflake's managed MCP server infrastructure. The stack is: dbt models (fct/dim marts) -> Snowflake semantic views -> Cortex Analyst -> Snowflake MCP server -> ChatGPT Snowflake plugin.

## Prerequisites

Before starting, you need:

- A Snowflake account with Cortex features enabled
- dbt models producing fct/dim mart tables
- Semantic views built on top of those mart tables (via SQL or Snowsight)
- An Okta tenant configured as your identity provider
- ChatGPT Enterprise or Team workspace (workspace admin access required), or ChatGPT Plus/Pro for individual setup
- ACCOUNTADMIN or equivalent Snowflake role for initial infrastructure setup

## 1. Semantic View Layer

Semantic views sit downstream of your fct/dim mart tables and provide a metadata-rich surface that Cortex Analyst can interpret. They define columns, metrics, relationships, synonyms, and custom instructions that help Cortex translate natural language into SQL.

Organize semantic views by domain. For a multi-team setup (e.g. finance, editorial, growth), use domain-scoped schemas rather than a single shared schema:

- `ANALYTICS_DB.SEMANTIC_FINANCE` -- revenue, costs, margins, financial KPIs
- `ANALYTICS_DB.SEMANTIC_EDITORIAL` -- article performance, pageviews, engagement
- `ANALYTICS_DB.SEMANTIC_GROWTH` -- subscriber acquisition, retention, funnel metrics

This schema-per-domain layout doubles as a governance boundary. Each MCP server lives in its domain's schema, so the schema itself limits what gets exposed.

From the dbt project, organize under `models/semantic/` with subdirectories per domain, each targeting its own Snowflake schema via `dbt_project.yml` config.

## 2. Identity and Access Management (Okta + SCIM)

Okta handles two things: SSO authentication and automated user/role provisioning into Snowflake via SCIM.

SCIM provisioning pushes Okta groups and user assignments into Snowflake as roles. Map your Okta groups to Snowflake roles:

- `okta-finance-analytics` -> `FINANCE_CORTEX_READER`
- `okta-editorial-analytics` -> `EDITORIAL_CORTEX_READER`
- `okta-growth-analytics` -> `GROWTH_CORTEX_READER`

SCIM requires a security integration in Snowflake and a dedicated service user with a SCIM-specific role. Authenticate the SCIM connection with either a Programmatic Access Token (PAT) or External OAuth.

Known issue: Okta SCIM writes `default_role` in whatever case the group name uses. Snowflake stores roles in uppercase and the OAuth token exchange does a case-sensitive lookup. If SCIM sets `default_role = 'finance_cortex_reader'`, authentication fails silently. Normalize with:

```sql
ALTER USER affected_user SET DEFAULT_ROLE = 'FINANCE_CORTEX_READER';
```

Detect mismatches across all users with:

```sql
SELECT name, default_role
FROM SNOWFLAKE.ACCOUNT_USAGE.USERS
WHERE default_role != UPPER(default_role);
```

## 3. Snowflake Role Grants

Each domain role needs SELECT on the semantic views, SELECT on the underlying mart tables (Cortex Analyst requires both), and USAGE on the MCP server, schema, database, and warehouse. Semantic views use owner's rights for direct SQL queries, but Cortex Analyst bypasses that and needs the executing role to have SELECT on the base tables.

```sql
-- Finance example (repeat pattern for editorial, growth)
GRANT USAGE ON DATABASE ANALYTICS_DB TO ROLE FINANCE_CORTEX_READER;
GRANT USAGE ON SCHEMA ANALYTICS_DB.SEMANTIC_FINANCE TO ROLE FINANCE_CORTEX_READER;
GRANT SELECT ON SEMANTIC VIEW ANALYTICS_DB.SEMANTIC_FINANCE.SV_REVENUE TO ROLE FINANCE_CORTEX_READER;
GRANT SELECT ON TABLE ANALYTICS_DB.MARTS.FCT_REVENUE TO ROLE FINANCE_CORTEX_READER;
GRANT SELECT ON TABLE ANALYTICS_DB.MARTS.DIM_ACCOUNTS TO ROLE FINANCE_CORTEX_READER;
GRANT USAGE ON WAREHOUSE CORTEX_WH TO ROLE FINANCE_CORTEX_READER;
```

Scope mart table grants tightly. `FINANCE_CORTEX_READER` gets SELECT on the specific fct/dim tables backing finance semantic views, not on every table in the marts schema. Use FUTURE GRANTS for semantic views within a domain schema so new views automatically inherit the right role access, but do not set up future grants on mart tables to avoid accidental exposure.

## 4. Create Snowflake MCP Servers

Create one MCP server per domain in its respective schema. The `FROM SPECIFICATION` block is a YAML config that declares the tools the MCP server exposes. The `identifier` points at an already-built semantic view. The `description` acts like a system prompt -- the MCP client LLM reads it to decide which tool to route a question to.

```sql
CREATE MCP SERVER ANALYTICS_DB.SEMANTIC_FINANCE.FINANCE_MCP
  FROM SPECIFICATION $$
  tools:
    - name: "finance-analyst"
      type: "CORTEX_ANALYST_MESSAGE"
      identifier: "ANALYTICS_DB.SEMANTIC_FINANCE.SV_REVENUE"
      title: "Finance Analyst"
      description: "Answer questions about revenue, costs, margins, and financial KPIs."
  $$;

GRANT USAGE ON MCP SERVER ANALYTICS_DB.SEMANTIC_FINANCE.FINANCE_MCP
  TO ROLE FINANCE_CORTEX_READER;
```

For production setups, Snowflake recommends wrapping individual tools in a Cortex Agent and exposing the agent as a single `CORTEX_AGENT_RUN` tool. This moves routing logic to the Snowflake side rather than relying on the client LLM to pick the right tool. Particularly useful when a domain needs both a Cortex Analyst (structured queries) and a Cortex Search service (unstructured document search).

Other tool types available in the MCP specification: `CORTEX_SEARCH_SERVICE_QUERY` for semantic search over unstructured content, `SYSTEM_EXECUTE_SQL` for raw read-only SQL access (use cautiously), and `GENERIC` for exposing UDFs and stored procedures as callable tools.

Verify setup:

```sql
SHOW MCP SERVERS IN SCHEMA ANALYTICS_DB.SEMANTIC_FINANCE;
DESCRIBE MCP SERVER ANALYTICS_DB.SEMANTIC_FINANCE.FINANCE_MCP;
```

## 5. OAuth Integration for ChatGPT

ChatGPT authenticates to the MCP server via OAuth. Create a custom OAuth security integration in Snowflake. The redirect URI must exactly match the callback URL that ChatGPT provides during template setup.

```sql
CREATE SECURITY INTEGRATION CHATGPT_OAUTH
  TYPE = OAUTH
  OAUTH_CLIENT = CUSTOM
  OAUTH_CLIENT_TYPE = 'CONFIDENTIAL'
  OAUTH_REDIRECT_URI = '<callback_url_from_chatgpt>'
  OAUTH_ISSUE_REFRESH_TOKENS = TRUE
  OAUTH_REFRESH_TOKEN_VALIDITY = 86400
  ENABLED = TRUE;
```

Retrieve credentials:

```sql
SELECT SYSTEM$SHOW_OAUTH_CLIENT_SECRETS('CHATGPT_OAUTH');
```

This returns a JSON with `oauth_client_id` and `oauth_client_secret`. You will paste these into ChatGPT.

To bind MCP servers to Okta instead of Snowflake's built-in OAuth, set `OAUTH_AUTHORIZATION_SERVER` at the schema or database level to point at an External OAuth security integration configured for Okta. This lets users authenticate through Okta SSO rather than Snowflake's login page.

## 6. ChatGPT Workspace Configuration

In ChatGPT, go to Settings (or Workspace Settings for admins) and open the Plugins section. Search for Snowflake and enable the "Snowflake - Official Template."

For each domain connection, open the template and enter:

- Connection name: e.g. "Finance Data"
- Managed MCP server URL:
  `https://<host_prefix>.snowflakecomputing.com/api/v2/databases/ANALYTICS_DB/schemas/SEMANTIC_FINANCE/mcp-servers/FINANCE_MCP`

Under Advanced OAuth Settings, select "User-Defined OAuth Client" and enter the `oauth_client_id` and `oauth_client_secret` from step 5. Set token endpoint auth method to `client_secret_basic`.

Workspace admins then configure: which workspace roles or groups can see and use each Snowflake connection, action controls for the exposed tools, and app permissions governing when ChatGPT prompts users before invoking a tool.

Each user authenticates individually through Snowflake OAuth. Their default role (provisioned via Okta SCIM) determines what data they can access. No shared service accounts.

## 7. Network and Security

If the Snowflake account uses a network policy or IP allowlist, allow inbound connections from ChatGPT's connector egress IP ranges, published at `https://openai.com/chatgpt-connectors.json`. This list is dynamic and should be automated. This allowlisting is configured in Snowflake and is separate from any ChatGPT workspace IP allowlisting.

## 8. Governance Summary

The access control layers in order:

1. Okta groups define who belongs to which domain audience
1. SCIM provisions those group memberships as Snowflake roles with correct default roles
1. Snowflake RBAC controls object-level access -- semantic views, mart tables, warehouses, MCP servers
1. Schema boundaries scope each MCP server to its domain's semantic views
1. MCP server specification declares exactly which tools and objects are exposed
1. ChatGPT workspace admin controls restrict which members can use each connection and what actions are available
1. Per-user OAuth ensures every query runs under the authenticated user's role with full audit trail in Snowflake query history

No single layer is sufficient on its own. The combination of identity provisioning, Snowflake RBAC, schema isolation, and ChatGPT workspace controls provides defense in depth.

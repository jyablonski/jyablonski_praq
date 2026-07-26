# Snowflake Semantic View Variant

This document describes how to replace Cube with Snowflake Semantic Views while preserving the two application entry points demonstrated by this POC: the FastAPI `/ask` endpoint and the MCP server.

## Current Cube path

```text
Slack / web app -> FastAPI /ask -> OpenAI agent -> Cube /meta and /load -> Postgres
MCP host        -> cube-mcp     -> Cube /meta and /load -> Postgres
```

Cube owns the semantic model, query compilation, and warehouse access. The shared client and policy code restrict the agent to public measures, dimensions, filters, grains, and row limits.

## Snowflake target path

```text
Slack / web app -> FastAPI /ask -> Cortex Analyst or Snowflake SQL -> Snowflake
MCP host        -> snowflake-mcp -> Cortex Analyst or Snowflake SQL -> Snowflake
```

Snowflake Semantic Views would become native schema objects defining logical tables, relationships, dimensions, facts, metrics, synonyms, verified queries, and custom instructions. They integrate with Snowflake privileges, the catalog, and sharing. See the [Semantic Views overview](https://docs.snowflake.com/en/user-guide/views-semantic/overview).

## Recommended implementation

Create a `sales_analysis` Semantic View containing the current `orders` and `customers` concepts. Preserve the approved `monthly_revenue` definition as a metric that sums amounts for completed orders and uses `order_date` as its time basis.

Use Cortex Analyst for natural-language questions when Snowflake should own SQL generation. Its REST API accepts a question and a fully qualified Semantic View name and returns text, suggestions, and generated SQL. See the [Cortex Analyst REST API](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-analyst/rest-api).

Keep the existing `/ask` and MCP contracts stable where possible. Replace `CubeTools` with a shared `SnowflakeAnalyticsClient` that can:

- call Cortex Analyst with the selected Semantic View;
- return the generated SQL and answer metadata for tracing;
- optionally execute approved Semantic SQL through the Snowflake SQL API;
- enforce row, time-range, query-cost, and user-authorization policies.

The MCP tools could retain their names—`search_semantic_model`, `get_metric_definition`, and `run_semantic_query`—so connected clients do not need to change. Their implementations would use Snowflake metadata and Cortex Analyst or Semantic SQL instead of Cube's `/meta` and `/load` endpoints.

## Security and operations

Use Snowflake roles and privileges as the primary data boundary. Derive user identity from Slack, the web application, or the MCP connection; never trust model-supplied identity fields. Store Snowflake credentials server-side, audit request IDs and generated SQL, enforce query limits, and avoid exposing arbitrary SQL execution to the model.

## Migration sequence

1. Define and test the Semantic View from the existing Cube YAML and seeded questions.
1. Add verified queries, synonyms, descriptions, and custom instructions for common stakeholder language.
1. Implement `SnowflakeAnalyticsClient` behind the existing shared adapter interface.
1. Add Snowflake-backed policy tests for metric visibility, filters, time ranges, and limits.
1. Point `/ask` at the new client and compare answers against Cube during a transition period.
1. Point `snowflake-mcp` at the same client and preserve the existing MCP tool contract.
1. Enable production roles, authentication, auditing, and cost controls before stakeholder access.

Snowflake recommends native Semantic Views for new implementations; Cube remains preferable when the semantic layer must stay warehouse-independent or when the application needs to own more of the agent and query orchestration.

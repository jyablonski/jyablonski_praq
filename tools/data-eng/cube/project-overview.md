# Sample Cube Analytics Project

## What this project demonstrates

This project shows how to let LLMs and agentic workflows use company data without giving the model direct access to the database.

We do that by setting up a semantic layer where we define business metrics, dimensions, relationships, filters, and business definitions in advance. In this sample, `monthly_revenue` means the sum of amounts from completed orders, grouped by the order date.

The semantic model is governed and hardcoded ahead of time, but the specific question and query are generated at runtime within the allowed semantic surface.

## How the data path works

Cube exposes APIs that accept semantic queries. Cube applies the definitions and joins from the semantic layer, queries Postgres on our behalf, and returns governed results.

The LLM does not receive Postgres credentials and does not query the underlying tables directly. It receives metadata and result rows, analyzes them, and returns a final answer to the user.

```text
Semantic definitions -> Cube API -> Postgres
                              -> governed result rows -> LLM -> user answer
```

## Two ways to use the project

### MCP: reusable AI-host integration

The project exposes a Cube MCP server at `http://localhost:8001/mcp` using Streamable HTTP. Local developers can connect it to Codex, Cursor, Claude Desktop, or another MCP-compatible LLM tool. Stakeholders could use the same pattern through a compatible ChatGPT or other AI client after deploying it behind HTTPS and authentication.

The MCP host owns the conversation and decides when to call tools such as `search_semantic_model`, `get_metric_definition`, and `run_semantic_query`.

### REST `/ask`: application-owned agentic workflow

The FastAPI `/ask` endpoint is for applications we own, such as Slack slash commands, Teams bots, internal web apps, scheduled reports, or custom dashboards.

It runs an OpenAI agent loop, validates the generated tool arguments, calls Cube, gives the results back to the model, and returns a stakeholder-facing answer. The application owns identity, user experience, orchestration, and response formatting.

## Shared governance

The MCP and REST paths reuse the same Cube client and query policies. Both enforce public metrics and dimensions, supported filters and time grains, read-only structured queries, and result limits.

The main difference is who owns the conversation: an external AI host owns it for MCP, while our application owns it for `/ask`.

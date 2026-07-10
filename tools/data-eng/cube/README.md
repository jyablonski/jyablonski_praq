# Cube semantic layer POC

This stack runs Cube Core and a small AI analytics agent over a seeded PostgreSQL database. It contains 360 orders across 12 months, with completed revenue increasing over time.

## Start

Export an OpenAI API key for the agent, then start the complete stack from this directory:

```sh
export OPENAI_API_KEY='your-api-key'
docker compose up --build
```

The key is passed directly into the agent container and is not stored in the repository. The agent defaults to `gpt-5.4-mini`; set `OPENAI_MODEL` before starting Compose to override it. Cube and Postgres still start without an API key, but `POST /ask` returns `503` until one is configured.

Open the Cube Developer Playground at <http://localhost:4000>. Select the `orders.monthly_revenue` measure and the `orders.order_date` time dimension with month granularity. Add `customers.segment` or `customers.region` to slice the result.

## Consuming the semantic layer

Any application, dashboard, BI tool, or other consumer that needs the governed metrics defined here must query Cube through one of its supported interfaces:

- REST API: `http://localhost:4000/cubejs-api/v1/load`
- GraphQL API: `http://localhost:4000/cubejs-api/graphql`
- SQL API: PostgreSQL-compatible connections on `localhost:15432`
- WebSockets or a supported Cube frontend integration

Consumers should not query the underlying Postgres tables directly. Doing so bypasses Cube's measure filters, joins, metadata, and other semantic definitions—for example, the rule that monthly revenue includes only completed orders.

## AI agents and natural-language queries

Cube Core is headless and does not include a built-in chat interface, but an LLM application or AI agent can use it as the governed execution layer for text-to-SQL or text-to-query workflows:

1. Read `/cubejs-api/v1/meta` so the agent knows the available measures, dimensions, descriptions, types, and formats.
1. Give that metadata and the stakeholder's question to the LLM, instructing it to use only exposed Cube members.
1. Have the LLM produce either a structured REST query or Semantic SQL for Cube's PostgreSQL-compatible SQL API.
1. Validate the generated query, apply row and time-range limits, and execute it through Cube rather than directly against Postgres.
1. Give the returned rows to the LLM to explain or visualize for the stakeholder.

For example, the question "How is monthly revenue trending?" could be translated into this Semantic SQL query:

```sql
SELECT
  DATE_TRUNC('month', order_date) AS month,
  MEASURE(monthly_revenue) AS monthly_revenue
FROM orders
GROUP BY 1
ORDER BY 1;
```

Because the query uses `MEASURE(monthly_revenue)`, Cube applies the governed definition that includes only completed orders. The agent should receive Cube credentials with read-only access and should never receive a direct warehouse connection. In production, also enforce authentication, member-level access, query limits, and logging outside of the LLM. The hosted Cube platform additionally provides MCP and Chat API integrations for connecting supported AI assistants directly; this Cube Core POC demonstrates the custom-agent API and Semantic SQL path.

### Agent service

The POC includes a FastAPI agent at <http://localhost:8000>. It uses the OpenAI Responses API tool-calling loop and exposes three controlled tools:

- `search_semantic_model`: searches Cube's public Meta API members.
- `get_metric_definition`: returns the governed measure description, format, owner, certification, and calculation metadata.
- `run_semantic_query`: validates and runs a structured Cube REST query.

The agent deliberately generates structured Cube queries rather than arbitrary SQL. The allowlist in `agent/policies.py` validates every measure, dimension, filter, time grain, order field, and limit against Cube metadata before execution. Cube then compiles the accepted request into warehouse SQL. The agent container has no Postgres credentials or network code for querying Postgres directly.

```text
POST /ask
    -> OpenAI model chooses a tool
    -> agent validates the tool arguments
    -> agent calls Cube Meta or REST API
    -> Cube queries Postgres using the governed model
    -> tool result returns to the model
    -> model returns a stakeholder-facing answer
```

Check the agent configuration:

```sh
curl 'http://localhost:8000/health'
```

Ask a question:

```sh
curl --request POST 'http://localhost:8000/ask' \
  --header 'Content-Type: application/json' \
  --data '{
    "question": "How is monthly revenue trending across 2025?",
    "user_context": {"user_id": "poc-user"},
    "include_trace": true
  }'
```

`include_trace` returns the tool calls and governed Cube results for inspection. This is useful for a POC but should normally be disabled or access-controlled in a production stakeholder interface.

### Agent limits and evaluations

Compose configures a maximum of five tool calls, 100 result rows, and a 15-second Cube request timeout. These values can be changed through `AGENT_MAX_TOOL_CALLS`, `AGENT_MAX_ROWS`, and `AGENT_QUERY_TIMEOUT_SECONDS`.

Example evaluation cases live in `agent/evaluations.yml` and are also visible through:

```sh
curl 'http://localhost:8000/evaluations'
```

Run the read-only policy unit tests:

```sh
docker compose run --rm agent python -m unittest discover --start-directory tests
```

This remains a development POC: `/ask` has no caller authentication, `user_context` is illustrative rather than trusted identity, and Cube itself is running with authentication disabled. Production deployment requires authenticated user identity, server-generated authorization context, access policies, audit storage, rate limits, and secret management.

The implementation follows the current [OpenAI model guidance](https://developers.openai.com/api/docs/models) and uses function calling through the Responses API.

## REST API example

Development mode disables API authentication. This query returns completed revenue grouped by month:

```sh
curl --get 'http://localhost:4000/cubejs-api/v1/load' \
  --data-urlencode 'query={"measures":["orders.monthly_revenue"],"timeDimensions":[{"dimension":"orders.order_date","granularity":"month"}],"order":{"orders.order_date":"asc"}}'
```

## Metadata API example

Cube's Meta API returns the cubes, measures, dimensions, types, descriptions, formats, and custom metadata exposed by the semantic layer:

```sh
curl 'http://localhost:4000/cubejs-api/v1/meta'
```

With `jq`, this query returns just the `monthly_revenue` measure metadata that could be synchronized to a data catalog:

```sh
curl --silent 'http://localhost:4000/cubejs-api/v1/meta' \
  | jq '.cubes[] | select(.name == "orders") | .measures[] | select(.name == "orders.monthly_revenue")'
```

## SQL API example

The SQL API is exposed on port `15432`. Any database name is accepted by the Cube SQL API; this example uses `cube`:

```sh
PGPASSWORD=cube_sql_password psql \
  --host localhost \
  --port 15432 \
  --username cube \
  --dbname cube \
  --command "SELECT DATE_TRUNC('month', order_date) AS month, MEASURE(monthly_revenue) AS monthly_revenue FROM orders GROUP BY 1 ORDER BY 1;"
```

## Tear down

Stop the containers and delete the seeded Postgres volume:

```sh
docker compose down --volumes
```

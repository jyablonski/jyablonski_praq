# Cube semantic layer POC

This stack runs Cube Core and a small AI analytics agent over a seeded PostgreSQL database. It contains 360 orders across 12 months, with completed revenue increasing over time.

## Start

Generate a Cube API secret, optionally export an OpenAI API key for the agent, then start the complete stack from this directory:

```sh
export CUBEJS_API_SECRET="$(openssl rand -hex 32)"
export OPENAI_API_KEY='your-api-key'
docker compose up --build
```

The secrets are passed directly into their containers and are not stored in the repository. `CUBEJS_API_SECRET` is required because Cube runs with development mode disabled; the agent and MCP adapter use it to generate short-lived JWTs for Cube. The agent defaults to `gpt-5.4-mini`; set `OPENAI_MODEL` before starting Compose to override it. Cube and Postgres still start without an OpenAI API key, but `POST /ask` returns `503` until one is configured.

The Cube Developer Playground and PostgreSQL-compatible SQL API are disabled to reduce the local runtime surface. Cube exposes its authenticated REST and GraphQL APIs on <http://localhost:4000>.

## Consuming the semantic layer

Any application, dashboard, BI tool, or other consumer that needs the governed metrics defined here must query Cube through one of its supported interfaces:

- REST API: `http://localhost:4000/cubejs-api/v1/load`
- GraphQL API: `http://localhost:4000/cubejs-api/graphql`
- WebSockets or a supported Cube frontend integration

Consumers should not query the underlying Postgres tables directly. Doing so bypasses Cube's measure filters, joins, metadata, and other semantic definitions—for example, the rule that monthly revenue includes only completed orders.

## AI agents and natural-language queries

Cube Core is headless and does not include a built-in chat interface, but an LLM application or AI agent can use it as the governed execution layer for text-to-query workflows:

1. Read `/cubejs-api/v1/meta` so the agent knows the available measures, dimensions, descriptions, types, and formats.
1. Give that metadata and the stakeholder's question to the LLM, instructing it to use only exposed Cube members.
1. Have the LLM produce a structured REST query.
1. Validate the generated query, apply row and time-range limits, and execute it through Cube rather than directly against Postgres.
1. Give the returned rows to the LLM to explain or visualize for the stakeholder.

For example, the question "How is monthly revenue trending?" could be translated into this Cube REST query:

```json
{
  "measures": ["orders.monthly_revenue"],
  "timeDimensions": [
    {
      "dimension": "orders.order_date",
      "granularity": "month"
    }
  ],
  "order": {
    "orders.order_date": "asc"
  }
}
```

Because the query uses `orders.monthly_revenue`, Cube applies the governed definition that includes only completed orders. The agent receives Cube API credentials and never receives a direct warehouse connection. In production, also enforce caller authentication, member-level access, query limits, and logging outside of the LLM. The hosted Cube platform additionally provides MCP and Chat API integrations for connecting supported AI assistants directly; this Cube Core POC demonstrates the custom-agent and structured REST query path.

### MCP service

The Compose stack also includes an MCP adapter at <http://localhost:8001/mcp>. It exposes the same governed Cube surface to MCP-compatible development hosts such as an IDE assistant or desktop AI client:

- `search_semantic_model`: discover public measures and dimensions.
- `get_metric_definition`: inspect the governed definition and metadata for a measure.
- `run_semantic_query`: execute a structured, read-only Cube query.

The MCP service contains no LLM and does not query Postgres directly. The MCP host supplies the model and orchestration; the service validates requests and calls Cube's Meta and REST APIs. The adapter and FastAPI agent both import the shared Cube client and query policy from `shared/`, so public-member checks, supported filters, time grains, and row limits remain enforced server-side through either interface.

For an MCP client that supports Streamable HTTP connections, configure the server URL as:

```text
http://localhost:8001/mcp
```

After connecting, a development assistant can ask questions such as "How is monthly revenue trending across 2025?" or "What is the approved definition of monthly revenue?" The host will discover the three tools and decide when to call them. The MCP path does not require the `OPENAI_API_KEY` used by the separate FastAPI `/ask` service.

This POC MCP endpoint has no caller authentication, and its empty `user_context` is not an authenticated identity. Production use requires authenticated MCP connections, server-derived authorization context, Cube authentication, audit logging, rate limits, and secret management.

### Potential consumers and use cases

The two interfaces are intended for different consumers while sharing the same governed Cube logic:

- Internal web app: provide a search box, charts, saved questions, and team-specific response formatting through `POST /ask`.
- Slack or Teams command: route a slash command or bot message to `/ask` and return a concise answer with links to a dashboard or trace.
- Scheduled reporting: call `/ask` from a workflow that sends recurring metric summaries to email or a team channel.
- Local developer assistants: connect Cursor, Claude Desktop, Codex, or another MCP-compatible tool using a Streamable HTTP connection to `http://localhost:8001/mcp` for governed metric discovery and read-only analysis during development.
- Stakeholder AI clients: connect an authenticated, reachable MCP deployment to a compatible ChatGPT or other AI client so users can ask questions without receiving warehouse credentials.
- Data and analytics development: use MCP to inspect approved metric definitions, validate proposed breakdowns, and investigate seeded or development data without granting direct Postgres access.

The `/ask` path is best when the team owns the product experience, identity, and answer format. The MCP path is best when an existing AI host owns the conversation and needs a reusable Cube integration. Neither path should bypass Cube by querying the underlying Postgres tables directly.

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
    "include_trace": false
  }'
```

#### Real request walkthrough (Simple)

For the question `How is monthly revenue trending across 2025?`, the simplified request lifecycle is:

1. `/ask` receives the user's JSON request and validates the request fields, including the question text, optional user context, and trace flag.
1. The agent sends the question text, the system instructions, and `TOOL_SCHEMAS` to the OpenAI Responses API. The schemas tell the model which functions exist, what each function does, and which JSON arguments each function accepts; they do not contain the function implementations.
1. The model decides whether it can answer directly or needs data. For this question, the system instructions tell it to use the governed workflow: search the semantic model, load metric definitions, and then run a semantic query. Because this request does not set `tool_choice`, the model makes the tool-use decision itself.
1. The model emits a `search_semantic_model` function call with the user's question. The agent receives the call, parses its JSON arguments, and dispatches it to the local `CubeTools` implementation.
1. `search_semantic_model` reads Cube's Meta API and returns matching public members, such as measures and dimensions. Its result has the shape `{"members": [...], "total_public_members": integer}`.
1. The agent packages that result as a `function_call_output` and sends it back to the model in a follow-up Responses API request. The model now has the search results as context for its next decision.
1. The model chooses `get_metric_definition` for `orders.monthly_revenue`. The agent executes it and returns the governed metric metadata, including its description, type, format, owner, certification, calculation, and time basis.
1. After the model has discovered and defined the measure, it emits a `run_semantic_query` call with the measure, monthly `orders.order_date` grain, 2025 date range, ordering, filters, and row limit. The agent checks that the required search and definition steps succeeded before allowing this call to run.
1. The agent validates and normalizes the query against Cube's public metadata and policy allowlist. It rejects unknown members, unsupported fields, invalid filters, unsafe limits, and queries that do not follow the required workflow. It then calls Cube's `/cubejs-api/v1/load` endpoint.
1. Cube executes the governed query against Postgres and returns data rows. The agent converts the Cube response into a tool result with `request_id`, the validated `query`, `data` rows, `last_refresh_time`, `row_count`, and `user_context_supplied`.
1. The agent sends that query result back to the model as another `function_call_output`. The model evaluates the returned rows against the original question and the metric definition. It may request another tool call for a breakdown or comparison, or it may decide that it has enough information to answer.
1. When the model returns no more function calls, the agent reads `response.output_text` as the final natural-language answer. `/ask` returns that answer, the total `tool_calls`, and the optional `trace` containing every tool's arguments and result.

If a tool call fails validation or Cube returns an error, the agent sends the model an error result such as `{"ok": false, "error": "..."}` instead of pretending that the query succeeded. The model can then correct its request, explain the limitation, or finish without a data-backed answer.

#### Real request walkthrough (Detailed)

For the request `How is monthly revenue trending across 2025?`, the agent follows this sequence:

1. The FastAPI `/ask` endpoint receives the JSON request, validates the `question`, `user_context`, and `include_trace` fields, and passes the question text to `_run_agent`.

1. `_run_agent` sends the question to the OpenAI Responses API as `input`. It also sends `TOOL_SCHEMAS`, which describe the three available functions, their purposes, and the JSON arguments each function accepts. The model does not discover tools by querying Cube; the application gives it the tool definitions on every Responses API call.

   ```python
   response = client.responses.create(
       model=model,
       instructions=SYSTEM_PROMPT,
       input=request.question,
       tools=TOOL_SCHEMAS,
   )
   ```

1. Based on the question and the supplied schemas, the model chooses `search_semantic_model` and returns a function call such as:

   ```json
   {
     "name": "search_semantic_model",
     "arguments": {"question": "How is monthly revenue trending across 2025?"}
   }
   ```

   The agent dispatches that function to `CubeTools.search_semantic_model`, which reads Cube's Meta API at `/cubejs-api/v1/meta` and returns matching public measures and dimensions. The application sends that result back to the model as a `function_call_output`.

1. The model then chooses `get_metric_definition` for the measure it needs:

   ```json
   {
     "name": "get_metric_definition",
     "arguments": {"metric_name": "orders.monthly_revenue"}
   }
   ```

   The agent reads the metric definition from Cube metadata and returns its description, type, format, cube, and custom metadata to the model. The agent requires this definition step for every measure used in a query.

1. With the public member and its definition established, the model chooses `run_semantic_query` and supplies a structured request:

   ```json
   {
     "name": "run_semantic_query",
     "arguments": {
       "measures": ["orders.monthly_revenue"],
       "dimensions": [],
       "time_dimension": {
         "dimension": "orders.order_date",
         "granularity": "month",
         "date_range": ["2025-01-01", "2025-12-31"]
       },
       "filters": [],
       "order_by": "orders.order_date",
       "order_direction": "asc",
       "row_limit": 100
     }
   }
   ```

1. The agent validates these arguments against the public Cube metadata and policy allowlist. It rejects unknown measures or dimensions, unsupported filters and time grains, arbitrary query fields, excessive limits, and queries that skip the required search or metric-definition steps. It then normalizes the tool arguments into the Cube REST query:

   ```json
   {
     "measures": ["orders.monthly_revenue"],
     "dimensions": [],
     "timeDimensions": [{
       "dimension": "orders.order_date",
       "granularity": "month",
       "dateRange": ["2025-01-01", "2025-12-31"]
     }],
     "filters": [],
     "order": {"orders.order_date": "asc"},
     "limit": 100,
     "timezone": "UTC"
   }
   ```

1. `CubeTools.run_semantic_query` sends that normalized query to Cube's `/cubejs-api/v1/load` endpoint. Cube applies the governed `orders.monthly_revenue` definition, queries Postgres, and returns the monthly rows. The agent sends those rows and query details back to the model as another `function_call_output`.

1. When there are no more function calls, the model writes the stakeholder-facing answer. `/ask` returns that answer, the number of tool calls, and—when `include_trace` is true—the tool arguments and governed results used to produce it.

In short, the model decides which available function to call from the schemas supplied by the application, while the agent—not the model—executes the functions, enforces the query policy, and controls access to Cube.

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

This remains a development POC: `/ask` has no caller authentication and `user_context` is illustrative rather than trusted identity. Cube API authentication protects the service boundary but does not yet implement per-user or row-level authorization. Production deployment requires authenticated user identity, server-generated authorization context, access policies, audit storage, rate limits, and managed secrets.

The implementation follows the current [OpenAI model guidance](https://developers.openai.com/api/docs/models) and uses function calling through the Responses API.

## REST API example

Generate a short-lived local Cube token from the shared secret inside the agent container:

```sh
export CUBE_API_TOKEN="$(docker compose exec --no-TTY agent python -c 'import os,time,jwt; now=int(time.time()); print(jwt.encode({"iat":now,"exp":now+300}, os.environ["CUBE_API_SECRET"], algorithm="HS256"))')"
```

This authenticated query returns completed revenue grouped by month:

```sh
curl --get 'http://localhost:4000/cubejs-api/v1/load' \
  --header "Authorization: ${CUBE_API_TOKEN}" \
  --data-urlencode 'query={"measures":["orders.monthly_revenue"],"timeDimensions":[{"dimension":"orders.order_date","granularity":"month"}],"order":{"orders.order_date":"asc"}}'
```

## Metadata API example

Cube's Meta API returns the cubes, measures, dimensions, types, descriptions, formats, and custom metadata exposed by the semantic layer:

```sh
curl --header "Authorization: ${CUBE_API_TOKEN}" \
  'http://localhost:4000/cubejs-api/v1/meta'
```

With `jq`, this query returns just the `monthly_revenue` measure metadata that could be synchronized to a data catalog:

```sh
curl --silent \
  --header "Authorization: ${CUBE_API_TOKEN}" \
  'http://localhost:4000/cubejs-api/v1/meta' \
  | jq '.cubes[] | select(.name == "orders") | .measures[] | select(.name == "orders.monthly_revenue")'
```

## Tear down

Stop the containers and delete the seeded Postgres volume:

```sh
docker compose down --volumes
```

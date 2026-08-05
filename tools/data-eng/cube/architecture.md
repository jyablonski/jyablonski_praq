# Cube analytics agent architecture

High-level request flow for the FastAPI agent in this directory, including its iterative tool-calling loop and policy boundaries.

```mermaid
flowchart LR
    User[User or client]

    subgraph App[Application]
        API[FastAPI agent<br/>POST /ask]
        Orchestrator[_run_agent<br/>while True<br/>previous_response_id<br/>5-call budget]
        Gate[Sequencing gate<br/>agent/app.py<br/>search + definitions required]
        Tools[CubeTools dispatch<br/>tools.py]
        QueryPolicy[Query validation<br/>policies.py]
        Context[Optional user_context<br/>illustrative only<br/>not trusted identity]
    end

    subgraph OpenAI[Provider: OpenAI]
        Model[Responses API<br/>runtime model: OPENAI_MODEL<br/>_run_agent fallback: gpt-5.6-luna]
    end

    subgraph Cube[Provider: Cube]
        Meta[Meta API<br/>discover members and definitions]
        Load[REST Load API<br/>run governed semantic query]
        Auth[Short-lived HS256 JWT<br/>shared service secret]
    end

    subgraph Postgres[Provider: PostgreSQL]
        Warehouse[(Sales warehouse<br/>seeded Postgres data)]
    end

    User -->|POST /ask<br/>question + user_context| API
    API -.-> Context
    API --> Orchestrator
    Orchestrator -->|Responses request<br/>instructions + tool schemas| Model
    Model -->|function call or final answer| Orchestrator

    Orchestrator -->|tool call| Gate
    Gate -->|allowed call| Tools
    Gate -->|rejected call| ErrorResult[Error result<br/>ok: false + error]

    Tools -->|search_semantic_model<br/>GET /meta| Meta
    Auth -.-> Meta
    Auth -.-> Load
    Meta -->|members| Tools
    Tools -->|get_metric_definition<br/>GET /meta| Meta
    Meta -->|metric definition| Tools
    Tools -->|run_semantic_query| QueryPolicy
    QueryPolicy -->|self.get_meta()<br/>GET /meta| Meta
    Meta -->|members for validation| QueryPolicy
    QueryPolicy -->|validated query<br/>GET /load| Load
    QueryPolicy -->|rejected query| ErrorResult
    Load -->|generated SQL| Warehouse
    Warehouse -->|query rows| Load
    Load -->|governed result set| Tools
    Tools -->|tool result| Orchestrator
    ErrorResult -->|function_call_output<br/>model can re-plan| Orchestrator

    Orchestrator -->|function_call_output<br/>previous_response_id| Model
    Orchestrator -->|200 response<br/>answer + optional trace| API
    API -->|response body| User

    Orchestrator -.->|repeat until no calls<br/>or budget is exceeded| Orchestrator

    classDef app fill:#e8f1ff,stroke:#2563eb,color:#111827
    classDef provider fill:#fff7ed,stroke:#ea580c,color:#111827
    classDef data fill:#ecfdf5,stroke:#059669,color:#111827
    class API,Orchestrator,Gate,Tools,QueryPolicy,Context app
    class Model,Meta,Load,Auth provider
    class Warehouse data
```

The model chooses tools from the schemas supplied by the FastAPI app. The orchestration gate enforces call ordering, while `validate_and_normalize_query` enforces the Cube query allowlist. Both policy failures become tool outputs so the model can correct its plan and continue the loop. A complete turn can call Cube's `/meta` endpoint three times: search, metric definition, and query validation. The shared Cube client signs a short-lived JWT for each Cube HTTP client; this authenticates the service but is not yet a per-user authorization mechanism.

Cube runs with both development mode and the SQL API disabled. Its cache and query queue use the single-instance in-memory driver, which avoids the embedded Cube Store process for this small REST-only POC. This configuration intentionally omits Cube Store pre-aggregations and distributed cache/queue behavior.

## MCP adapter path

Compose also runs a separate `cube-mcp` service on host port `8001`. It exposes `search_semantic_model`, `get_metric_definition`, and `run_semantic_query` through MCP Streamable HTTP at `/mcp` for external development hosts. Those hosts perform the model orchestration; the adapter and FastAPI agent both import the shared Cube client and query policy, then call Cube's `/meta` and `/load` APIs. This is an interoperability layer for MCP-compatible clients, not a replacement for Cube's semantic layer or the FastAPI agent.

For Codex or another local MCP client, select `Streamable HTTP` and configure `http://localhost:8001/mcp`. The root URL and a browser GET are not interactive health checks for this protocol; the client must send MCP protocol requests to `/mcp`.

Model configuration is currently inconsistent: Docker Compose supplies `gpt-5.4-mini` when `OPENAI_MODEL` is unset, `_run_agent` falls back to `gpt-5.6-luna`, and `/health` reports `gpt-5.4-mini` when unset. The diagram labels the model by the runtime setting and shows the `_run_agent` fallback explicitly.

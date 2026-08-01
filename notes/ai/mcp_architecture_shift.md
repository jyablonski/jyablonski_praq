# MCP Servers: Deployment Targets and the 2026-07-28 Architecture Shift

## What an MCP server provides

Model Context Protocol (MCP) standardizes how an AI host connects to external context and capabilities. The host contains an MCP client, exposes selected capabilities to the model, executes approved calls through the server, and returns the results to the model. The LLM model does not connect to the MCP server directly.

Servers expose three primary primitives:

- Tools: model-controlled functions that retrieve information or perform actions, such as querying a warehouse or creating a ticket.
- Resources: application-controlled, URI-addressed content, such as schema documentation, files, or dbt manifests.
- Prompts: user-controlled templates that a host can present as commands or workflow starters.

The portability benefit is one protocol implementation rather than one integration per host. Portability is not automatic, however: hosts differ in supported protocol revisions, primitives, authentication methods, approval flows, and administrative controls.

## Two deployment shapes, one application core

Keep tool, resource, and prompt implementations independent of transport. Put stdio and HTTP concerns at the edge so the same application logic can serve local and remote clients without maintaining separate business logic.

### Local clients: stdio

- Typical hosts include Claude Code, Codex, Cursor, and VS Code.
- The client launches the MCP server as a subprocess and exchanges newline-delimited JSON-RPC messages over stdin and stdout.
- Only the MCP transport is local. The server may still call databases, cloud APIs, or other network services, and the host may send model context to a cloud LLM.
- The MCP HTTP authorization specification does not apply to stdio. The server normally receives credentials through its process environment, local credential stores, or the host's execution environment.
- The stdio transport remains standard in `2026-07-28`, but its protocol lifecycle did change: the `initialize` handshake is gone for the new revision, per-request metadata is required, and clients can use `server/discover` for capability and version discovery.
- stdio is usually the simplest choice when the server should run with one developer's local identity and lifecycle.

### Hosted clients: Streamable HTTP

- Web products such as Claude and ChatGPT connect to remote MCP endpoints rather than launching stdio subprocesses.
- Use the current Streamable HTTP transport: a single MCP endpoint accepts POST requests and returns either one JSON response or a request-scoped Server-Sent Events (SSE) stream.
- Internet-hosted endpoints should use HTTPS. The endpoint must be reachable from the provider's infrastructure unless the provider offers an approved private-connectivity mechanism. ChatGPT now offers Secure MCP Tunnel for private, on-premises, and developer-machine servers, so public exposure is not an absolute requirement.
- For multi-user deployments, prefer OAuth so the server receives per-user identity and can enforce authorization at the resource and action level. Authless or shared-credential configurations may be suitable for narrow cases but do not provide per-user authorization.
- Treat transport support and product support separately. A server can conform to the MCP specification while still using features that a particular web product does not yet expose.

Current product behavior as of 2026-08-01:

- Claude custom connectors are available on Pro, Max, Team, and Enterprise. Owners or Primary Owners configure organization connectors for Team and Enterprise; users authenticate individually and enable the connector or individual tools. Anthropic documents authless and OAuth servers and currently documents both legacy SSE and Streamable HTTP, while warning that legacy SSE support may be deprecated.
- ChatGPT full MCP support is in beta for Business, Enterprise, and Edu; Pro users have more limited read/fetch custom-app support. Only admins or owners publish workspace apps. Enterprise and Edu can grant developer access and app access through RBAC, while Business limits developer-mode deployment to admins and owners.
- ChatGPT stores an approved snapshot of tool definitions. Enterprise and Edu admins can refresh and review added or changed actions; Business currently requires recreating and republishing an app to change published tools or metadata.

These product rules change independently of the MCP specification and should be rechecked immediately before rollout.

## The pre-2026 architecture

MCP launched in `2024-11-05` with stdio and the original HTTP+SSE transport. Streamable HTTP replaced HTTP+SSE in `2025-03-26`, but revisions through `2025-11-25` retained connection-oriented features:

- An `initialize` request and `notifications/initialized` notification negotiated the protocol version, peer identity, and capabilities once for a logical connection.
- A Streamable HTTP server could assign an `Mcp-Session-Id`; sessions were optional, not mandatory. A client receiving one had to return it on later requests.
- A client could open a standalone GET SSE stream, and a server could issue JSON-RPC requests such as sampling, elicitation, and roots requests over an active SSE channel.
- Streams could support resumption and redelivery through SSE event IDs and `Last-Event-ID`.

### Why the connection-oriented features complicated production

When a deployment used sessions, resumable streams, subscriptions, or server-initiated requests, successive messages had to reach the correct state. Multi-replica services therefore needed sticky routing, shared session state, or another coordination layer. Those requirements complicated round-robin load balancing, serverless runtimes, rolling deploys, failure recovery, and autoscaling. Basic servers that did not use those optional features could already operate more simply.

## What `2026-07-28` changed

The revision is a breaking wire-protocol redesign, not merely a new default for HTTP servers. Its core is stateless and request-oriented across transports.

| Area | SEP | Effect |
| ------------------------ | ---- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Sessions | 2567 | Removes protocol-level sessions and `Mcp-Session-Id`; servers use explicit state handles when an application workflow spans calls. |
| Lifecycle | 2575 | Removes `initialize` and `notifications/initialized`; adds required per-request protocol and capability metadata plus `server/discover`. |
| Server-to-client input | 2322 | Replaces server-initiated JSON-RPC requests with Multi Round-Trip Requests (MRTR): the server returns `resultType: "input_required"`, and the client retries the original request with `inputResponses` and the opaque `requestState`. |
| Result shape | 2322 | Requires every new-revision result to declare `resultType`, normally `"complete"`; clients treat a missing field from a legacy peer as complete. |
| HTTP routing | 2243 | Requires `Mcp-Method` on HTTP JSON-RPC requests and `Mcp-Name` for `tools/call`, `resources/read`, and `prompts/get`; the server must reject header/body mismatches. |
| Caching | 2549 | Adds required `ttlMs` and `cacheScope` freshness and sharing hints to list results and resource reads. |
| Long-lived notifications | 2575 | Replaces the standalone GET stream and resource subscription methods with an opt-in `subscriptions/listen` POST response stream. |
| Tasks | 2663 | Moves Tasks from the experimental core into the `io.modelcontextprotocol/tasks` extension, removes `tasks/list` and blocking `tasks/result`, and uses `tasks/get`, `tasks/update`, and `tasks/cancel`. |
| Extensions | 2133 | Adds a first-class, independently versioned extension mechanism negotiated through client and server capabilities. |
| Tool schemas | 2106 | Allows full JSON Schema 2020-12 input and output schemas, including composition and references, subject to validation and resource limits. |
| Deprecation lifecycle | 2596 | Defines Active, Deprecated, and Removed states and a minimum 12-month deprecation window. |

Additional transport consequences:

- Streamable HTTP is POST-only in the new revision. HTTP GET and DELETE, `Last-Event-ID`, resumable response streams, and protocol-managed session termination are gone.
- Servers no longer initiate JSON-RPC requests. Request-scoped progress and logging notifications may still flow before the final response on that request's SSE stream.
- Streaming remains useful but no longer implies a session. A normal request may stream progress, while `subscriptions/listen` provides a separate opt-in stream for list changes and resource updates.
- `MCP-Protocol-Version` mirrors the request body's protocol version on HTTP. `Mcp-Method` and, where applicable, `Mcp-Name` let gateways route and apply policy without parsing JSON, but the server must validate the headers against the body to prevent inconsistent enforcement.
- Cross-call application state remains valid. A server can mint an explicit handle such as `query_id` or `browser_id`, persist the corresponding state in a durable store, return the handle, and accept it as an ordinary argument on later calls. Do not rely on later calls reaching the same process.
- Cache fields are protocol hints, not permission checks. A server must set `cacheScope: "private"` for user-specific results and must still authorize every request that reaches it.

## Deprecations and compatibility

Roots, Sampling, and Logging were deprecated by SEP-2577. The legacy HTTP+SSE transport was formally classified as deprecated, and OAuth Dynamic Client Registration was deprecated in favor of Client ID Metadata Documents. New implementations should use tool parameters, resource URIs, or server configuration instead of Roots; direct provider integration instead of Sampling; stderr for stdio or OpenTelemetry for structured observability instead of MCP Logging; Streamable HTTP instead of HTTP+SSE; and Client ID Metadata Documents where supported.

Deprecated features remain in the specification during the minimum 12-month window and cannot be removed before 2027-07-28. That guarantee does not require every host or SDK to implement every deprecated feature, and it does not guarantee that a `2026-07-28`-only peer can communicate with a `2025-11-25`-only peer.

Mixed-version support requires deliberate compatibility code. A modern client can probe with `server/discover` and fall back to the legacy `initialize` lifecycle when the server does not speak the new era. A server can expose both eras if its SDK supports them. Test both paths; do not assume an SDK's tier label or latest package version implies support for this exact protocol revision.

## Implementation guidance

- Start from the protocol revisions actually supported by every required host, then select an SDK release that documents and tests those revisions. Prefer dual-era support during migration when the SDK provides it.
- Design the application core for horizontal scaling even if the first deployment is local: no in-process cross-call state, no sticky-routing assumption, deterministic tool lists, explicit state handles, and durable shared storage where state is necessary.
- Keep transport and authentication adapters outside tool implementations. stdio and Streamable HTTP should invoke the same authorization-aware service layer, but they will obtain identity and credentials differently.
- Do not adopt Roots, Sampling, MCP Logging, the original HTTP+SSE transport, or OAuth Dynamic Client Registration in a new design unless a required legacy client leaves no alternative.
- Treat remote MCP as production infrastructure: validate the HTTP `Origin` header, authenticate and authorize every call, scope tokens to the intended resource, protect downstream credentials, rate-limit expensive or destructive tools, audit tool invocations, bound request and schema complexity, and propagate trace context.
- Treat tool schemas as an externally reviewed contract. Make additive changes when possible, version breaking changes, keep list ordering deterministic, and coordinate tool-definition refreshes with workspace administrators.
- Test JSON and SSE response paths, cancellation, retries after broken streams, MRTR retries, private-cache behavior, version fallback, replica changes between calls, and expired or revoked OAuth credentials.

## This repository's Python example

The example under `tools/apis-integrations/mcp` implements the new architecture with the stable Python MCP SDK v2.0.0:

- `pyproject.toml` and `uv.lock` pin `mcp==2.0.0`, the first stable Python SDK release with final `2026-07-28` support.
- `server.py` uses `MCPServer` and exposes one Streamable HTTP endpoint at `/mcp`; it no longer exposes the deprecated `/sse` and message-endpoint pair.
- New-revision requests are sessionless by construction. `stateless_http=True` also makes the SDK's compatibility path for 2025-era clients stateless, avoiding sticky routing for either era at the cost of legacy back-channel features.
- `json_response=True` returns a single JSON response for this simple tool. The server can use a request-scoped SSE response instead when that option is removed and streaming progress is needed.
- `client_example.py` uses the v2 high-level `Client`, which probes with `server/discover`, falls back for legacy servers when necessary, and exposes the negotiated revision as `client.protocol_version`. The example fails unless it negotiates `2026-07-28`.
- The tool's `str` return annotation generates an output schema and both text content for the model and `{"result": "..."}` structured content for the host application.
- The generated app retains the SDK's localhost host and origin allowlist. The README calls out the explicit transport-security, authentication, TLS, timeout, and rate-limit configuration required before remote deployment.

The SDK serves the new revision and every earlier revision from the same server, but its v2.0.0 release does not implement the Tasks extension. Do not add Tasks to this example until a later SDK release explicitly documents that support.

## References

- [MCP `2026-07-28` changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog)
- [MCP `2026-07-28` Streamable HTTP specification](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/streamable-http)
- [MCP official SDK tiers](https://modelcontextprotocol.io/docs/sdk)
- [MCP Python SDK v2.0.0 release](https://github.com/modelcontextprotocol/python-sdk/releases/tag/v2.0.0)
- [MCP Python SDK v2 deployment guidance](https://py.sdk.modelcontextprotocol.io/run/deploy/)
- [MCP Python SDK v2 protocol-version negotiation](https://py.sdk.modelcontextprotocol.io/protocol-versions/)
- [Anthropic: Getting Started with Custom Connectors Using Remote MCP](https://support.anthropic.com/en/articles/11175166-about-custom-integrations-using-remote-mcp)
- [Anthropic: Building Custom Connectors via Remote MCP Servers](https://support.anthropic.com/en/articles/11503834-building-custom-connectors-via-remote-mcp-servers)
- [OpenAI: Developer mode and MCP apps in ChatGPT](https://help.openai.com/en/articles/12584461-developer-mode-apps-and-full-mcp-connectors-in-chatgpt-beta)
- [OpenAI: Secure MCP Tunnel](https://developers.openai.com/api/docs/guides/secure-mcp-tunnels)

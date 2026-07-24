# The Agent Tool-Use Loop

## What it is

A tool-use loop lets a language model request actions in systems it cannot access directly.

The application sends the model the user's request, relevant instructions, and tool schemas. The model either returns an answer or emits a structured request to call a tool. The application validates and executes that request, then returns the result as additional context. This repeats until the model returns an answer or the application stops the loop.

This pattern is also called multi-turn function calling. ReAct (Yao et al.) is a related pattern that interleaves reasoning with actions.

## The core property: the model cannot execute anything

A model has no direct network, filesystem, process, or credential access. When it "calls a tool," it emits a structured request:

```json
{
  "type": "function_call",
  "name": "run_semantic_query",
  "arguments": "{\"measures\": [\"orders.monthly_revenue\"], ...}",
  "call_id": "call_abc123"
}
```

That request does not execute anything. The harness parses it, validates it, and decides whether to dispatch the function. After execution, the harness returns a result associated with the same `call_id`:

```json
{
  "type": "function_call_output",
  "call_id": "call_abc123",
  "output": "{\"data\": [{\"orders.monthly_revenue\": 12345.67}]}"
}
```

### Three layers

| Layer | Sees | Can reach |
| ------------------ | -------------------------------------------------------- | ------------------------------- |
| Model | Tool names, descriptions, JSON schemas, returned outputs | Nothing |
| Harness (your app) | Everything | Internal APIs, credentials, DBs |
| Backend services | Requests from the harness only | — |

The model needs to know a tool's name, purpose, and argument shape. It does not need the API base URL, a token, or a database connection string. Keep those in the harness's environment and out of the model's context.

### Why this matters

The gap between what the model requests and what the harness executes is the enforcement boundary:

- Keep credentials in the harness. A context leak should not become a credential leak, though tool results may still contain sensitive business data.
- Validate every request. Use allowlists and schema validation, and enforce row limits, timeouts, read-only behavior, authorization, and other policies in the harness.
- Treat rejection as a normal result. Return a structured error as tool output so the model can revise its request or explain the limitation.
- Limit the tool surface. The model can request only the operations the harness exposes, so narrow tools and schemas reduce the attack surface.

Provider-executed tools, such as hosted code interpreters or provider-side MCP connectors, use a different trust model. The pattern described here keeps execution inside the application's perimeter.

## How the loop runs

1. Send the user's request, instructions, and tool schemas to the model.
1. Inspect the response for items whose type is `function_call`.
1. If there are no function calls, return the model's text response.
1. For each function call, parse and validate the arguments, execute the tool, and create a `function_call_output` with the same `call_id`.
1. Send all tool outputs back to the model and repeat from step 2.

Set a maximum round count and an overall deadline so repeated tool requests cannot consume unbounded time or cost.

```python
while True:
    calls = [i for i in response.output if i.type == "function_call"]
    if not calls:
        return response.output_text

    outputs = []
    for call in calls:
        args = json.loads(call.arguments)
        result = dispatch(call.name, args)      # validation lives here
        outputs.append({
            "type": "function_call_output",
            "call_id": call.call_id,
            "output": json.dumps(result),
        })

    response = client.responses.create(
        previous_response_id=response.id,
        input=outputs,
        tools=TOOL_SCHEMAS,
    )
```

### Implementation notes

- `arguments` is model-generated JSON and can be malformed. Parse it defensively, validate its shape and values, and return a structured error when it is invalid.
- Answer every function call in a round. Omitting a call leaves an unmatched `call_id` and can cause the next request to fail.
- Keep authorization and side-effect controls in the dispatcher. A model's tool choice and arguments are proposals, not permission.
- Tool descriptions guide selection; schema constraints such as `enum` and `maximum` provide enforceable input boundaries.
- Each round is a full API call over the accumulated context. Four rounds over a 12k-token prefix are roughly 50k input tokens, not 12k. Prompt caching can reduce this cost when the prefix is byte-stable.
- Treat tool output as untrusted input. A database row or fetched page may contain prompt injection, so do not let returned content authorize new actions.
- Bound and observe tool failures with timeouts, normalized errors, and logs that omit credentials and unnecessary sensitive payloads.

## Workflow vs. agent

If the model freely chooses which tools to call and in what order, it is an agent. If the sequence is fixed and enforced by the harness, it is a workflow or prompt chain and may not need a model-driven loop.

Hybrids are possible, but an agent loop with harness-enforced ordering may pay agent costs while providing workflow-level control. Consider a fixed pipeline when the sequence is known in advance.

## Good fits

- Governed analytics. The model translates a question into a structured query against a semantic layer, which executes deterministically. The model selects metrics and dimensions but never writes SQL.
- Internal API access. The model works with ticketing, CRM, or deployment-status APIs while credentials remain in the harness and responses are shaped before they are returned.
- Multi-step retrieval. Search, read, follow a reference, and synthesize when each step depends on the previous result.
- Recoverable failure. Tool errors let the model correct its request or explain a limitation instead of failing immediately.

### When not to use it

- Single deterministic lookup. If a question always maps to one call, invoke the function directly.
- Small fixed catalogs. A discovery tool can cost an extra round trip to return information that could have been included in the system prompt.
- Deterministic control flow. If order, authorization, or side effects must be exact, encode that policy in the harness.
- Strong audit requirements. The loop records tool calls and results, not a reliable explanation of why the model chose them. Record explicit decision inputs and policy outcomes when auditability matters.

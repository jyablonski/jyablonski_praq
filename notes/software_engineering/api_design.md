## API Design

Resources, not procedures. The fundamental REST move is modeling nouns and letting HTTP verbs supply the actions. `POST /pipelines/{id}/runs` beats `POST /triggerPipelineRun`. When an operation genuinely isn't CRUD-shaped, don't contort it — make it an explicit action sub-resource (`POST /runs/{id}:cancel` or `/runs/{id}/cancel`) rather than pretending it's a state update.

Verb semantics matter and are contractual:

| Method | Safe | Idempotent | Notes |
| ------ | ---- | ----------- | -------------------------------------------------- |
| GET | ✓ | ✓ | Never mutates. No request body. |
| PUT | ✗ | ✓ | Full replacement; caller supplies complete state |
| PATCH | ✗ | ✗ (usually) | Partial update; ambiguity around null-vs-absent |
| POST | ✗ | ✗ | Creation, non-idempotent actions |
| DELETE | ✗ | ✓ | Second call → 204 or 404, pick one and document it |

Clients, proxies, and retry middleware make real decisions off these properties. Breaking them (a GET that mutates, a PUT that appends) causes bugs you'll never see in your own tests.

Status codes carry meaning. 400 = your request is malformed. 401 = who are you. 403 = I know who you are, no. 404 = doesn't exist (or you're not allowed to know it exists). 409 = conflicts with current state. 422 = well-formed but semantically invalid. 429 = slow down. 503 + `Retry-After` = try again. The distinction that matters most operationally is 4xx (client's fault, don't retry) vs 5xx (mine, retry with backoff).

## Advanced Design Decisions

Errors as a typed contract. Return a stable machine-readable code alongside human text. Something like:

```json
{
  "error": {
    "code": "warehouse_quota_exceeded",
    "message": "Credit limit reached for warehouse ANALYTICS_WH",
    "details": [{"field": "warehouse", "reason": "quota"}],
    "request_id": "req_01HX..."
  }
}
```

The `code` is what clients branch on — it must be stable across versions. The `message` is for humans and can change freely. Never make callers regex your prose. RFC 9457 (`application/problem+json`) is the standardized version of this if you want a spec to point at.

Pagination: cursor over offset. Offset pagination (`?page=5&size=100`) breaks under concurrent writes — rows shift, you skip or duplicate. It also degrades badly at depth since the database still scans everything it skips. Cursor/keyset pagination encodes the last-seen sort key: `?after=eyJpZCI6MTIzfQ&limit=100`. Opaque, base64'd, and clients must treat it as opaque so you can change the encoding. Always cap `limit` server-side, always return a consistent envelope, and always define a total ordering (append a tiebreaker like `id` to any non-unique sort key or your cursor is unstable).

Idempotency keys for unsafe operations. Any POST that creates something expensive or externally-visible should accept an `Idempotency-Key` header. Store key → response for some TTL (24h is common); a replay returns the original response rather than creating a second thing. This is what makes at-least-once client retries safe, and it's the single highest-value thing in a distributed API.

Versioning. Pick one and commit: URL path (`/v1/`) is ugly but unambiguous and easy to route; header-based is cleaner but harder to debug with curl. What actually matters is your compatibility policy — additive changes (new optional fields, new enum values, new endpoints) are non-breaking; removals, renames, type changes, and tightened validation are breaking. Clients must ignore unknown fields, and you should say so in your docs so you're allowed to add them.

Auth and multi-tenancy. Never derive tenant scope from a request parameter the caller controls — derive it from the authenticated principal. `GET /datasets/{id}` should 404 (not 403) if the dataset belongs to another tenant, since 403 leaks existence.

Long-running work. Anything over a few seconds shouldn't block a request. Return `202 Accepted` with a job resource: `{"id": "job_...", "status": "running"}` plus a `Location` header, and let the client poll or subscribe to a webhook. This is squarely your world — a "run this dbt selector" endpoint should never hold a connection open for four minutes.

## Low-level practices that travel across languages

Naming

- Pick one case convention for wire format and never deviate — `snake_case` is the safe default for JSON, `camelCase` if your consumers are JS-first. Do not mix. Do not let each service decide.
- Plural collection nouns (`/datasets`, not `/dataset`).
- Booleans read as assertions: `is_active`, `has_schema_drift`. Never negate in the name (`is_not_enabled` guarantees a double-negative bug).
- Field names describe the value, not the type: `created_at`, not `created_timestamp_string`.

Types and encoding

- Timestamps: RFC 3339 / ISO 8601, UTC, with explicit offset. `2026-07-26T18:04:22Z`. Never epoch integers in a public API (ambiguous units), never local time without an offset.
- Durations: integers with the unit in the name — `timeout_seconds`, `retention_days`. Never a bare number.
- Money and large integers: strings, or integer minor units. IEEE 754 doubles lose precision above 2^53, and JSON numbers are doubles in JavaScript. Snowflake row counts and byte totals cross that line more often than people expect.
- IDs: opaque strings, even if they're integers underneath. Prefixed IDs (`run_01HX…`, `wh_abc123`) are self-describing in logs and make type confusion impossible. Sequential integer IDs leak volume and invite enumeration.
- Enums: send strings, not integers. Document that clients must tolerate unknown values, and give them a fallback — otherwise you can never add a variant.

Nullability and absence

- Distinguish "field not present," "field present and null," and "field present and empty." This is the entire PATCH ambiguity problem. If partial updates matter, either use JSON Merge Patch semantics (null = delete) or require an explicit `update_mask` / `fields` list.
- Prefer empty arrays over null arrays. `[]` lets callers iterate unconditionally; `null` produces a null-check at every call site in every language.
- Omit-vs-null should be consistent across your whole surface, not per-endpoint.

Defaults and validation

- Validate at the boundary, once, exhaustively, and reject with all errors at once rather than one at a time. Nothing is worse than fixing a payload through six round-trips.
- Fail closed on unknown fields *in configuration*, fail open on unknown fields *in responses*. A typo'd key in a config POST should be a 400; an unrecognized field in a response your client parses should be ignored.
- Every default should be safe and explicit in the docs. Unbounded defaults (no `limit`, no `timeout`) are outages waiting to happen.

Robustness

- Set timeouts on every outbound call. Every one. A missing client timeout is the most common cause of cascading failure.
- Retry only idempotent operations, only on 5xx/429/network errors, with exponential backoff *and jitter*. Synchronized retries are how you turn a blip into an outage.
- Bound everything: max page size, max request body, max batch size, max array length. Unbounded inputs are both a DoS vector and an accidental-self-DoS vector.
- Propagate a request/trace ID through every layer and return it in error responses. It's the difference between a five-minute and a five-hour debugging session.

Consistency over cleverness. A slightly suboptimal convention applied uniformly beats a locally optimal one applied inconsistently. Consumers build mental models from your first three endpoints and expect the rest to match.

## Examples

### CRUD baseline

```
GET    /datasets                    list (tenant scoped from token)
POST   /datasets                    create → 201 + Location: /datasets/d_9f3a
GET    /datasets/{id}               read
PUT    /datasets/{id}               full replace
PATCH  /datasets/{id}               partial update
DELETE /datasets/{id}               delete → 204
```

No verbs in the path. No `{id}` on create — the server assigns it.

### Nested collections

```
GET    /pipelines/{id}/runs         runs belonging to a pipeline
POST   /pipelines/{id}/runs         trigger a run
GET    /datasets/{id}/columns       columns belonging to a dataset
GET    /runs/{id}/logs              logs belonging to a run
```

Nest when the child is meaningless without the parent.

### Filtering, sorting, pagination

```
GET /pipelines/{id}/runs?status=failed&limit=50&sort=-started_at
GET /datasets?q=revenue&after=eyJpZCI6MTIzfQ&limit=100
```

`-` prefix for descending. Cursor over offset. Cap `limit` server-side.

### Actions that aren't CRUD

```
POST /pipelines/{id}/pause
POST /pipelines/{id}/resume
POST /runs/{id}/cancel              → 202
POST /api-keys/{id}/rotate          returns new secret once
POST /dbt-models:validate           creates nothing, returns errors
POST /alert-channels/{id}/test-notifications
```

Use these for state transitions with side effects, not for plain field edits.

### Async jobs

```
POST /pipelines/{id}/runs           → 201, Location: /runs/run_abc
                                      {"id":"run_abc","status":"queued"}
GET  /runs/run_abc                  → {"status":"running","progress":0.4}
POST /runs/run_abc/cancel           → 202, status → "cancelling"
```

Terminal states: `succeeded | failed | cancelled`. Client polls with backoff or subscribes to a webhook.

### Retry / re-run

```
POST /pipelines/{id}/runs
{"source_run_id": "run_abc"}
```

Preferred over `/runs/{id}/retry` — keeps one creation path.

### Bulk operations

```
PATCH /datasets/{id}/columns        [{"name":"x","description":"..."}, ...]
POST  /tables/{id}/rows:batchUpsert
Idempotency-Key: <uuid>

→ 207 {"succeeded":9970,"failed":30,
       "errors":[{"index":42,"code":"type_mismatch"}]}
```

Index errors back to the input. Cap batch size. Document all-or-nothing vs partial success.

### Computed reads

```
GET /datasets/{id}/schema-diff?from=v3&to=v7
GET /datasets/{id}?format=csv                  small exports
POST /datasets/{id}/exports                    large exports → async job
```

### Headers worth remembering

```
Authorization: Bearer <token>       tenant derived from here, never the request
Idempotency-Key: <uuid>             any expensive/external-effect POST
If-Match: "a1b2c3"                  optimistic concurrency → 412 on conflict
If-None-Match: "a1b2c3"             conditional GET → 304
Location: /runs/run_abc             on 201 and 202
Retry-After: 30                     on 429 and 503
```

### Status codes in play

| Code | Use |
| --------- | --------------------------------------------- |
| 200 | read / update succeeded |
| 201 | resource created (+ `Location`) |
| 202 | accepted, work is async |
| 204 | deleted, no body |
| 207 | partial success in a batch |
| 304 | ETag matched, reuse your copy |
| 400 | malformed |
| 401 / 403 | unauthenticated / authenticated but forbidden |
| 404 | missing or cross-tenant |
| 409 | conflicts with current state |
| 412 | `If-Match` failed |
| 422 | well-formed, semantically invalid |
| 429 | rate limited (+ `Retry-After`) |

### Two rules that override convenience

Tenant scope comes from the authenticated principal, never from a path param, query param, header, or body field. Cross-tenant access returns 404, not 403.

If the last path segment is a verb, you've written RPC. The exception is the action list above — deliberate, documented, and used only for real state transitions.

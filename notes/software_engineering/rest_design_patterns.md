# REST Design Patterns

## Core Principles

REST (Representational State Transfer) is built on a few key ideas: statelessness, resource-based modeling, and uniform interface. Every request contains all information needed to process it, and resources are the nouns you're manipulating through standard HTTP verbs.

## URL Structure & Naming

Use nouns for resources, not verbs. The HTTP method already provides the action.

```
GET    /users              # list users
GET    /users/123          # get specific user
POST   /users              # create user
PUT    /users/123          # full update
PATCH  /users/123          # partial update
DELETE /users/123          # delete user
```

For nested resources representing clear ownership:

```
GET /users/123/orders           # orders belonging to user 123
GET /users/123/orders/456       # specific order for that user
```

Naming conventions:

- Use plural nouns: `/users` not `/user`
- Use lowercase with hyphens: `/user-profiles` not `/userProfiles` or `/user_profiles`
- Avoid deep nesting beyond 2-3 levels—flatten when it gets unwieldy
- Keep URLs predictable and guessable

## HTTP Methods & Idempotency

| Method | Purpose        | Idempotent | Safe |
| ------ | -------------- | ---------- | ---- |
| GET    | Read           | Yes        | Yes  |
| POST   | Create         | No         | No   |
| PUT    | Full replace   | Yes        | No   |
| PATCH  | Partial update | No\*       | No   |
| DELETE | Remove         | Yes        | No   |

Idempotent means calling it multiple times produces the same result. This matters for retry logic and caching. PUT is idempotent because sending the same full resource representation repeatedly yields the same state. POST isn't because each call might create a new resource.

## Status Codes

Use them correctly, they're part of your API contract.

Success:

- `200 OK` — general success with body
- `201 Created` — resource created, include `Location` header
- `204 No Content` — success, no body (common for DELETE)

Client errors:

- `400 Bad Request` — malformed syntax, validation failure
- `401 Unauthorized` — missing or invalid authentication
- `403 Forbidden` — authenticated but not authorized
- `404 Not Found` — resource doesn't exist
- `409 Conflict` — state conflict (duplicate, version mismatch)
- `422 Unprocessable Entity` — semantically invalid (valid JSON but breaks business rules)
- `429 Too Many Requests` — rate limited

Server errors:

- `500 Internal Server Error` — unexpected failure
- `502 Bad Gateway` — upstream service failed
- `503 Service Unavailable` — temporarily down, often used during maintenance

## Request & Response Design

Consistent response envelope (optional but common):

```json
{
  "data": { ... },
  "meta": { "page": 1, "total": 100 },
  "errors": null
}
```

Some prefer flat responses without envelopes for simplicity. Either works if you're consistent.

Error responses should be structured:

```json
{
  "error": {
    "code": "VALIDATION_FAILED",
    "message": "Invalid input",
    "details": [{ "field": "email", "issue": "must be valid email format" }]
  }
}
```

## Pagination

For list endpoints, always paginate. Common patterns:

Offset-based:

```
GET /users?limit=20&offset=40
```

Simple but has issues with large offsets (database has to skip rows) and inconsistency if data changes between requests.

Cursor-based:

```
GET /users?limit=20&cursor=eyJpZCI6MTIzfQ
```

The cursor encodes the position (often base64-encoded ID or timestamp). More efficient for large datasets and handles inserts/deletes gracefully. Prefer this for production systems.

Return pagination metadata:

```json
{
  "data": [...],
  "pagination": {
    "next_cursor": "abc123",
    "has_more": true
  }
}
```

### Cursor Code Example

```py
import base64
import json

def encode_cursor(last_item):
    # For simple ID-based pagination
    cursor_data = {"id": last_item["id"]}

    # Or for sorting by created_at with ID as tiebreaker
    cursor_data = {
        "created_at": last_item["created_at"].isoformat(),
        "id": last_item["id"]
    }

    return base64.urlsafe_b64encode(
        json.dumps(cursor_data).encode()
    ).decode()

def decode_cursor(cursor_string):
    return json.loads(
        base64.urlsafe_b64decode(cursor_string.encode()).decode()
    )
```

The general pattern is: your cursor contains the values of all columns in your ORDER BY, and your WHERE clause uses tuple comparison (or the expanded equivalent) matching the sort direction.

So if your last item has id=500 and created_at=2024-01-15T10:30:00Z, the endpoint would decode the cursor and find:

- `{"created_at": "2024-01-15T10:30:00Z", "id": 500}`
- In the next query, we want all rows w/ `id > 500`, but we don't want to miss rows created at the same time as that last item.

Then you use those values to fetch the next set of results to serve in the response.

```sql
SELECT * FROM users
WHERE
    id > 500                                 -- decoded cursor value
    AND created_at >= '2024-01-15T10:30:00Z' -- decoded cursor value
ORDER BY created_at ASC, id ASC
LIMIT 100;
```

- You need a tiebreaker (like ID) when sorting by non-unique fields (like created_at) for deterministic pagination.

For generating `has_more`, the trick here is to fetch one extra record than requested. If you asked for 100 and got 101, you know there's more data.

```py
def get_users(cursor=None, limit=20):
    cursor_data = decode_cursor(cursor) if cursor else None

    # Fetch limit + 1
    query = "SELECT * FROM users"
    if cursor_data:
        query += f" WHERE id > {cursor_data['id']}"
    query += f" ORDER BY id ASC LIMIT {limit + 1}"

    rows = db.execute(query)

    # Check if we got the extra row
    has_more = len(rows) > limit

    # Only return the requested amount
    items = rows[:limit]

    next_cursor = None
    if has_more and items:
        next_cursor = encode_cursor(items[-1])

    return {
        "data": items,
        "pagination": {
            "next_cursor": next_cursor,
            "has_more": has_more
        }
    }
```

- So if a user requests 100 rows, we pull 101 rows and then we build the cursor based on the 100th row, not the 101st row
- You then create `has_more` based on whether you got more than the requested limit, and discard that extra row from the response data
- Then you return the `next_cursor` based on the last item in the actual response data
- If there are no more rows, `next_cursor` is null. If there are more rows, it contains the encoded cursor for the next page.

This beats offset for a number of reasons:

- Database performance - w/ offset, the DB has to skip rows which gets slower with higher offsets. With cursor based, it can jump directly to the right spot using indexes.
- Consistency - if data is inserted/deleted between requests, offset can lead to missing or duplicate records. Cursor based handles this gracefully.
- Scalability - cursor based scales better for large datasets.

## Filtering, Sorting, Searching

Keep it intuitive:

```
GET /orders?status=pending&created_after=2024-01-01
GET /users?sort=created_at:desc
GET /products?q=keyboard
```

For complex filtering, some APIs use a dedicated query parameter with a mini query language, but simple key-value pairs cover most cases.

## Versioning

You need a strategy from day one. Options:

URL path versioning (most common, explicit):

```
/v1/users
/v2/users
```

Header versioning (cleaner URLs, less visible):

```
Accept: application/vnd.myapi.v2+json
```

Query parameter:

```
/users?version=2
```

URL path is most widely used because it's obvious and easy to test in browsers. The tradeoff is URLs changing when versions bump.

## Caching & Headers

Cache-Control tells clients and intermediaries how to cache:

```
Cache-Control: public, max-age=3600          # cache for 1 hour
Cache-Control: private, no-cache             # revalidate each time
Cache-Control: no-store                      # never cache (sensitive data)
```

ETag for conditional requests:

```
# Response includes:
ETag: "abc123"

# Subsequent request:
If-None-Match: "abc123"

# Server returns 304 Not Modified if unchanged
```

Last-Modified / If-Modified-Since works similarly with timestamps.

Other important headers:

- `Content-Type: application/json` — always set this
- `Location: /users/123` — on 201 Created, point to new resource
- `Retry-After: 60` — with 429 or 503, tell client when to retry
- `X-Request-ID` — correlation ID for tracing/debugging
- `X-RateLimit-Remaining`, `X-RateLimit-Reset` — rate limit visibility

## Authentication

Common approaches:

- API keys — simple, good for server-to-server
- JWT Bearer tokens — `Authorization: Bearer <token>`, stateless, good for user auth
- OAuth 2.0 — for delegated access, third-party integrations

Always use HTTPS. Never pass secrets in query parameters (they get logged).

## Common Mistakes to Avoid

Verbs in URLs:

```
# Bad
POST /createUser
GET /getUser/123

# Good
POST /users
GET /users/123
```

Inconsistent pluralization:

```
# Bad — mixing singular and plural
/user/123/order

# Good
/users/123/orders
```

Exposing internal implementation:

```
# Bad
GET /api/mysql/users/select

# Good
GET /users
```

Using GET for mutations — violates HTTP semantics and breaks caching.

Ignoring partial failure — for batch operations, define clear semantics (all-or-nothing vs partial success with details).

Not using appropriate status codes — returning 200 with `{"success": false}` makes clients parse bodies to detect errors.

## System Design Interview Tips

When discussing APIs in interviews:

1. Start by identifying resources and their relationships
2. Define the URL structure
3. Specify request/response formats with examples
4. Address pagination strategy for list endpoints
5. Mention authentication approach
6. Note caching headers for read-heavy endpoints
7. Consider rate limiting and how you'd communicate limits
8. Think about idempotency for write operations (idempotency keys for POST)

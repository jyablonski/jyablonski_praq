# API Usage and Best Practices

Comprehensive notes on working with APIs — authentication mechanisms, HTTP methods, REST design, documentation, public vs private APIs, GraphQL, contract testing, and general best practices for building and consuming APIs.

______________________________________________________________________

## Authentication and Authorization

Authentication is about proving who you are. Authorization is about what you're allowed to do. APIs need both, and they're handled differently depending on the use case.

### API Keys

An API key is a simple string token that a client includes with every request to identify itself.

- Usually passed as a header (`X-API-Key: abc123`)
- Prefer headers over query parameters — query params end up in server logs, browser history, and proxy logs
- API keys identify the **calling application**, not a specific user. They're best for server-to-server communication where you want to track which service is making calls
- They're essentially a shared secret — if someone gets your key, they have your access
- Keys should be treated like passwords: stored in environment variables or secret managers, never committed to source control

Common usage:

- Third-party service integrations (Stripe, Twilio, SendGrid)
- Internal service-to-service calls where OAuth would be overkill
- Rate limiting and usage tracking per client

Key management best practices:

- Support key rotation — always allow multiple active keys so you can roll to a new one without downtime
- Scope keys to specific permissions (read-only, write, admin) when possible
- Set expiration dates and force periodic rotation
- Log key usage for audit trails but never log the key value itself
- Provide a way to revoke keys immediately if compromised

### Bearer Tokens (JWT)

Bearer tokens are the standard for user-level authentication. The most common format is JWT (JSON Web Token).

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

A JWT has three parts separated by dots:

1. **Header** — algorithm and token type (`{"alg": "HS256", "typ": "JWT"}`)
1. **Payload** — claims about the user (user ID, roles, expiration time, etc.)
1. **Signature** — cryptographic signature to verify the token hasn't been tampered with

The key advantage of JWTs is that they're **stateless** — the server doesn't need to look up a session in a database to verify the token. It just checks the signature and reads the claims. This makes them great for distributed systems where multiple services need to validate auth.

Tradeoffs:

- You can't easily revoke a JWT before it expires (no central session store to delete from). Workarounds include short expiration times + refresh tokens, or maintaining a blocklist of revoked tokens
- Token size can be large compared to opaque tokens since all the claims are encoded in the payload
- If you put sensitive data in the payload, anyone can decode it (it's base64, not encrypted). Use encryption (JWE) if you need confidentiality

> ELI5: An API key is like a building access card — it says which company you're from. A JWT is like a badge with your name, photo, and department printed on it — anyone can read it and know who you are and what you're allowed to do without calling the front desk.

### Access Tokens and Refresh Tokens

Access Tokens and Refresh Tokens work together to balance security and user experience.

Access Tokens:

- Grant access to protected resources or APIs on behalf of the user or client
- Are usually short-lived, expiring minutes or hours after being issued. This limits the window a stolen token can be used
- Clients send their Access Token with every request in the authorization header: `Authorization: Bearer <access_token>`

Refresh Tokens:

- Used to obtain a new access token without requiring the user to re-authenticate. This allows for a smooth user experience — the client can silently refresh tokens when they expire
- Are usually long-lived and can last hours, days, or even longer depending on the server's configuration
- When an Access Token expires, the client sends the refresh token to the authorization server for a new access token

Client ID and Client Secret are unique identifiers per client interacting with the API. They're used by the authorization server to identify the client making the request.

The authentication flow:

1. **Initial Authentication** — client provides its Client ID, Client Secret, and any other user creds to the authorization server. The server returns an access token and a refresh token
1. **Accessing Resources** — the client uses the access token to access protected resources
1. **Token Expiration** — when the access token expires, the client uses the refresh token to request a new access token from the authorization server

Why use a Refresh Token instead of just re-authenticating every time?

- **Minimizes credential exposure** — you don't have to send the Client ID + Secret over the network every time you need a new access token. The refresh token limits how often sensitive credentials travel over the wire
- **Seamless re-authentication** — clients can stay logged in for long periods without interruption
- **Lower auth server load** — issuing a refresh token requires database calls to verify the client ID + secret. Validating a refresh token (if it's a JWT) just requires verifying the signature — no database call needed. At scale (think Uber, Facebook — millions of users, 100k+ requests/minute), this matters enormously
- **Scope re-evaluation** — when refresh tokens are used to issue new access tokens, you can potentially allow clients to change the scope of their permissions during the refresh

> Basically think of the refresh token as a JWT. To issue it originally, you had to make database calls to verify the client ID + secret. To validate the refresh token later, you just verify the JWT signature hasn't been tampered with — no database call required. Faster for both client and server, and fewer database calls than re-authenticating every time.

### OAuth 2.0

OAuth 2.0 is a framework for **delegated authorization** — it lets a user grant a third-party application limited access to their resources on another service without sharing their password.

The main flows:

- **Authorization Code** — the standard web app flow. User is redirected to the auth server, logs in, gets redirected back with a code that your server exchanges for tokens. Most secure for server-side apps
- **Authorization Code + PKCE** — same as above but with Proof Key for Code Exchange. Required for SPAs and mobile apps where you can't keep a client secret
- **Client Credentials** — machine-to-machine, no user involved. The client authenticates directly with client ID + secret
- **Implicit** (deprecated) — tokens returned directly in the redirect URL. Don't use this anymore; use Authorization Code + PKCE instead

Key concepts:

- **Scopes** define what permissions the token grants (e.g., `read:users`, `write:orders`)
- **Resource server** is the API being accessed
- **Authorization server** issues tokens (could be the same server or a separate service like Auth0, Okta, Keycloak)

### API Key vs Bearer Token vs OAuth — When to Use What

| Mechanism | Best For | User Context | Complexity |
| --------- | -------------------------------- | ------------ | ---------- |
| API Key | Server-to-server, simple integrations | No | Low |
| Bearer/JWT | User authentication, microservices | Yes | Medium |
| OAuth 2.0 | Third-party access, delegated permissions | Yes | High |

______________________________________________________________________

## HTTP Methods In Practice

### GET

- Retrieves data. Must be **safe** (no side effects) and **idempotent** (same result every time)
- Should never modify state. If your GET endpoint changes data, you're doing it wrong
- Cacheable by default — browsers, CDNs, and proxies will cache GET responses
- Use query parameters for filtering and searching: `GET /orders?status=shipped&limit=50`
- Has a practical URL length limit (~2000-8000 chars depending on server/browser) — if your query is too complex for query params, consider POST with a body (search endpoints commonly do this)

### POST

- Creates a new resource or triggers a process
- **Not idempotent** by default — calling it twice might create two resources
- For idempotent POSTs, use an **idempotency key**: the client generates a unique ID and sends it with the request. The server checks if it's already processed that key and returns the cached result instead of creating a duplicate

```
POST /payments
Idempotency-Key: 550e8400-e29b-41d4-a716-446655440000
Content-Type: application/json

{"amount": 100, "currency": "USD"}
```

- Stripe and other payment APIs use this pattern extensively — it prevents double charges if a client retries due to a timeout

### PUT

- Replaces the entire resource with the provided representation
- **Idempotent** — sending the same PUT twice results in the same state
- Client must send the complete resource. If you omit a field, it should be set to null or its default, not left unchanged (that's PATCH behavior)
- Less common in practice than PATCH because most updates are partial

### PATCH

- Partial update — only the fields included in the request body are modified
- Technically not guaranteed to be idempotent (depends on implementation), but in practice most PATCH implementations are
- More bandwidth-efficient than PUT for large resources where you're only changing one field

### DELETE

- Removes a resource. **Idempotent** — deleting something that's already deleted should return success (usually 204 or 404, both are valid approaches)
- Consider soft deletes for resources that might need recovery — mark as deleted rather than actually removing from the database
- For bulk deletes, common patterns are `DELETE /users?ids=1,2,3` or `POST /users/bulk-delete` with a body

### Less Common But Useful

- **HEAD** — same as GET but only returns headers, no body. Useful for checking if a resource exists or getting metadata without downloading the full response
- **OPTIONS** — returns allowed methods for a resource. Used heavily in CORS preflight requests. Browsers send an OPTIONS request automatically before cross-origin requests that aren't "simple"

### Idempotency Summary

| Method | Purpose | Idempotent | Safe |
| ------ | -------------- | ---------- | ---- |
| GET | Read | Yes | Yes |
| POST | Create | No | No |
| PUT | Full replace | Yes | No |
| PATCH | Partial update | No\* | No |
| DELETE | Remove | Yes | No |

Idempotent means calling it multiple times produces the same result. This matters for retry logic and caching. PUT is idempotent because sending the same full resource representation repeatedly yields the same state. POST isn't because each call might create a new resource.

______________________________________________________________________

## URL Structure and Naming

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
- Avoid deep nesting beyond 2-3 levels — flatten when it gets unwieldy
- Keep URLs predictable and guessable

______________________________________________________________________

## Status Codes

Use them correctly — they're part of your API contract.

### Success

- `200 OK` — general success with body
- `201 Created` — resource created, include `Location` header
- `204 No Content` — success, no body (common for DELETE)

### Client Errors

- `400 Bad Request` — malformed syntax, validation failure
- `401 Unauthorized` — missing or invalid authentication
- `403 Forbidden` — authenticated but not authorized
- `404 Not Found` — resource doesn't exist
- `409 Conflict` — state conflict (duplicate, version mismatch)
- `422 Unprocessable Entity` — semantically invalid (valid JSON but breaks business rules)
- `429 Too Many Requests` — rate limited

### Server Errors

- `500 Internal Server Error` — unexpected failure
- `502 Bad Gateway` — upstream service failed
- `503 Service Unavailable` — temporarily down, often used during maintenance

______________________________________________________________________

## Request and Response Design

### Response Envelope

Consistent response envelope (optional but common):

```json
{
  "data": { ... },
  "meta": { "page": 1, "total": 100 },
  "errors": null
}
```

Some prefer flat responses without envelopes for simplicity. Either works if you're consistent.

### Error Responses

Error responses should be structured and actionable:

```json
{
  "error": {
    "code": "VALIDATION_FAILED",
    "message": "Invalid input",
    "details": [{ "field": "email", "issue": "must be valid email format" }]
  }
}
```

______________________________________________________________________

## Pagination

For list endpoints, always paginate.

### Offset-Based

```
GET /users?limit=20&offset=40
```

Simple but has issues with large offsets (database has to skip rows) and inconsistency if data changes between requests.

### Cursor-Based

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

```python
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

For generating `has_more`, the trick is to fetch one extra record than requested. If you asked for 100 and got 101, you know there's more data.

```python
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

- So if a user requests 100 rows, we pull 101 rows and then build the cursor based on the 100th row, not the 101st
- You create `has_more` based on whether you got more than the requested limit, and discard that extra row from the response data
- Then return `next_cursor` based on the last item in the actual response data
- If there are no more rows, `next_cursor` is null. If there are more rows, it contains the encoded cursor for the next page

### Why Cursor Beats Offset

- **Database performance** — with offset, the DB has to skip rows which gets slower with higher offsets. With cursor-based, it can jump directly to the right spot using indexes
- **Consistency** — if data is inserted/deleted between requests, offset can lead to missing or duplicate records. Cursor-based handles this gracefully
- **Scalability** — cursor-based scales better for large datasets

______________________________________________________________________

## Filtering, Sorting, and Searching

Keep it intuitive:

```
GET /orders?status=pending&created_after=2024-01-01
GET /users?sort=created_at:desc
GET /products?q=keyboard
```

For complex filtering, some APIs use a dedicated query parameter with a mini query language, but simple key-value pairs cover most cases.

______________________________________________________________________

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

______________________________________________________________________

## Caching and Headers

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

______________________________________________________________________

## API Documentation

### Swagger / OpenAPI

OpenAPI (formerly Swagger) is the industry standard for describing REST APIs. The specification is a YAML or JSON file that defines your endpoints, request/response schemas, authentication, and more.

```yaml
openapi: 3.0.0
info:
  title: User API
  version: 1.0.0
paths:
  /users:
    get:
      summary: List all users
      parameters:
        - name: limit
          in: query
          schema:
            type: integer
            default: 20
      responses:
        '200':
          description: A list of users
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/User'
components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: integer
        name:
          type: string
        email:
          type: string
          format: email
```

Key benefits:

- **Auto-generated interactive docs** — tools like Swagger UI and Redoc turn the spec into a browsable, testable UI. Developers can try out endpoints directly from the docs page
- **Code generation** — generate client SDKs in any language from the spec. Also generate server stubs
- **Validation** — request and response payloads can be validated against the schema at runtime
- **Single source of truth** — the spec file acts as the canonical API contract

Two approaches to maintaining specs:

- **Code-first** — write your API code and generate the spec from annotations/decorators. FastAPI does this automatically. Less drift, but the spec is a secondary artifact
- **Design-first** — write the spec first, then implement. Better for team collaboration and review before writing code, but you have to keep the spec in sync with the code

### Other Documentation Tools and Formats

- **Postman Collections** — shareable request collections with examples, environments, and tests. Great for team onboarding
- **API Blueprint** — markdown-based format, less common than OpenAPI but more readable for simple APIs
- **AsyncAPI** — like OpenAPI but for event-driven/async APIs (WebSockets, Kafka, etc.)
- **README + Examples** — for simple APIs, a well-written README with curl examples can be more effective than a formal spec

Documentation best practices:

- Include runnable examples for every endpoint — curl commands, Python snippets, etc.
- Document error responses as thoroughly as success responses. Developers spend more time debugging errors than reading happy-path docs
- Show authentication setup as the very first thing in your docs
- Include rate limit information prominently
- Provide a changelog for API updates so consumers know what changed

______________________________________________________________________

## GraphQL vs REST

GraphQL and REST are two different approaches to building APIs. REST uses multiple endpoints with fixed response shapes, while GraphQL uses a single endpoint with flexible queries.

### Key Differences

**Data Fetching:**

- GraphQL has a single endpoint. Clients specify exactly what data they need, avoiding over-fetching (getting more data than needed) and under-fetching (needing multiple requests)
- REST has multiple endpoints, each returning a fixed set of data. Clients may receive more than they need or have to make multiple calls to gather related data

**Schema and Types:**

- GraphQL is strongly typed with a schema defining all types and relationships. The schema is used for validating queries and responses. Supports nested queries to fetch related data in a single request
- REST has no required schema. The response structure is defined by the server's implementation. Relationships are managed via additional requests or embedded data

**Operations:**

- GraphQL distinguishes between queries (reads), mutations (writes), and subscriptions (real-time updates)
- REST relies on standard HTTP methods: GET, POST, PUT/PATCH, DELETE

**Versioning:**

- GraphQL typically doesn't use versioning — APIs evolve by adding new fields and types. Clients only request what they need, so breaking changes are less frequent
- REST often uses versioning (`/v1/resource`) to manage changes

**Error Handling:**

- GraphQL returns both data and errors in a structured format in the response body, allowing clients to handle partial successes
- REST uses HTTP status codes for error signaling with details in the response body

**Caching:**

- GraphQL caching is more complex due to the flexible nature of queries. Tools like Apollo Client provide client-side caching mechanisms. Server-side caching is harder since a single endpoint handles everything
- REST leverages standard HTTP caching (ETags, Cache-Control) easily since each endpoint represents a resource

### GraphQL Example

```graphql
query {
  users {
    id
    name
    email
  }
}

mutation {
  createUser(input: { name: "Alice Johnson", email: "alice@example.com" }) {
    id
    name
    email
  }
}

mutation {
  updateUser(id: "1", input: { email: "newemail@example.com" }) {
    id
    name
    email
  }
}
```

Equivalent REST calls:

```bash
GET https://my_api.com/v1/users/1

POST /users HTTP/1.1
Host: example.com
Content-Type: application/json

{
  "name": "Alice Johnson",
  "email": "alice@example.com"
}

PATCH /users/1 HTTP/1.1
Host: example.com
Content-Type: application/json

{
  "email": "newemail@example.com"
}
```

### GraphQL Advantages

- Self-documenting — documentation is available on the UI itself and updates automatically as you add new models
- Automatic validation and error messages for clients
- Once you have all the objects available via GraphQL, you never have to create another endpoint at the client's request because they can specify any data they need in a single call
- Much smaller API surface — fewer endpoints to maintain
- Being able to specify what you want not only returns less data over the wire, but allows the backend to retrieve less data
- The query language is easier to read and type than JSON
- Introspection — clients can query the schema to understand available types and fields. Tools like GraphiQL, Apollo Client, and Relay provide robust development and debugging support

### When to Use Which

- **GraphQL** — applications requiring flexible data retrieval, complex querying needs, or efficient handling of related data. Common in modern web and mobile apps where front-end developers need precise control over fetched data
- **REST** — simpler resource-based APIs where standard CRUD operations suffice. Common in microservices architectures, public APIs, and scenarios where standardization and ease of use are priorities

______________________________________________________________________

## Public vs Private APIs

### Public APIs

Public APIs (also called external or open APIs) are exposed to third-party developers outside your organization.

Characteristics:

- **Versioning is critical** — you can't force external consumers to update. Breaking changes require a new version while maintaining the old one for a deprecation period
- **Rate limiting is mandatory** — protect your infrastructure from abuse. Common tiers: free (100 req/min), basic (1000 req/min), enterprise (custom)
- **API keys or OAuth** — you need to know who's calling you for billing, analytics, and abuse prevention
- **Documentation must be excellent** — external devs don't have access to your Slack to ask questions
- **Backward compatibility** — never remove or rename fields. Add new fields, deprecate old ones, remove in the next major version
- **SLAs (Service Level Agreements)** — uptime guarantees, response time commitments, support channels
- **Security is paramount** — assume every input is hostile. Validate everything, use HTTPS only, implement CORS properly

Examples: Stripe API, GitHub API, Twilio API, Twitter/X API

### Private APIs

Private APIs (also called internal APIs) are used within your organization between teams and services.

Characteristics:

- **More flexibility to change** — you control all consumers, so coordinated breaking changes are possible (though still painful)
- **Simpler auth** — often service mesh mTLS, internal API keys, or network-level restrictions (VPC, firewall rules) rather than OAuth
- **Less formal documentation** — though you should still document them. Future you is also a consumer
- **Performance optimizations** — internal APIs can use binary protocols (gRPC, Protocol Buffers) since you control both ends
- **Can expose internal details** — field names might match database columns, internal IDs are fine to expose

### Partner APIs

A middle ground — exposed to specific business partners with a formal agreement.

- Require API keys with specific scoping per partner
- Documentation is shared privately
- Often have custom rate limits and SLAs per partner
- May expose more functionality than public APIs but less than internal ones

### API Gateway Patterns

In practice, most organizations use an **API gateway** to manage the boundary between public and private:

- The gateway handles auth, rate limiting, logging, and routing
- External consumers hit the gateway, which proxies to internal services
- Internal services can communicate directly or through a service mesh
- Common gateways: Kong, AWS API Gateway, Apigee, nginx

______________________________________________________________________

## Contract Testing

Contract testing verifies that the communication between API providers and consumers works as expected. It's different from integration testing — instead of testing the entire stack, you test the **contract** (the agreed-upon interface) independently on each side.

### The Problem Contract Testing Solves

In a microservices world, Service A depends on Service B's API. Without contract testing:

1. Service B deploys a change that renames a field from `user_name` to `username`
1. Integration tests might not catch this if they don't cover that specific path
1. Service A breaks in production

With contract testing, both sides verify independently that they conform to the agreed-upon contract. If Service B renames a field, the contract test fails before it reaches production.

### Consumer-Driven Contract Testing

The most popular approach, championed by **Pact**.

How it works:

1. **Consumer side** — the consumer writes tests that define what it expects from the provider. These expectations are captured as a **pact file** (a JSON contract)
1. **Pact file is shared** — usually published to a Pact Broker (a central registry)
1. **Provider side** — the provider runs the pact file against its actual API to verify it fulfills the contract
1. **Both sides run independently** — consumer tests run without the real provider (using a mock), provider verification runs without the real consumer

```python
# Consumer side (Python example with Pact)
from pact import Consumer, Provider

pact = Consumer('OrderService').has_pact_with(Provider('UserService'))

pact.given(
    'a user with ID 123 exists'
).upon_receiving(
    'a request for user 123'
).with_request(
    method='GET',
    path='/users/123'
).will_respond_with(
    status=200,
    body={
        'id': 123,
        'name': 'Alice',
        'email': 'alice@example.com'
    }
)

# This generates a pact JSON file that the provider must verify against
```

```python
# Provider side — verifies the pact
from pact import Verifier

verifier = Verifier(
    provider='UserService',
    provider_base_url='http://localhost:8000'
)

# Pulls the contract from the Pact Broker and verifies
verifier.verify_with_broker(
    broker_url='https://pact-broker.example.com',
    publish_version='1.0.0'
)
```

### Provider Contract Testing

The reverse approach — the provider publishes its contract (usually an OpenAPI spec) and consumers verify they're using it correctly. Less common but useful when the provider team controls the API design.

### Schema Testing

A lighter-weight alternative to full contract testing. Instead of verifying behavior, you verify that the response matches an expected schema.

```python
# Using jsonschema
from jsonschema import validate

expected_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "name": {"type": "string"},
        "email": {"type": "string", "format": "email"}
    },
    "required": ["id", "name", "email"]
}

response = requests.get('/users/123')
validate(instance=response.json(), schema=expected_schema)
```

### When to Use Contract Testing

- Microservices communicating over HTTP or messaging
- When multiple teams own different services and deploy independently
- When integration tests are slow, flaky, or don't cover all interactions
- When you want faster feedback than end-to-end tests provide

When it's probably overkill:

- Monolithic applications
- Small teams where everyone works on all services
- APIs with very few consumers

### Tools

- **Pact** — the most popular consumer-driven contract testing framework. Supports many languages (Python, JS, Java, Go, etc.)
- **Spring Cloud Contract** — popular in the Java/Spring ecosystem
- **Schemathesis** — property-based testing for APIs using OpenAPI specs. Generates random valid requests and checks the API behaves correctly
- **Dredd** — tests your API against its API Blueprint or OpenAPI documentation

______________________________________________________________________

## Rate Limiting

Rate limiting protects your API from abuse and ensures fair usage across consumers.

Common algorithms:

- **Fixed window** — count requests per time window (e.g., 100 requests per minute). Simple but has burst issues at window boundaries
- **Sliding window** — smooths out the fixed window problem by using a rolling time frame
- **Token bucket** — tokens are added at a steady rate, each request costs a token. Allows short bursts while maintaining an average rate. Most commonly used in production systems
- **Leaky bucket** — requests queue up and are processed at a fixed rate. Good for smoothing out traffic

Communicate limits via headers:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 67
X-RateLimit-Reset: 1672531200
Retry-After: 30
```

When rate limited, return `429 Too Many Requests` with the `Retry-After` header.

Best practices:

- Different rate limits for different endpoints (reads vs writes, search vs CRUD)
- Different tiers for different API key levels
- Consider rate limiting by user AND by IP to prevent a single user from hogging resources
- Return meaningful error messages that tell the consumer when they can retry

______________________________________________________________________

## API Security Best Practices

- **Always use HTTPS** — never serve APIs over plain HTTP. Use HSTS headers to prevent downgrade attacks
- **Validate all input** — never trust client data. Validate types, lengths, formats, and ranges. SQL injection and XSS are still among the most common vulnerabilities
- **Use parameterized queries** — never build SQL from string concatenation
- **Implement CORS properly** — don't use `Access-Control-Allow-Origin: *` for authenticated endpoints. Whitelist specific domains
- **Don't expose stack traces** — return generic error messages in production. Log the details server-side
- **Use request timeouts** — prevent slow clients from holding connections open. Set reasonable timeouts on both client and server side
- **Implement request size limits** — prevent denial of service via enormous payloads
- **Sanitize sensitive data in logs** — never log tokens, passwords, credit card numbers, or PII
- **Use security headers** — `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Strict-Transport-Security`

______________________________________________________________________

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

______________________________________________________________________

## General Best Practices Checklist

### Designing APIs

- Design the API from the consumer's perspective, not the database schema
- Use consistent naming conventions across all endpoints
- Version your API from day one, even if you think you won't need it
- Make errors actionable — tell the consumer what went wrong and how to fix it
- Support filtering, sorting, and pagination on all list endpoints
- Use standard HTTP status codes correctly

### Building APIs

- Implement health check endpoints (`GET /health`) for monitoring and load balancers
- Add request ID tracking for distributed tracing — generate a UUID per request and include it in logs and responses
- Implement graceful shutdown — stop accepting new requests, finish in-flight ones
- Use connection pooling for database connections
- Implement circuit breakers for downstream API calls to prevent cascading failures
- Write integration tests that cover auth flows, error cases, and edge cases — not just happy paths

### Consuming APIs

- Always set timeouts on HTTP clients — never wait forever for a response
- Implement retry logic with exponential backoff and jitter for transient failures
- Cache responses when the API supports it (respect `Cache-Control`, `ETag` headers)
- Handle rate limiting gracefully — respect `Retry-After` headers, implement backoff
- Don't hard-code base URLs — use configuration so you can switch environments
- Parse responses defensively — don't assume fields will always be present
- Monitor your API dependencies — track latency, error rates, and availability of APIs you depend on

### System Design Interview Tips

When discussing APIs in interviews:

1. Start by identifying resources and their relationships
1. Define the URL structure
1. Specify request/response formats with examples
1. Address pagination strategy for list endpoints
1. Mention authentication approach
1. Note caching headers for read-heavy endpoints
1. Consider rate limiting and how you'd communicate limits
1. Think about idempotency for write operations (idempotency keys for POST)

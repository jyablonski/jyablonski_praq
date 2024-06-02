# GraphQL vs REST API
GraphQL and REST are two different approaches to building APIs, each with its own principles, features, and use cases. Here are the main differences between GraphQL and REST APIs:

### 1. **Data Fetching**

- **GraphQL**:
  - **Single Endpoint**: Typically, a GraphQL API has a single endpoint for all queries and mutations.
  - **Flexible Queries**: Clients specify exactly what data they need, and the server responds with only that data. This avoids over-fetching (retrieving more data than necessary) and under-fetching (retrieving insufficient data).

- **REST**:
  - **Multiple Endpoints**: REST APIs typically have multiple endpoints, each representing a resource.
  - **Fixed Responses**: Each endpoint returns a fixed set of data. This can lead to over-fetching or under-fetching since clients may receive more data than needed or require multiple requests to get all necessary data.

### 2. **Data Structure and Types**

- **GraphQL**:
  - **Typed Schema**: GraphQL APIs are strongly typed, and a schema defines the types and relationships of the data available. This schema is used for validating queries and responses.
  - **Nested Queries**: GraphQL allows clients to request nested and related data in a single query.

- **REST**:
  - **No Fixed Schema**: REST APIs do not require a schema. The structure of the response is defined by the server's implementation.
  - **Resource-Based**: Each resource is typically represented by a URL, and relationships are managed via additional requests or embedding data within resources.

### 3. **Operations**

- **GraphQL**:
  - **Queries and Mutations**: GraphQL distinguishes between queries (for reading data) and mutations (for writing data).
  - **Subscriptions**: GraphQL supports real-time data updates through subscriptions.

- **REST**:
  - **HTTP Methods**: REST relies on standard HTTP methods for operations: GET (read), POST (create), PUT/PATCH (update), DELETE (delete).

### 4. **Versioning**

- **GraphQL**:
  - **No Versioning**: GraphQL APIs typically do not use versioning. Instead, they evolve by adding new fields and types. Clients request only the data they need, so breaking changes are less frequent.
  
- **REST**:
  - **Versioning**: REST APIs often use versioning (e.g., `/v1/resource`) to manage changes and updates to the API.

### 5. **Error Handling**

- **GraphQL**:
  - **Unified Error Format**: GraphQL responses include both data and errors in a structured format, allowing clients to handle partial successes and failures gracefully.

- **REST**:
  - **HTTP Status Codes**: REST APIs use standard HTTP status codes for error handling, and the error details are often included in the response body.

### 6. **Tooling and Ecosystem**

- **GraphQL**:
  - **Introspection**: GraphQL APIs can be introspected, meaning clients can query the schema to understand the available types and fields.
  - **Tooling**: Tools like GraphiQL, Apollo Client, and Relay provide robust development and debugging support.

- **REST**:
  - **Widespread Adoption**: REST has been around for longer and has extensive tooling and community support.
  - **Tools**: Tools like Postman, Swagger (OpenAPI), and various client libraries provide strong support for REST API development and testing.

### 7. **Performance Considerations**

- **GraphQL**:
  - **Efficient Data Retrieval**: Can reduce the number of requests and amount of data transferred by allowing clients to request exactly what they need.
  - **Complex Queries**: Can potentially lead to performance issues if not properly managed, as complex queries might be resource-intensive.

- **REST**:
  - **Simple Operations**: Each endpoint is generally optimized for specific operations, which can lead to straightforward performance optimization.
  - **Multiple Requests**: Clients may need to make multiple requests to different endpoints to gather related data, potentially increasing latency.

### 8. **Caching**

- **GraphQL**:
  - **Client-Side Caching**: More complex due to the flexible nature of queries. Tools like Apollo Client provide mechanisms for caching.
  - **Server-Side Caching**: Can be challenging since a single endpoint handles all operations, requiring more sophisticated caching strategies.

- **REST**:
  - **HTTP Caching**: Leverages standard HTTP caching mechanisms (e.g., ETags, Cache-Control headers) more easily, as each endpoint represents a resource.

### Use Cases

- **GraphQL**:
  - Suitable for applications requiring flexible data retrieval, complex querying needs, or efficient handling of related data.
  - Often used in modern web and mobile applications where front-end developers need precise control over the data they retrieve.

- **REST**:
  - Ideal for simpler, resource-based APIs where standard CRUD operations suffice.
  - Commonly used in microservices architectures, public APIs, and scenarios where standardization and ease of use are priorities.

Both GraphQL and REST have their strengths and trade-offs, and the choice between them depends on the specific requirements and constraints of the application being developed.

- GraphQL comes w/ documentation available on the UI itself and is self-documenting as you add new models
- Automatic validation and error messages for clients
- Once you have all the objects in your API available via GraphQL, you'll never have to create another endpoint at the client's request because they need certain pieces of information available in the same endpoint, because they can specify any data they need in a single call.
- Much smaller API surface for the reason described in the previous reason
- Being able to specify what you want not only lets you return less data over the wire, but it allows the backend to retrieve less data
- The query language is easier to read and type than JSON

``` graphql
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

``` bash
GET https://my_api.com/v1//users/1

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
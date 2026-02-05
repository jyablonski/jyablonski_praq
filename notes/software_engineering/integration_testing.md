# Integration Testing in Software Development

A practical guide to understanding when and how to use integration tests, the role of mocks, and the spectrum of testing strategies.

## What Is an Integration Test?

An integration test verifies that multiple components work together correctly. Unlike unit tests, which isolate a single function or class, integration tests exercise the boundaries between systems.

The key question an integration test answers: "Do these pieces actually work together in the real world?"

Examples of what integration tests verify:

- Your application code correctly queries a database
- Your service properly calls an external API and handles its responses
- Multiple microservices communicate correctly over HTTP or message queues
- Your ORM mappings match your actual database schema
- Database migrations run successfully and preserve data integrity

## The Testing Spectrum

Testing isn't binary. There's a spectrum from fully isolated to fully integrated:

```
Unit Tests ──────────────────────────────────────────── Production
     │                                                        │
     │   Mocked        Partial         Full          Staging  │
     │   Unit          Integration     Integration   / E2E    │
     │   Tests         Tests           Tests         Tests    │
     │                                                        │
  [Fast, Isolated]                              [Slow, Realistic]
```

Each point on this spectrum trades off speed and isolation for realism and confidence.

## Unit Tests vs Integration Tests

| Aspect | Unit Test | Integration Test |
| ----------------- | --------------------- | --------------------- |
| Scope | Single function/class | Multiple components |
| Dependencies | All mocked/stubbed | Some or all real |
| Speed | Milliseconds | Seconds to minutes |
| Failure diagnosis | Pinpoints exact issue | "Something broke" |
| Confidence | Logic is correct | System actually works |
| Maintenance | Low | Higher |

Neither is "better" — they serve different purposes. A healthy test suite needs both.

## When to Use Mocks vs Real Dependencies

### Use Mocks When

Testing business logic in isolation. If you're testing that your `calculateOrderTotal()` function correctly applies discounts, you don't need a real database. Mock the repository layer and focus on the calculation logic.

External services are unreliable or expensive. Third-party APIs (Stripe, Twilio, AWS) shouldn't be called in every test run. They're slow, cost money, and their availability isn't in your control.

You need to simulate edge cases. Mocks let you easily test error conditions: What happens when the database times out? When the API returns a 500? When the network drops mid-request? These scenarios are hard to reproduce with real services.

Speed is critical. Unit tests with mocks run in milliseconds. If you're doing TDD with rapid feedback loops, mocks keep you productive.

You're testing code that orchestrates other components. If your service coordinates between multiple dependencies, you might mock those dependencies to verify the orchestration logic itself.

### Use Real Dependencies When

Testing data access code. ORMs, query builders, raw SQL — these need real database validation. A mock won't catch that your JOIN is wrong or your index isn't being used.

Verifying serialization/deserialization. JSON parsing, protobuf encoding, database type mappings — subtle bugs hide here that mocks will never reveal.

Testing database migrations. You absolutely need a real database to verify migrations work correctly.

Validating configuration and connection handling. Connection pooling, timeout settings, retry logic — these only matter against real infrastructure.

Building confidence before deployment. Before shipping, you want tests that prove the system works end-to-end, not just that each piece works in isolation.

## Is It Still an Integration Test If There Are Mocks?

This is where terminology gets fuzzy, and people have strong opinions. Here's a practical framework:

### The Purist View

Some argue that if *any* dependency is mocked, it's not a true integration test. By this definition, integration tests must use all real components.

### The Pragmatic View

Most teams use a more flexible definition: An integration test is any test that exercises real interactions between components, even if some dependencies are mocked.

The key distinction is *what* you're testing:

- If you're testing that your code correctly interacts with Postgres -> use real Postgres
- If you're testing that your code correctly handles responses from a payment API -> mocking that API is reasonable, as long as your mock accurately represents real behavior

### A Useful Mental Model

Think about what you're integrating:

```
┌─────────────────────────────────────────────────────────────┐
│                     Your Application                        │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐  │
│  │ Handler │───▶│ Service │───▶│  Repo   │───▶│   DB    │  │
│  └─────────┘    └─────────┘    └─────────┘    └─────────┘  │
│                      │                                      │
│                      ▼                                      │
│               ┌─────────────┐                               │
│               │ External API│                               │
│               └─────────────┘                               │
└─────────────────────────────────────────────────────────────┘
```

An integration test might:

- Use a real database (testing Repo -> DB integration)
- Use a mocked external API (because testing that integration isn't the focus)

This is still meaningfully an integration test — you're testing real integration between your service, repository, and database layers. The mocked external API doesn't invalidate that.

## Real Postgres in Docker vs Mocked HTTP Endpoint

Let's compare two common patterns:

### Pattern A: Real Postgres in Docker

```go
func TestUserRepository_Create(t *testing.T) {
    // Spin up real Postgres
    container, _ := postgres.RunContainer(ctx)
    db, _ := sql.Open("postgres", container.ConnectionString())
    
    // Run migrations
    migrate.Up(db)
    
    // Test against real database
    repo := NewUserRepository(db)
    user, err := repo.Create(&User{Email: "test@example.com"})
    
    // Verify actual database state
    var count int
    db.QueryRow("SELECT COUNT(*) FROM users").Scan(&count)
    assert.Equal(t, 1, count)
}
```

What this validates:

- SQL syntax is correct
- Schema matches your code's expectations
- Constraints (unique, foreign keys) behave as expected
- Transactions work correctly
- Connection handling is proper
- Your ORM mappings are accurate

What this doesn't catch:

- Production Postgres configuration differences
- Network latency issues
- Connection pool exhaustion under load

### Pattern B: Mocked HTTP Endpoint

```go
func TestPaymentService_Charge(t *testing.T) {
    // Create mock server
    server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        // Verify request format
        assert.Equal(t, "POST", r.Method)
        assert.Equal(t, "application/json", r.Header.Get("Content-Type"))
        
        // Return canned response
        w.WriteHeader(http.StatusOK)
        json.NewEncoder(w).Encode(map[string]string{
            "charge_id": "ch_123",
            "status": "succeeded",
        })
    }))
    defer server.Close()
    
    // Test against mock
    client := NewPaymentClient(server.URL)
    result, err := client.Charge(1000, "usd")
    
    assert.NoError(t, err)
    assert.Equal(t, "succeeded", result.Status)
}
```

What this validates:

- Your HTTP client constructs requests correctly
- Response parsing works
- Error handling for various status codes (if you add more test cases)

What this doesn't catch:

- The real API's actual response format (if your mock is wrong, your tests pass but production fails)
- Authentication/authorization issues
- Rate limiting behavior
- Real network conditions

### The Critical Difference

| Aspect | Real Postgres | Mocked HTTP |
| ------------------- | -------------------------------------- | ----------------------------------- |
| Fidelity | High — it's the actual database engine | Variable — depends on mock accuracy |
| Drift risk | Low — Postgres is Postgres | High — real API may change |
| What you're testing | Real integration | Your assumptions about integration |
| Maintenance burden | Container management | Keeping mocks in sync |

The real Postgres test gives you genuine confidence that your database code works. The database in Docker behaves identically to production (assuming same version).

The mocked HTTP test only validates your code's behavior given your assumed API contract. If the real API returns `"state": "completed"` instead of `"status": "succeeded"`, your mock won't catch that.

### Making HTTP Mocks More Valuable

If you must mock HTTP dependencies, increase confidence with:

Contract testing: Use tools like Pact to verify your mock matches the real API's contract.

Record/replay: Record real API responses and replay them in tests. Tools like VCR (Ruby), go-vcr, or Polly.js help here.

Periodic live validation: Run a subset of tests against the real API in CI (maybe nightly) to catch contract drift.

OpenAPI validation: If the API has an OpenAPI spec, validate your mock responses against it.

## Practical Patterns for Integration Tests

### Transaction Rollback Pattern

Wrap each test in a transaction that rolls back, leaving the database clean:

```go
func TestWithRollback(t *testing.T) {
    tx, _ := db.BeginTx(ctx, nil)
    defer tx.Rollback()
    
    repo := NewUserRepo(tx)
    // ... test operations ...
    // Rollback happens automatically, database unchanged
}
```

Pros: Fast, tests are isolated, no cleanup needed\
Cons: Can't test transaction commit behavior, some operations don't work in transactions

### Truncate Pattern

Truncate relevant tables before or after each test:

```go
func setup(t *testing.T) {
    db.Exec("TRUNCATE users, orders, payments CASCADE")
}
```

Pros: Tests commit behavior, realistic\
Cons: Slower, requires careful ordering, can't parallelize easily

### Test Containers Pattern

Spin up fresh containers per test or test suite:

```go
func TestMain(m *testing.M) {
    container, _ := postgres.RunContainer(ctx)
    db = connectTo(container)
    code := m.Run()
    container.Terminate(ctx)
    os.Exit(code)
}
```

Pros: Complete isolation, matches production, can test different versions\
Cons: Slower startup, requires Docker, resource intensive

### Hybrid Pattern

Use different strategies for different needs:

```go
// Fast unit tests with mocks
func TestOrderService_CalculateTotal(t *testing.T) {
    mockRepo := &OrderRepoMock{...}
    svc := NewOrderService(mockRepo)
    // Test business logic
}

// Integration tests with real database
func TestOrderService_Integration(t *testing.T) {
    if testing.Short() {
        t.Skip("skipping integration test")
    }
    db := setupTestDB()
    svc := NewOrderService(NewOrderRepo(db))
    // Test real database operations
}
```

Run fast tests during development (`go test -short`), full suite in CI.

## Common Anti-Patterns

### Over-Mocking

Mocking so much that tests don't verify real behavior:

```go
// Bad: What is this even testing?
func TestCreateUser(t *testing.T) {
    mockDB := &MockDB{}
    mockDB.On("Insert", mock.Anything).Return(nil)
    
    svc := NewUserService(mockDB)
    err := svc.CreateUser(&User{})
    
    assert.NoError(t, err)
    mockDB.AssertCalled(t, "Insert", mock.Anything)
}
```

This test only verifies that `CreateUser` calls `Insert`. It doesn't verify that the data is correct, that the SQL works, or that the user is actually created.

### Mock Drift

Mocks that no longer reflect reality:

```go
// Your mock
mockAPI.On("GetUser", "123").Return(&User{Name: "Alice"}, nil)

// Real API now returns
// {"user": {"full_name": "Alice", "id": "123"}}

// Tests pass, production breaks
```

### Testing Implementation Instead of Behavior

```go
// Bad: Testing that specific methods are called
mockRepo.AssertCalled(t, "FindByID", "123")
mockRepo.AssertCalled(t, "Save", mock.Anything)
mockRepo.AssertNumberOfCalls(t, "Save", 1)

// Better: Testing the actual outcome
user, _ := service.UpdateEmail("123", "new@email.com")
assert.Equal(t, "new@email.com", user.Email)
```

### Ignoring Test Data Setup Complexity

Integration tests often fail not because of bugs, but because test data setup is brittle. Invest in:

- Factory functions for creating test entities
- Fixtures for common scenarios
- Clear documentation of data dependencies

## Guidelines for a Balanced Test Suite

Write unit tests for:

- Pure business logic
- Complex algorithms
- Input validation
- Error handling branches

Write integration tests for:

- Database queries and commands
- External service interactions (with appropriate mocking strategy)
- API endpoint behavior
- Message queue producers/consumers
- File I/O operations

Consider end-to-end tests for:

- Critical user journeys
- Deployment verification
- Cross-service workflows

A reasonable ratio might be:

- 70% unit tests (fast, focused)
- 20% integration tests (real dependencies where it matters)
- 10% end-to-end tests (key flows only)

This isn't a strict rule — it depends on your system. A data pipeline might need 50% integration tests. A pure computation library might be 95% unit tests.

## Key Takeaways

1. Integration tests verify real interactions between components. The presence of some mocks doesn't disqualify a test from being an integration test — what matters is whether you're testing genuine integration points.

1. A real database in Docker provides high-fidelity testing because it's the actual database engine. A mocked HTTP endpoint only tests your assumptions about the API.

1. Mock external dependencies you don't control, but validate those mocks against reality through contract testing, recorded responses, or periodic live tests.

1. Use real dependencies for code that directly interacts with them — especially database access, serialization, and configuration.

1. Speed and confidence are in tension. Balance them based on what each test is trying to prove.

1. Integration tests require investment in test infrastructure — database setup, fixture management, cleanup strategies. This investment pays off in confidence.

1. The goal isn't test purity; it's confidence that your system works. Use whatever combination of techniques gets you there efficiently.

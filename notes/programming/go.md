# Go

[Guide](https://go.dev/doc/tutorial/getting-started)

Go is a statically typed, compiled language designed at Google for simplicity, reliability, and efficiency. It emphasizes fast compilation, clean syntax, and built-in concurrency primitives, making it well-suited for backend services and infrastructure tooling.

## Why Go?

- Simplicity by design - Small language spec, easy to learn, one obvious way to do things
- Fast compilation - Large projects compile in seconds, not minutes
- Built-in concurrency - Goroutines and channels make concurrent code straightforward
- Single binary deployment - Compiles to a static binary with no runtime dependencies
- Strong standard library - HTTP servers, JSON, crypto, testing all built in
- Excellent tooling - Formatter, linter, testing, profiling included out of the box
- Battle-tested at scale - Powers Docker, Kubernetes, Terraform, and much of cloud infrastructure

## Components

- go - The Go compiler and toolchain, handles building, testing, and module management
- gofmt - Official formatter, zero-config, enforces consistent style
- go mod - Dependency management system (like npm or cargo)
- Modules - Go's term for packages/projects. Published via git repos (usually GitHub)
- go vet - Built-in static analyzer that catches common mistakes
- golangci-lint - Popular third-party meta-linter that bundles many linters together

## Quick Start

[Install Guide](https://go.dev/doc/install)

Download from the official site or use a package manager:

```sh
# macOS
brew install go

# Ubuntu/Debian
sudo apt install golang-go

# Or download directly from https://go.dev/dl/
```

Verify installation:

```sh
go version
```

Set up your workspace (Go 1.18+ with modules, you can work anywhere):

```sh
mkdir my_project && cd my_project
go mod init github.com/yourname/my_project
```

## Commands

```sh
# Project management
go mod init <module-name>    # Initialize new module
go mod tidy                  # Add missing, remove unused dependencies
go mod download              # Download dependencies to cache
go get <package>             # Add a dependency

# Building and running
go build                     # Compile package
go build -o myapp            # Compile with specific output name
go run main.go               # Compile and run (for development)
go install                   # Build and install to $GOPATH/bin

# Testing and checks
go test ./...                # Run all tests
go test -v                   # Verbose test output
go test -cover               # Show coverage percentage
go test -bench=.             # Run benchmarks
go vet ./...                 # Run static analysis

# Formatting and linting
gofmt -w .                   # Format all files in place
go fmt ./...                 # Same thing via go command
golangci-lint run            # Run linter suite (install separately)

# Other
go doc <package>             # View documentation
go generate                  # Run code generation directives
go clean                     # Remove build artifacts
```

## Project Structure

A typical Go project looks like this:

```
my_project/
├── go.mod                # Module definition and dependencies
├── go.sum                # Checksums for dependencies
├── main.go               # Entry point (package main)
├── internal/             # Private packages (can't be imported externally)
│   └── config/
│       └── config.go
├── pkg/                  # Public packages (optional, some projects skip this)
│   └── client/
│       └── client.go
├── cmd/                  # Multiple entry points for different binaries
│   ├── server/
│   │   └── main.go
│   └── cli/
│       └── main.go
└── *_test.go             # Tests live alongside code
```

go.mod defines your module and dependencies:

```go
module github.com/yourname/my_project

go 1.25

require (
    github.com/gin-gonic/gin v1.9.1
    github.com/jackc/pgx/v5 v5.5.0
)
```

## Core Concepts

Go favors explicitness and simplicity over abstraction.

Packages and visibility:

```go
package main

import "fmt"

// Uppercase = exported (public), lowercase = unexported (private)
func PublicFunction() {}
func privateFunction() {}
```

Error handling:

Go doesn't have exceptions. Functions return errors explicitly:

```go
file, err := os.Open("config.yaml")
if err != nil {
    return fmt.Errorf("failed to open config: %w", err)
}
defer file.Close()
```

The `if err != nil` pattern is everywhere. It's verbose but makes error paths explicit.

Zero values:

Variables are initialized to their zero value — no null pointer surprises:

```go
var s string   // ""
var n int      // 0
var b bool     // false
var p *int     // nil
```

Pointers without arithmetic:

```go
func increment(n *int) {
    *n++
}

x := 5
increment(&x)  // x is now 6
```

## Common Patterns

Structs and methods:

```go
type Server struct {
    Host string
    Port int
}

// Method with receiver
// `(s *Server)` is the receiver part
func (s *Server) Address() string {
    return fmt.Sprintf("%s:%d", s.Host, s.Port)
}

// Constructor convention
func NewServer(host string, port int) *Server {
    return &Server{Host: host, Port: port}
}

server := NewServer("localhost", 8080)
fmt.Println(server.Address())
```

A Receiver is what turns a regular function into a method associated with a type. It's the thing in parentheses before the method name.

```go
// Pointer receiver - can modify the struct, avoids copying
func (s *Server) SetPort(p int) {
    s.Port = p  // actually modifies the original
}

// Value receiver - gets a copy, can't modify original
func (s Server) Address() string {
    return fmt.Sprintf("%s:%d", s.Host, s.Port)
}
```

Interfaces (implicit):

No `implements` keyword — if a type has the methods, it satisfies the interface:

```go
type Writer interface {
    Write([]byte) (int, error)
}

// MyBuffer doesn't declare "implements Writer" anywhere
type MyBuffer struct {
    data []byte
}

// But because it has this method with the right signature...
func (b *MyBuffer) Write(p []byte) (int, error) {
    b.data = append(b.data, p...)
    return len(p), nil
}

// ...it IS a Writer, and you can use it anywhere a Writer is expected
func SaveData(w Writer, data []byte) {
    w.Write(data)
}

buf := &MyBuffer{}
SaveData(buf, []byte("hello"))  // works!

// os.File, bytes.Buffer, net.Conn all satisfy Writer
// without explicitly declaring it
```

Goroutines and channels:

```go
// Start a goroutine
go func() {
    doWork()
}()

// Channels for communication
ch := make(chan string)

go func() {
    ch <- "result"  // Send
}()

msg := <-ch  // Receive
```

Context for cancellation:

```go
ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
defer cancel()

result, err := doWorkWithContext(ctx)
```

Defer for cleanup:

```go
func readFile(path string) error {
    f, err := os.Open(path)
    if err != nil {
        return err
    }
    defer f.Close()  // Runs when function returns
    
    // ... work with file
}
```

## Packages Worth Knowing

| Category | Package | Purpose |
| ------------ | ----------------- | ------------------------------------- |
| HTTP routing | chi, gin, echo | Web frameworks (stdlib is also solid) |
| Database | sqlx, pgx | SQL with less boilerplate |
| ORM | gorm, ent | Full ORM if you want one |
| CLI | cobra, urfave/cli | Command line apps |
| Config | viper | Configuration management |
| Logging | zap, zerolog | Structured logging |
| Testing | testify | Assertions and mocks |
| Validation | validator | Struct validation |

## When to Use Go

Good fit:

- Backend services and APIs - Simple concurrency model, fast compilation, easy deployment. The sweet spot for Go.
- CLI tools - Single binary, fast startup, cross-compilation built in. Terraform, Hugo, and GitHub CLI are all Go.
- Infrastructure and DevOps tooling - Docker, Kubernetes, Prometheus, Vault, Consul — the cloud-native ecosystem is largely Go.
- Network services - Proxies, load balancers, API gateways. Goroutines handle many concurrent connections efficiently.
- Microservices - Small footprint, fast builds, straightforward deployment.
- When team onboarding matters - Small language, easy to learn, code looks the same everywhere.

Not a good fit (use something else):

| Scenario | Better Choice | Why |
| --------------------------------------- | --------------------- | ----------------------------------------------------------- |
| Data science, ML, notebooks | Python | Ecosystem isn't there, iteration speed matters |
| Scripts and automation | Python, Bash | Too much ceremony for quick tasks |
| GUI applications | Swift, Kotlin, C# | Go's GUI story is weak |
| Systems requiring manual memory control | C, C++, Rust | Go has a garbage collector, no low-level memory access |
| Heavy numerical computing | Python (NumPy), Julia | No operator overloading, limited numeric libraries |
| Maximum possible performance | C, C++, Rust | GC pauses exist, less control over memory layout |
| Embedded systems | C, Rust | GC and runtime aren't suitable for constrained environments |

The trade-off:

Go optimizes for simplicity and maintainability over expressiveness. It deliberately omits features (generics were only added in 1.18, still no sum types, limited metaprogramming). This makes large codebases readable but can feel repetitive for complex abstractions.

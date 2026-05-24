# How Go Works

Go is a statically-typed, compiled language with a managed runtime. When you run `go run main.go` or build a binary with `go build`, the Go toolchain parses your source, type-checks it, compiles it directly to native machine code, and links it into a single self-contained executable. There's no separate VM or interpreter at runtime, just your code plus a small embedded runtime that handles goroutines, garbage collection, and a few other services.

## The Build Pipeline

When you build a Go program, the toolchain performs several steps:

1. Scanning: source files are tokenized into keywords, identifiers, operators, and literals.
1. Parsing: tokens are assembled into an Abstract Syntax Tree (AST) per file.
1. Type checking: the AST is checked against Go's type system; this is where most program errors surface.
1. SSA generation and optimization: the typed AST is lowered to Static Single Assignment form, where the compiler does most of its optimization work.
1. Code generation: SSA is lowered to machine code for the target architecture (amd64, arm64, etc.).
1. Linking: compiled packages and the Go runtime are linked into a single static binary.

```
source (.go) -> tokens -> AST -> typed AST -> SSA -> machine code -> linked binary
```

The output is a native executable with no external runtime dependency. You can scp a Go binary to a matching OS/arch machine and run it without installing Go there. This is one of the main reasons Go gets used for CLIs, containers, and distribution-heavy infrastructure.

### Why Tokens, then AST?

Most compiled and interpreted languages (Go, Python, Rust, Java, etc.) go through this two-step lexing-then-parsing pipeline rather than jumping straight from source text to an AST. It's a separation of concerns.

The lexer's job is to chew through raw bytes and answer "what kind of thing is this?" Is `func` a keyword or an identifier? Is `123` an integer literal? Is `//` the start of a comment? It deals with whitespace, comments, character encoding, and string escape sequences. Once that's done, the parser gets a clean stream of typed tokens and can focus purely on grammar: does this sequence of tokens form a valid function declaration?

If you tried to parse directly from characters, your grammar rules would be tangled up with "skip whitespace here, but not inside a string literal, and watch out for comments." Doable (some parsers do this, called scannerless parsing) but it makes the grammar uglier and harder to maintain.

The AST itself exists because it's a structured representation that throws away syntactic noise (parentheses, semicolons, whitespace) and keeps only the meaning. `1 + 2 * 3` and `1 + (2 * 3)` produce the same AST because they mean the same thing. Every subsequent compiler stage (type checking, optimization, code generation) wants to ask questions like "what are the children of this expression?" or "what type does this identifier resolve to?" Trivial on a tree, miserable on a flat token stream or raw text.

### `go run` vs `go build`

`go run main.go` compiles the program to a temporary directory, runs it, and discards the binary. It's convenient for quick iteration but does the full compile every time. `go build` produces a persistent binary in the current directory. `go install` produces a binary in `$GOBIN` (usually `$HOME/go/bin`). All three go through the same compile pipeline; the difference is only what happens to the output.

### Compile-time vs Run-time Errors

Because Go is statically typed and compiled, a huge class of errors that would be runtime issues in Python become compile-time errors here: misspelled names, wrong argument types, accessing fields that don't exist, returning the wrong number of values. The compiler also rejects programs with unused imports or unused local variables, which is unusual and occasionally annoying but keeps the codebase tidy.

Errors that still happen at runtime: nil pointer dereferences, index-out-of-range, type assertion failures on interfaces, division by zero on integers, and anything you explicitly `panic` on.

## Modules and the Module Cache

A Go module is a collection of packages versioned as a unit, identified by a module path declared in `go.mod` at the module's root.

```
myapp/
├── go.mod              # module github.com/jacob/myapp, go 1.23, dependency list
├── go.sum              # cryptographic hashes of dependencies for verification
├── main.go
└── internal/
    └── store/
        └── store.go
```

`go.mod` declares the module's path, the Go version, and its dependencies with their selected versions. `go.sum` records hashes of every dependency (and every dependency's dependencies) for reproducibility and tamper detection. Both files are committed.

### How Dependencies are Resolved

When you `go build` or `go test`, the toolchain reads `go.mod`, downloads any missing modules into the module cache (default `$HOME/go/pkg/mod/`), and compiles against them. There's no per-project `node_modules/` or `.venv/` equivalent. The cache is shared across all projects on the machine. Each version of each module lives in its own immutable directory in the cache, so two projects depending on different versions of the same library coexist without conflict.

- The module cache is read-only by default. `go clean -modcache` wipes it if you need to.
- Dependencies are fetched from a module proxy (default `proxy.golang.org`), which caches versions and serves them as zip files. This makes builds reproducible even if the upstream repo disappears.
- `go mod tidy` reconciles `go.mod` and `go.sum` with what your code actually imports, adding missing entries and removing unused ones.

### Module Hosts: Not Just GitHub

Nothing about Go modules is GitHub-specific. The import path is just a string. By convention it looks like a URL because the toolchain uses it to fetch the code, but the host can be anything that speaks the right protocol. GitLab works fine:

```go
import "gitlab.com/yourorg/yourmodule/pkg/thing"
```

Bitbucket, self-hosted Gitea, your own server, all work. Go's `go get` does a lookup against the import path to figure out where to fetch from. For well-known hosts (github.com, gitlab.com, bitbucket.org) it has built-in knowledge of the URL scheme. For custom hosts, you serve a small HTML meta tag at the import path telling Go where the actual git repo lives. This is the "vanity import" mechanism, and it's how `k8s.io/client-go` works even though the code is on GitHub.

You can also work entirely offline or with private repos. `GOPRIVATE=gitlab.mycompany.com/*` tells Go to skip the public proxy and fetch directly. Module paths are conceptually independent of any specific forge.

### Minimum Version Selection

Go uses Minimum Version Selection (MVS) instead of the SAT-solver-style resolution npm and pip use. Each module declares the minimum version of each dependency it needs; the build picks the highest of those minimums across the whole graph. The result is deterministic, fast, and doesn't require lockfiles in the traditional sense (`go.sum` is a hash manifest, not a resolution lockfile). The tradeoff is that you sometimes get older versions than you'd expect because nothing in the graph asked for a newer one.

## GOPATH and the Workspace

Historically, Go required all code to live under `$GOPATH/src/`, with imports resolved by directory structure. That's gone in modules mode (Go 1.16+ defaults). Today:

- `$GOPATH` still exists, but its only practical roles are housing the module cache (`$GOPATH/pkg/mod/`) and installed binaries (`$GOPATH/bin/`).
- Your project can live anywhere on disk. The presence of `go.mod` marks the module root.
- `go.work` files enable multi-module workspaces for local development across several modules at once, without publishing intermediate versions.

## How Imports Work

Go imports are resolved at compile time, not at runtime. There's no `sys.path` equivalent and no dynamic import. Every import is a fully-qualified path declared in the source file:

```go
import (
    "fmt"                              // standard library
    "net/http"                         // standard library, nested
    "github.com/jacob/myapp/internal/store"  // local package in this module
    "github.com/google/uuid"           // third-party dependency
)
```

The compiler resolves each import path against:

1. The standard library, baked into the Go installation.
1. The current module (anything under the module path declared in `go.mod`).
1. Dependencies listed in `go.mod`, fetched from the module cache.

### Packages, Not Files

The unit of compilation in Go is the package, not the file. A package is all `.go` files in a single directory that share the same `package` declaration at the top. Files in the same package can reference each other's identifiers without imports. They're effectively one big translation unit.

```
internal/store/
├── store.go         // package store
├── postgres.go      // package store
└── memory.go        // package store
```

All three files compile together as package `store`. Anything exported (capitalized identifier) is visible to other packages that import this one; anything lowercase is package-private.

### Importing a Package vs Importing a Directory Tree

There's no such thing as importing a directory tree in Go. You import one package at a time, and a package is exactly one directory's worth of files sharing a `package` declaration. So if you have:

```
internal/
├── store/
│   └── store.go      // package store
└── sync/
    └── sync.go       // package sync
```

You'd import each child package individually:

```go
import (
    "github.com/jacob/myapp/internal/store"
    "github.com/jacob/myapp/internal/sync"
)
```

You can't write `import "github.com/jacob/myapp/internal"` to bring in everything underneath. `internal/` is just a folder, not a package. (If you put `.go` files directly inside `internal/` itself, those would form a package importable at that path, but that's unusual.)

By convention the package name matches the directory name, but it doesn't have to. The package name is whatever's in the `package X` declaration; the import path is the directory location.

### What You Get from an Import

When you `import "github.com/jacob/myapp/internal/store"`, you get access to every capitalized identifier in that package: `store.Get`, `store.User`, `store.ErrNotFound`. Lowercase identifiers like `store.cache` or `store.parseRow` exist but the compiler won't let you reference them from outside the package. There's no way to selectively import "only these names" the way Python's `from x import y` works. You always get the whole package's exported surface, namespaced under the package name.

### The `internal/` Convention

Any package under a directory named `internal/` can only be imported by code rooted at the parent of that `internal/` directory. So `github.com/jacob/myapp/internal/store` is importable by `github.com/jacob/myapp/main.go` but not by some other module that depends on yours. This is enforced by the compiler. It's the standard way to mark code as "implementation detail, not API." Note that `internal/` is a special directory name to the compiler for access control; it's not itself a package.

### No Circular Imports

Go forbids circular imports at the package level, full stop. If package A imports B, B cannot import A, directly or transitively. The compiler rejects it. This forces you to think about dependency direction up front, and pushes shared types into a third package that both depend on.

### Initialization Order

When a package is imported, Go runs:

1. Package-level variable initializers, in declaration order across files (with dependencies between them resolved).
1. Every `init()` function in the package, in the order files are presented to the compiler.

Imports are initialized depth-first before the importing package's own init runs. Each package is initialized exactly once per program. `main.main` runs last, after every transitively imported package has finished initializing.

## The Runtime

Compiled Go binaries embed a runtime written in Go and assembly. It's small compared to a JVM or CPython, but it's doing real work:

- Goroutine scheduler: multiplexes goroutines (lightweight, user-space "threads") onto OS threads. The scheduler is preemptive since Go 1.14, so a tight loop in one goroutine can't starve others.
- Garbage collector: concurrent, tri-color mark-and-sweep, tuned for low pause times (sub-millisecond typical). Runs in parallel with your program on dedicated GC worker goroutines.
- Memory allocator: per-P (processor) thread-local caches backed by central heaps, similar in spirit to tcmalloc.
- Network poller: integrates with epoll/kqueue/IOCP so blocking I/O on a goroutine doesn't block its OS thread; the runtime parks the goroutine and resumes it when the fd is ready.

The runtime is why `go func() { ... }()` is cheap and why a Go server can handle tens of thousands of concurrent connections without thread-per-connection costs.

### What "Multiplexing" Means Here

Multiplexing means many-to-few mapping. You might have 50,000 goroutines but only 8 OS threads (one per CPU core). The scheduler is constantly deciding which goroutines run on which threads, swapping them in and out. One thread will run goroutine A for a bit, then park A and run goroutine B, then C, then back to A. From the OS's perspective there are just 8 threads doing work; from your code's perspective there are 50,000 independent execution contexts. That's multiplexing: sharing a smaller resource (threads) among a larger set of consumers (goroutines).

It's the same word used in networking ("multiplexing connections over a single socket") and electronics ("multiplexing signals on one wire"). General concept: many logical things sharing one physical thing via time-slicing or interleaving.

### Cooperative vs Preemptive Scheduling

- Cooperative: a goroutine only yields control when it hits a "safe point", a function call, a channel operation, a syscall, etc. If a goroutine runs a tight loop with no function calls, it never yields, and other goroutines starve.
- Preemptive: the runtime can interrupt a goroutine at (almost) any instruction and switch to another one, whether the goroutine cooperated or not.

Before Go 1.14, Go was effectively cooperative. You could write a `for { x++ }` loop and it would hang the whole scheduler. No other goroutines on that thread would get to run, GC couldn't proceed, etc. Go 1.14 added signal-based preemption: the runtime sends the thread a signal, the signal handler hijacks the stack, and the goroutine gets paused at an arbitrary point. Now tight loops can't starve the scheduler. This is a meaningful behavioral guarantee, not just an implementation detail.

## Concurrency: Goroutines and Channels

Go's concurrency model is built on two primitives:

- Goroutines: `go someFunc()` schedules a function to run concurrently. Goroutines start with a small stack (~2 KB) that grows and shrinks dynamically, so you can have millions of them.
- Channels: typed conduits for sending values between goroutines, with optional buffering. `ch <- v` sends, `v := <-ch` receives. Unbuffered channels synchronize sender and receiver.

```go
results := make(chan int, 10)
for _, item := range items {
    go func(it Item) {
        results <- process(it)
    }(item)
}
```

Unlike Python's processes-vs-threads dichotomy, goroutines are genuinely parallel on multiple cores (subject to `GOMAXPROCS`, which defaults to the number of CPUs), and they share memory directly. There's no GIL. The flip side is that you need to think about data races; the race detector (`go test -race`, `go run -race`) is essential.

The idiomatic guidance is "share memory by communicating", pass values over channels rather than mutating shared state behind locks. In practice real codebases use both, and `sync.Mutex`, `sync.RWMutex`, and `sync.WaitGroup` are perfectly idiomatic when channels would be awkward.

## Error Handling

Go has no exceptions for ordinary control flow. Functions return errors as values:

```go
result, err := doThing()
if err != nil {
    return fmt.Errorf("doing thing: %w", err)
}
```

The `%w` verb wraps an error so callers can `errors.Is` or `errors.As` it to inspect the chain. `panic` exists but is reserved for unrecoverable programmer errors (nil dereference, impossible invariants); library and application code should return errors instead. `defer`/`recover` can catch panics at goroutine boundaries, mostly used to keep a server from crashing on a bug in one request handler.

### When to Panic (and When Not To)

Panic is for "this should be impossible, and if it happened my program's assumptions are broken." Not for "something went wrong that the caller might want to handle."

Reasonable uses for `panic`:

- Programmer errors in library code. `regexp.MustCompile("[invalid")` panics because passing a literal invalid regex is a bug in your source, not a runtime condition. The non-`Must` version returns an error for cases where the pattern comes from user input.
- Initialization failures that make the program unusable. A database driver that can't load its required SQL grammar file at init time. There's no recovery, the program shouldn't continue.
- Invariant violations. "I just inserted into this map, the key must be present." If the assertion fails, the data structure is corrupt and continuing is dangerous.
- `Must` constructors. Common pattern for "I'm setting this up at startup with known-good inputs; if it fails, crash immediately."

Don't panic for:

- Network errors, timeouts, connection failures. These are expected, callers want to retry or fail gracefully. Return an error.
- File not found, permission denied, disk full. Totally normal operational conditions.
- Bad user input. Validation failures get returned as errors. A JSON parse failure on a request body is a 400 response, not a crashed process.
- Database query errors. Even "table not found", return it, let the caller log and continue.
- Anything in a request handler that you don't want to take down the server. If you do panic in a handler, the HTTP server's default recovery will catch it and return 500, but you've still lost any in-flight work for that request.

The mental test: if this happens, can any sensible caller do anything other than crash? If yes, return an error. If no, and continuing would be unsafe or nonsensical, panic. In practice, application code rarely panics intentionally. It's almost always library code with a `Must*` variant, or genuine "this can't happen" assertions.

One related point: panics propagate up through goroutines independently. A panic in goroutine A won't be caught by a `recover` in goroutine B. If you spawn goroutines that might panic, each one needs its own `defer recover()` if you want to handle it, otherwise the whole process dies.

## Build Modes and Cross-Compilation

`go build` defaults to a statically-linked binary for your current OS and architecture. Cross-compiling is built in:

```bash
GOOS=linux GOARCH=arm64 go build ./cmd/myapp
```

No toolchain to install, no Docker, no cross-compiler. The standard distribution can target every supported platform out of the box. This is why Go got popular for shipping container images: `FROM scratch` plus a single statically-linked binary is a valid, working image.

CGo (calling C code from Go) breaks pure static linking and complicates cross-compilation, so most idiomatic Go code avoids it where possible.

## Tooling Worth Knowing

- `go fmt` (or `gofmt`): canonical formatter. There's one correct format and the tool enforces it; no style debates.
- `go vet`: catches common bugs the compiler doesn't (printf format mismatches, copying locks, suspicious shadowing).
- `go test`: built-in testing, benchmarking, and coverage. Tests live in `_test.go` files in the same package.
- `go mod tidy`: reconciles `go.mod` with actual imports.
- `go doc`: pulls docs straight from source comments.
- `staticcheck`, `golangci-lint`: community linters that catch a much wider set of issues than `go vet` alone.

## When to Use Go (and When Not To)

Go has a fairly well-defined sweet spot. Outside it, other languages usually win.

### Where Go Shines

Network services with high concurrency. This is the canonical use case. An API at thousands of req/s is comfortably in Go territory, with a single process on modest hardware handling it without breaking a sweat, often with p99 latencies in single-digit milliseconds. The goroutine-per-request model means you write straightforward synchronous-looking code and the runtime handles the concurrency. You don't need an async framework, an event loop library, or worker pools to scale up. The stdlib's `net/http` is genuinely production-grade; you don't need a framework to ship a real service.

CLIs and operational tools. Single statically-linked binary, cross-compile from your laptop to every target, no runtime to install. `kubectl`, `terraform`, `docker`, `helm`, `gh`, `hugo`, `caddy` are all Go for these reasons. If you're building something that ops teams will install across heterogeneous machines, or that needs to ship in scratch containers, Go is hard to beat.

Infrastructure plumbing. Service meshes, proxies, agents, sidecars, sync daemons, gRPC backends. Things that need to be fast, resource-efficient, deal with lots of connections, and run forever without leaking. The combination of low memory footprint, fast startup, and good concurrency is almost ideal here.

Cron-style automation jobs that need to do real work. Anything where you're orchestrating HTTP calls, doing modest transforms, writing to databases, sending email. Go is great because the concurrency lets you parallelize the IO trivially, and the single-binary deploy makes it easy to ship as a Kubernetes CronJob or systemd timer.

Stream processing and protocol implementations. Anything where you're shuffling bytes between sockets, parsing protocols, multiplexing connections. Go's channels and goroutines map well onto this work, and the performance is close to C++ for most realistic workloads.

### Where Go Is Fine but Not Obviously Better

Internal web apps with light traffic. You can absolutely build a CRUD app in Go, and the result will be fast and reliable. But Django or Rails will get you there in half the code with batteries included (admin UI, ORM, auth, migrations, forms). If the bottleneck is "how fast can I build the next feature" rather than "how fast can I serve requests," Go's verbosity starts to cost you.

Background job processing. Go works well here (River is a great example). But Python with Celery or Ruby with Sidekiq are also mature ecosystems, and if the jobs themselves are doing Python-y work (ML inference, calling pandas, sklearn), staying in Python keeps the data path simple.

Glue code and scripting. Bash for small stuff, Python for medium stuff. Go's `fmt.Println("hello")` requires a `main` function, a `package main` declaration, and a `func`. For a 20-line script, that's overhead. Go has no REPL either, which hurts for exploratory work.

### Where to Reach for Something Else

Data science and analytics work. Python wins decisively. The ecosystem isn't catchable: pandas, polars, duckdb, scikit-learn, pytorch, jupyter, matplotlib, statsmodels, the whole HuggingFace stack. Even when individual Go libraries exist (gonum, gorgonia), they're a fraction of the functionality and lack the interactive workflow data work requires. The exceptions are when "data" means "high-throughput streaming pipelines" rather than "analytical exploration." Building a Kafka consumer that shovels events through a transformation and into a sink at high throughput is great in Go. Computing rolling regressions over years of price data with custom feature engineering is Python.

Frontend or anything with a UI. Go has no real story for this. TypeScript and the JS ecosystem own this space. You can server-render HTML from Go (and `templ` is nice), but you're not building rich interactivity in Go. For user-facing apps, Next.js or SvelteKit will be a much better time. WASM exists but is niche.

ML/AI workloads. Python, full stop, for both training and most inference. If you need to serve a model at very high throughput with strict latency, you might wrap inference in a Go service that calls into ONNX runtime or Triton via gRPC, but the model itself is being trained and exported from the Python ecosystem. Rust is starting to encroach on inference serving (candle, burn) but Go isn't really in the conversation.

Systems programming where you need control. Kernels, embedded, real-time, drivers, anything where GC pauses are unacceptable or you need precise memory layout. Rust or C++. Go's GC is great but it's still a GC, and the runtime overhead is real if you're trying to fit on a microcontroller or guarantee sub-100µs latency.

Heavy CPU-bound numerical work. Matrix math, simulations, scientific computing. Use NumPy/JAX/PyTorch (which is C++/CUDA under the hood) or Julia or Fortran or Rust. Go is "fine" at this but not optimized for it, and you'd rewrite the hot loops in something else anyway.

Quick prototypes. Python. The REPL, the dynamic typing, the dense expressiveness all compound. By the time you've written Go's `if err != nil` for the third time, your Python prototype is running. The right time to reach for Go is when you've decided what you're building and now want it to be reliable and fast.

### The Framing

Go is for the part of the system that runs continuously and needs to be efficient. Python is for the part that does the thinking. JS/TS is for the part that humans look at. Most non-trivial systems eventually have all three.

## Key Takeaways

- Go compiles to native machine code and links statically; the output is a single binary with no runtime install needed on the target.
- The unit of compilation is the package (a directory of files sharing a `package` declaration), not the file.
- Modules (`go.mod`) define dependency boundaries; dependencies live in a shared, immutable module cache, not per-project.
- Imports are resolved at compile time against the stdlib, the current module, and entries in `go.mod`. No dynamic imports, no circular imports. One package per directory; you can't import a directory tree.
- Module hosting is not GitHub-specific. Any git host works, and vanity imports let you decouple the import path from the actual repo location.
- The runtime gives you goroutines (cheap, preemptively scheduled since Go 1.14), channels, a concurrent GC, and a network poller. Concurrency is genuinely parallel and there's no GIL.
- Errors are values returned from functions; panic is for unrecoverable bugs, not control flow.
- Cross-compilation is built in; `GOOS` and `GOARCH` env vars are all you need.
- Go's sweet spot is network services, CLIs, infrastructure tooling, and IO-heavy automation. Reach for Python for data/ML/analytics work and for prototypes; reach for TS for anything with a UI.

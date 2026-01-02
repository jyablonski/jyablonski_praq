# Rust

[Guide](https://doc.rust-lang.org/book/ch00-00-introduction.html)

Rust is a systems programming language focused on safety, speed, and concurrency. It is designed to provide memory safety without using garbage collection, making it suitable for performance-critical applications.

## Why Rust?

- Memory safety without GC - Ownership system catches memory bugs at compile time (no null pointers, dangling references, or data races)
- Zero-cost abstractions - High-level features compile down to efficient machine code
- Fearless concurrency - The type system prevents data races, making multithreaded code safer
- Modern tooling - Cargo handles dependencies, building, testing, and docs out of the box
- Great error messages - The compiler tells you what's wrong and often how to fix it
- Growing ecosystem - Strong adoption in CLI tools, WebAssembly, embedded systems, and infrastructure

## Components

- rustc - The Rust compiler, translates `.rs` files into executables
- Cargo - Package manager and build system (like npm + webpack in one). Handles dependencies, builds, tests, docs, and publishing
- Rustup - Toolchain manager for installing and switching between Rust versions (stable, beta, nightly)
- Crates - Rust's term for packages/libraries. Published to [crates.io](https://crates.io)
- Clippy - Linter that catches common mistakes and suggests idiomatic improvements
- rustfmt - Auto-formatter for consistent code style

## Use Cases

## When to Use Rust

Good fit:

- CLI tools - Fast startup, single binary distribution, no runtime dependencies. Tools like ripgrep, fd, bat, and exa are Rust rewrites of classic Unix tools that are significantly faster.
- Systems programming - OS components, device drivers, embedded systems. Rust is replacing C/C++ in security-critical contexts (Linux kernel now accepts Rust).
- WebAssembly - Rust has first-class WASM support. Great for performance-critical browser code or edge computing (Cloudflare Workers, Fastly).
- Infrastructure tooling - Projects where correctness and performance matter: databases, message queues, proxies. Examples: Firecracker (AWS Lambda's VM), TiKV, Vector.
- Game engines and graphics - Low-level control without memory bugs. Bevy is a growing Rust game engine.
- Cryptocurrency/blockchain - Memory safety is critical when bugs mean lost money. Solana, Polkadot, and many others use Rust.
- Performance-critical services - When you've profiled and need more speed than GC languages provide, especially for latency-sensitive workloads.

Not a good fit (use something else):

| Scenario | Better Choice | Why |
| ---------------------------- | ------------- | -------------------------------------------------------------------------------------------------- |
| Quick scripts and automation | Python | Rust's compile times and verbosity slow you down for throwaway code |
| Data analysis, ML, notebooks | Python | Ecosystem (pandas, numpy, sklearn) is unmatched, iteration speed matters more than runtime |
| Rapid API prototyping | Go, Python | Faster to get something running, easier onboarding for teams |
| Enterprise CRUD apps | Go, Java, C# | Rust's learning curve isn't worth it when you're mostly shuffling JSON between a database and HTTP |
| Glue code and orchestration | Python | When you're calling other services and not doing heavy computation |
| Small team, tight deadline | Go | Simpler language, faster to productive, still good performance |
| Throwaway/exploratory work | Python | When you're figuring out what to build, not optimizing how to build it |

The trade-off:

Rust makes you pay upfront (steeper learning curve, longer compile times, fighting the borrow checker) in exchange for runtime guarantees and performance. If you don't need those guarantees or performance, that upfront cost isn't worth it.

Go is often the pragmatic middle ground; it's faster than Python, simpler than Rust, good enough performance for most backend services.

## Quick Start

[Install Guide](https://rust-lang.org/learn/get-started/)

Install Rust using their preferred method which is the curl script, this lets you easily manage Rust versions with rustup.

- `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh`

This installs:

- `rustc` - The Rust compiler
- `cargo` - The Rust package manager and build tool
- `rustup` - The Rust toolchain installer
- And other standard Rust tools

After install, source the env file or restart your shell:

- `. "$HOME/.cargo/env"`

## Commands

```sh
# Project management
cargo new my_project      # Create new binary project
cargo new my_lib --lib    # Create new library project
cargo init                # Initialize in existing directory

# Building and running
cargo build               # Compile (debug mode)
cargo build --release     # Compile with optimizations
cargo run                 # Build and run
cargo run --release       # Build and run optimized

# Testing and checks
cargo test                # Run tests
cargo check               # Fast compile check without producing binary
cargo clippy              # Run linter

# Dependencies
cargo add serde           # Add a dependency
cargo update              # Update dependencies
cargo tree                # Show dependency tree

# Toolchain management (rustup)
rustup update             # Update Rust toolchains
rustup default stable     # Set default toolchain
rustup show               # Show installed toolchains

# Other
cargo fmt                 # Format code
cargo doc --open          # Generate and open documentation
cargo publish             # Publish crate to crates.io
```

## Standardization

Rust is like Go in terms of formatting, where there's a strong emphasis on having a single, standardized way to format code.

rustfmt is the official formatter and it's widely adopted, most Rust projects just use the defaults. You run `cargo fmt` and it handles everything. The Rust community has largely standardized around it, so open source crates, tooling, and CI pipelines all expect rustfmt-formatted code.

Clippy adds another layer of opinionation as the official linter, pushing you toward idiomatic Rust patterns.

Key difference from Go though: rustfmt is more configurable. You can create a `rustfmt.toml` to tweak things like max line width, import grouping, brace styles, etc. Go's `gofmt` is deliberately zero-config — you get what you get.

So Rust hits a middle ground:

- Strong defaults that 90% of projects use as-is
- Escape hatches if you really need them
- Community expectation that you're using rustfmt either way

The practical effect is the same as Go, you open any Rust codebase and it looks familiar. No team arguments about tabs vs spaces or brace placement.

## Project Structure

A typical Cargo project looks like this:

```
my_project/
├── Cargo.toml          # Project manifest (dependencies, metadata)
├── Cargo.lock          # Locked dependency versions (commit for binaries, ignore for libraries)
├── src/
│   ├── main.rs         # Entry point for binaries
│   ├── lib.rs          # Entry point for libraries
│   └── bin/            # Additional binaries
├── tests/              # Integration tests
├── benches/            # Benchmarks
└── examples/           # Example usage code
```

Cargo.toml is like `package.json` or `go.mod`, it just defines your project and dependencies:

```toml
[package]
name = "my_project"
version = "0.1.0"
edition = "2021"

[dependencies]
serde = { version = "1.0", features = ["derive"] }
tokio = { version = "1", features = ["full"] }
```

## Ownership Basics

Rust's defining feature - memory safety enforced at compile time with no garbage collector.

Three rules:

1. Each value has exactly one owner
1. When the owner goes out of scope, the value is dropped (freed)
1. You can have either one mutable reference OR any number of immutable references (not both)

```rust
let s1 = String::from("hello");
let s2 = s1;              // s1 is "moved" to s2, s1 is now invalid
// println!("{}", s1);    // Compile error: s1 no longer owns the data

let s3 = s2.clone();      // Explicit deep copy if you need both
```

Borrowing lets you reference data without taking ownership:

```rust
fn print_length(s: &String) {    // Borrows immutably
    println!("{}", s.len());
}

fn add_suffix(s: &mut String) {  // Borrows mutably
    s.push_str("!");
}
```

This catches entire categories of bugs at compile time: use-after-free, double-free, data races, null pointer dereferences.

## Common Patterns

Error handling with Result:

Rust doesn't have exceptions. Functions that can fail return `Result<T, E>`:

```rust
use std::fs::File;

fn read_config() -> Result<String, std::io::Error> {
    let contents = std::fs::read_to_string("config.toml")?;  // ? propagates errors
    Ok(contents)
}

// Handling results
match read_config() {
    Ok(config) => println!("Config: {}", config),
    Err(e) => eprintln!("Failed to read config: {}", e),
}
```

Option for nullable values:

No null in Rust. Use `Option<T>` to represent something that might not exist:

```rust
fn find_user(id: u32) -> Option<User> {
    // Returns Some(user) or None
}

if let Some(user) = find_user(42) {
    println!("Found: {}", user.name);
}
```

Structs and impl blocks:

```rust
struct Server {
    host: String,
    port: u16,
}

impl Server {
    // Constructor (convention is `new`)
    fn new(host: String, port: u16) -> Self {
        Self { host, port }
    }

    // Method (takes &self)
    fn address(&self) -> String {
        format!("{}:{}", self.host, self.port)
    }
}

let server = Server::new("localhost".to_string(), 8080);
println!("{}", server.address());
```

Traits (like interfaces):

```rust
trait Describe {
    fn describe(&self) -> String;
}

impl Describe for Server {
    fn describe(&self) -> String {
        format!("Server running at {}", self.address())
    }
}
```

## Crates Worth Knowing

| Category | Crate | Purpose |
| -------------- | ----------------- | ---------------------------------- |
| Serialization | serde | JSON, YAML, TOML, etc. |
| Async runtime | tokio | Async I/O, networking |
| HTTP client | reqwest | HTTP requests |
| HTTP server | axum, actix-web | Web frameworks |
| CLI parsing | clap | Command line argument parsing |
| Error handling | anyhow, thiserror | Simplified error types |
| Logging | tracing | Structured logging and diagnostics |
| Database | sqlx, diesel | SQL with compile-time checks |

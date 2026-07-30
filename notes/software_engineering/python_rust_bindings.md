# Python and Rust Bindings

Python bindings let Python code call functions implemented in a compiled language such as C, C++, or Rust. To the caller, the compiled code usually looks like an ordinary Python module:

```python
from fast_math import sum_squares

result = sum_squares([1.0, 2.0, 3.0])
```

The implementation of `sum_squares` can run as optimized native machine code even though the surrounding application, notebook, or data pipeline remains Python.

## Why Python Can Call Native Code

Most people run Python through CPython, the reference interpreter written primarily in C. CPython exposes a C API and an application binary interface (ABI) that native libraries can use to:

- Receive Python values and convert them into native values.
- Create and return Python objects.
- Raise Python exceptions.
- Define functions, classes, and modules that participate in Python's normal import system.

When Python imports a compiled extension, its import machinery loads a shared library instead of a `.py` file. The importable extension is normally a `.so` file on Linux and macOS or a `.pyd` file on Windows. It exports a specially named initialization function that CPython calls to construct the module.

```
Python call
    -> CPython extension API
    -> conversion from Python objects to native values
    -> compiled C or Rust function
    -> conversion back to Python objects
    -> Python result or exception
```

C can implement this interface directly because CPython's extension API is a C API. Rust does not use the C ABI by default, but it can compile a C-compatible shared library. A binding library such as PyO3 generates the glue needed to expose safe, ergonomic Rust functions through CPython's C interface.

Python can also load ordinary C-compatible libraries through `ctypes` or `cffi`. Those approaches are useful when a library already has a C API. PyO3 is usually more convenient when designing a Python extension in Rust because it understands Python objects, exceptions, modules, classes, and packaging.

## Why Bindings Improve Performance

Python's dynamic object model and bytecode interpreter make the language productive and flexible, but each operation in a tight Python loop has overhead. CPython must repeatedly inspect object types, dispatch operations, manage reference counts, and execute bytecode instructions.

Compiled Rust or C code works with concrete native types and is compiled ahead of time into optimized machine code. It can process a large amount of data inside one call without returning to the Python interpreter for every iteration. Rust also provides memory safety without garbage collection and makes it possible to use multiple threads for suitable work.

Bindings are especially useful for:

- Numeric algorithms and simulations.
- Parsing, compression, serialization, and hashing.
- Image, audio, and signal processing.
- DataFrame, database, and query-engine internals.
- Tokenization and other CPU-intensive text processing.

This architecture is already common in the Python ecosystem. Libraries expose a friendly Python API while their expensive operations run in native code.

The important unit of optimization is a substantial operation, not an individual addition or property lookup. Every Python-to-Rust call requires argument validation and conversion. Calling Rust millions of times for tiny operations can be slower than staying in Python, and copying a large collection into a new Rust allocation can erase much of the gain. Good bindings move an entire loop or algorithm across the boundary and, where possible, borrow contiguous buffers instead of copying them.

## The Typical Rust Stack

A small Python/Rust extension commonly uses:

- A Rust toolchain: `rustc` compiles the code, while Cargo manages Rust dependencies and builds.
- PyO3: a Rust crate that provides Python-aware types, macros, error handling, and CPython interoperability.
- Maturin: a Python packaging and build tool that compiles the Rust crate and produces an installable Python wheel.
- Python and a virtual environment: used to install, import, and test the extension.
- Python development headers: sometimes required when building locally, commonly provided by a package such as `python3-dev` or `python3-devel` on Linux.

PyO3 is declared in `Cargo.toml` because it is a Rust dependency. Maturin can be installed as a Python development dependency with `pip`, `uv`, or another Python package manager. `setuptools-rust` is an alternative build integration, but PyO3 plus maturin is the common straightforward starting point.

## Roughly How It Is Built

Maturin can scaffold a project:

```bash
mkdir fast-math
cd fast-math
python -m venv .venv
source .venv/bin/activate
python -m pip install maturin
maturin init --bindings pyo3
```

The generated project has both Python packaging metadata and a Rust crate:

```
fast-math/
├── Cargo.toml
├── pyproject.toml
└── src/
    └── lib.rs
```

`Cargo.toml` configures a dynamic library and includes PyO3:

```toml
[lib]
name = "fast_math"
crate-type = ["cdylib"]

[dependencies]
pyo3 = "0.29"
```

The version above is illustrative. `maturin init` selects a compatible PyO3 version when it creates the project, and Cargo records the resolved dependency versions in `Cargo.lock`. Older PyO3 releases required an `extension-module` feature in this configuration; current maturin and PyO3 releases handle that extension setup automatically.

`pyproject.toml` tells Python packaging tools to build the project with maturin:

```toml
[build-system]
requires = ["maturin>=1,<2"]
build-backend = "maturin"

[project]
name = "fast-math"
requires-python = ">=3.10"
dynamic = ["version"]
```

The Rust module can expose a function with PyO3 macros:

```rust
use pyo3::prelude::*;

#[pyfunction]
fn sum_squares(values: Vec<f64>) -> f64 {
    values.iter().map(|value| value * value).sum()
}

#[pymodule]
fn fast_math(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_function(wrap_pyfunction!(sum_squares, module)?)?;
    Ok(())
}
```

PyO3 generates the CPython-facing wrapper. It converts the Python sequence into a Rust `Vec<f64>`, calls the Rust function, converts the result into a Python `float`, and turns conversion failures into Python exceptions.

During development, maturin can compile an optimized extension and install it into the active virtual environment:

```bash
maturin develop --release
python -c "from fast_math import sum_squares; print(sum_squares([1.0, 2.0, 3.0]))"
```

For distribution, `maturin build --release` creates wheel files. Wheels contain the compiled extension, so builds are specific to supported operating systems, CPU architectures, and Python ABIs. A published package will usually build and test a wheel matrix in CI. Projects may use Python's limited API and `abi3` to let one wheel work across several CPython versions, although this can restrict which CPython features the extension uses.

## The GIL and Parallel Work

On a traditional GIL-enabled CPython build, calling a Rust extension does not automatically bypass the Global Interpreter Lock (GIL). Rust code initially runs while the calling Python thread owns the GIL. This is necessary while it reads or creates Python objects.

For long-running work that no longer touches Python objects, a binding can call PyO3's `Python::detach` and operate only on Rust-owned data. On a GIL-enabled build this releases the GIL so other Python threads can run, and the Rust implementation can use its own worker threads when the algorithm is safe to parallelize. Before returning Python objects, the extension must attach to the interpreter again.

This separation is useful both for correctness and performance:

1. Validate and convert inputs while attached to the Python interpreter.
1. Detach from the interpreter and perform expensive work using Rust-owned values.
1. Attach to the interpreter again and convert the result back to Python.

Native code must still be designed carefully. Releasing the GIL does not make shared data automatically thread-safe, and panics or unsafe foreign-function interface code must not be allowed to unwind across the C boundary.

Modern CPython also offers free-threaded builds that can run without the GIL. PyO3 supports them, but extension authors must ensure their Rust and unsafe code are genuinely thread-safe. Detaching during long Rust-only work remains useful because it lets the interpreter coordinate events such as garbage collection without waiting on that work.

## The User Outcome

The end user normally does not need Rust, Cargo, or a compiler. They install a prebuilt wheel from a package index and use a normal Python interface:

```bash
pip install fast-math
```

```python
from fast_math import sum_squares

total = sum_squares(measurements)
```

This creates a useful division of responsibilities:

- Python provides the approachable API, rapid iteration, notebooks, orchestration, and compatibility with the broader Python ecosystem.
- Rust provides optimized native execution, predictable memory use, memory safety, and optional parallelism for performance-critical internals.
- Wheels hide the native build from most users and make the package install like any other Python dependency.

The result is not that Python itself becomes faster. Instead, Python coordinates the program while selected hotspots execute as compiled Rust code. Users keep the interface and workflow they expect from Python while receiving native performance where it matters.

## Practical Tradeoffs

- Measure first. A Rust rewrite adds build and packaging complexity and is worthwhile only when profiling shows a meaningful hotspot.
- Keep the boundary coarse. Pass enough work per call to outweigh conversion and dispatch overhead.
- Avoid unnecessary copies. Buffer-aware types and libraries such as NumPy can let native code operate on existing memory, subject to lifetime and mutability rules.
- Preserve Python ergonomics. Expose Python exceptions, type hints, docstrings, and familiar data types rather than leaking Rust implementation details.
- Test both sides. Rust unit tests validate the core algorithm, while Python tests validate imports, conversions, errors, and the public API.
- Plan distribution early. Native wheels must be built for each supported platform and architecture; source-only releases require users to have a compatible Rust toolchain.
- Benchmark realistic inputs. A microbenchmark of the native loop alone does not include boundary conversions, allocations, or the surrounding Python workflow.

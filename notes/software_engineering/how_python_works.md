# How Python Works

Python is an interpreted, dynamically-typed language. When you run `python app.py`, you're invoking the CPython interpreter (the reference implementation written in C), which reads your source code, compiles it to an intermediate bytecode, and then executes that bytecode on a virtual machine.

## The Execution Pipeline

When you run a Python file, CPython performs several steps:

1. Tokenizing — the raw source text is broken into tokens (keywords, identifiers, operators, literals).
1. Parsing — tokens are assembled into an Abstract Syntax Tree (AST) that represents the structure of the program.
1. Compilation — the AST is compiled into bytecode, a lower-level, platform-independent set of instructions for the Python Virtual Machine (PVM).
1. Execution — the PVM (a giant evaluation loop in C) executes the bytecode one instruction at a time.

```
source (.py) -> tokens -> AST -> bytecode (.pyc) -> PVM executes
```

The `.pyc` files are there to catch the bytecode so it doesn't have to do the tokenization and AST parsing every time you import a module. The top-level script you run directly is compiled in-memory and never written to a `.pyc`.

- The cache exists to avoid re-compiling on a future run. `.pyc` files are only pulled in on import, so they speed up imports but not the initial execution of the main script.

### "Line by Line" Execution

People say Python runs "line by line," and that's true in a practical sense: there is no separate ahead-of-time compile step you invoke like in C or Go. But it's more accurate to say Python compiles a whole module to bytecode *first*, then executes that bytecode top to bottom.

This is why a `SyntaxError` anywhere in the file stops the program before *any* code runs — the compile step fails — whereas a `NameError` or `TypeError` only surfaces when execution actually reaches that line. Definitions like `def` and `class` are themselves executable statements: they run top-down to *bind a name* to a function/class object, but the body inside a `def` isn't executed until the function is called.

## Virtual Environments (venv)

A virtual environment is an isolated, self-contained Python installation for a single project, so dependencies for one project don't collide with another (or with the system Python). You create one with:

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
```

### How a venv is Structured

```
.venv/
├── bin/                 # Scripts/ on Windows
│   ├── python           # symlink (or copy) to the base interpreter
│   ├── pip
│   └── activate         # shell script that tweaks $PATH
├── lib/
│   └── python3.12/
│       └── site-packages/   # where pip installs your dependencies
├── include/
└── pyvenv.cfg           # points back to the base Python install
```

- `bin/python` is usually a symlink to the system interpreter — the venv does not copy the entire Python install. `pyvenv.cfg` records the path to that base interpreter and the version.
- Activating the venv simply prepends `.venv/bin` to your `$PATH`, so typing `python` or `pip` resolves to the venv's binaries first. It also sets `$VIRTUAL_ENV`. You don't strictly *need* to activate — running `.venv/bin/python` directly works the same.
- `site-packages/` is the key directory: this is where third-party libraries land. Isolation works because the venv's `python` only looks here (plus the standard library), not at globally installed packages.
- The `.venv/` directory is never committed — it's machine and OS-specific (symlinks, compiled binaries, absolute paths). Instead you commit a `requirements.txt`, `pyproject.toml`, or lockfile and recreate the venv elsewhere.

## .pyc Files and `__pycache__`

When a module is imported, CPython compiles it to bytecode and caches the result as a `.pyc` file inside a `__pycache__/` directory, named like `module.cpython-312.pyc`.

- The `.pyc` is a performance cache: on the next import, if the source hasn't changed, CPython skips tokenizing/parsing/compiling and loads the bytecode directly. It does *not* make execution faster — only startup/import.
- CPython decides whether the cache is stale by comparing the source file's mtime (or a hash, in newer "hash-based" pyc mode) recorded in the `.pyc` header. Change the `.py`, and the `.pyc` is regenerated.
- Note: only *imported* modules get cached. The top-level script you run directly (`python app.py`) is compiled in-memory and never written to a `.pyc`.

### Why `.pyc` Files Aren't Committed

- They're generated artifacts — fully reproducible from source, so committing them adds noise and merge conflicts for zero benefit.
- They're version and platform-specific — a `.pyc` built for `cpython-312` won't be used by `cpython-311`, and a stale or mismatched `.pyc` can cause confusing behavior.
- They can mask source changes if they go stale in odd ways.

Best practice is to add `__pycache__/` and `*.pyc` to `.gitignore`.

## How Imports Work

When you write `import foo`, CPython does roughly:

1. Check `sys.modules` — a cache of already-imported modules. If `foo` is there, use it (modules are only executed *once* per process).
1. Otherwise, search the finders on `sys.meta_path` to locate the module, walking the directories in `sys.path`.
1. Compile + execute the module's code (top to bottom), building a module object.
1. Bind the resulting module object to the name `foo` in the current namespace, and store it in `sys.modules`.

### `sys.path`

`sys.path` is the list of directories Python searches for modules, in order:

1. The directory of the entry script (or the current dir for the REPL).
1. Directories from the `$PYTHONPATH` env var.
1. Standard library locations.
1. The venv's `site-packages/`.

A common source of `ModuleNotFoundError` or accidentally importing the wrong module is `sys.path` ordering — e.g. a local file named `random.py` shadowing the stdlib `random`.

### Packages and `__init__.py`

A package is a directory of modules. Historically it needed an `__init__.py` file to be importable; that file runs when the package is first imported and can expose a public API. Since Python 3.3, *namespace packages* allow packages without `__init__.py`, but explicit `__init__.py` is still the clearest, most common choice.

### Absolute vs Relative Imports

Given this layout:

```
myapp/
├── __init__.py
├── main.py
├── utils/
│   ├── __init__.py
│   ├── helpers.py
│   └── formatting.py
```

Absolute imports spell out the full path from the project/package root:

```python
from myapp.utils import helpers
from myapp.utils.formatting import format_date
```

Relative imports use leading dots to navigate relative to the *current module's* package. One dot = current package, two dots = parent package:

```python
# inside myapp/utils/helpers.py
from . import formatting          # same package (myapp/utils)
from .formatting import format_date
from ..main import run            # go up to myapp, then into main
```

Which to use?

- Prefer absolute imports (this is also PEP 8's recommendation). They're explicit, unambiguous, and don't break if you move a file around within its package.
- Relative imports are concise for tightly-coupled modules within the same package, but they obscure where things come from and only work *inside a package*.

Gotcha: relative imports rely on the module's `__package__`/`__name__`, which is only set correctly when the module is imported *as part of a package*. If you run a file with relative imports directly (`python myapp/utils/helpers.py`), `__name__` becomes `"__main__"`, it has no package context, and you get `ImportError: attempted relative import with no known parent package`. Run it as a module instead: `python -m myapp.utils.helpers`.

## CPython vs Other Implementations

"Python" the language has multiple implementations. CPython is the standard one nearly everyone uses. Others exist for specific needs:

- PyPy — a JIT-compiling interpreter that can be much faster for long-running, compute-heavy code.
- Jython / IronPython — run on the JVM and .NET CLR respectively.

Bytecode (`.pyc`) is a CPython implementation detail — it's not part of the language spec, which is why those files are tied to a specific CPython version.

## The GIL (Global Interpreter Lock)

A frequently-discussed CPython detail: the GIL is a mutex that allows only one thread to execute Python bytecode at a time within a process. This makes the interpreter's memory management simpler and thread-safe, but means CPU-bound multithreading doesn't achieve true parallelism.

- I/O-bound work (network, disk) still benefits from threads, because the GIL is released during blocking I/O.
- CPU-bound work needs `multiprocessing` (separate processes, each with its own GIL) or native extensions to parallelize.
- Recent CPython (3.13+) ships an experimental free-threaded build that can disable the GIL.

## Key Takeaways

- Python compiles source to bytecode, then a virtual machine executes it; "interpreted" doesn't mean there's no compile step.
- A venv is just an isolated `site-packages/` plus a `python` symlink and a tweaked `$PATH` — commit the requirements, not the `.venv/`.
- `.pyc` files are reproducible bytecode caches that speed up imports; gitignore them.
- Imports execute a module once, cache it in `sys.modules`, and are found via `sys.path`. Prefer absolute imports for clarity.

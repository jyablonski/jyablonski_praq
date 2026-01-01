# Python Package Management Files

### setup.py

A `setup.py` file is a Python script that defines how to build and install a package. It was commonly used alongside setup.cfg for configuration. While it got the job done, modern tools like Poetry and uv offer simpler, more robust alternatives.

### pyproject.toml

The modern, standardized way to configure Python projects. It replaces the need for the old files like `setup.py`, `setup.cfg` and centralizes configuration for:

- Package metadata
- Dependency management
- Tool settings (linters, test runners, formatters)
- Build systems (Poetry, Hatch etc)

## Poetry

Poetry is a dependency management and packaging tool for Python, written in Python. It manages dependencies for your project, offers optional groups for things like `test` or `local` sets of packages, and can be used to create and deploy libraries to PyPI.

With Poetry, you don't need to manage a `setup.py` file, you just use `pyproject.toml`.

Uses a `poetry.lock` file for reproducible builds

## uv

uv is a new dependency and packagement management tool written in Rust that aims to be the fastest package manager in Python. It's a multi-purpose, high-performance toolchain that’s designed to unify and replace several commonly used tools.

It offers a handful of incredibly advanced features:

- Fastest Package Manager for Python
- It includes `uvx` which effectively replaces `pipx` to run various scripts or CLIs in isolated environments
- It includes Python Version Management to automatically download and instasll Python versions to use in your projects. This means no more need for 3rd party tools like `pyenv` or `asdf`
- It works with `pyproject.toml` by default

| Functionality | Traditional Tool(s) | `uv` Replacement |
| ------------------------------- | ----------------------------- | ------------------------------------------- |
| Installing packages | `pip` | `uv pip install` |
| Creating virtual environments | `virtualenv`, `venv` | `uv venv` |
| Managing dependencies/lockfiles | `pip-tools`, `poetry install` | `uv pip compile`, `uv pip install` |
| Running CLI apps globally | `pipx` | `uvx` |
| Managing Python versions | `pyenv`, `asdf`, `rye` | `uv` (built-in `python` version management) |

## Wheels

[Article](https://realpython.com/python-wheels/)

Python Wheels are pre-built bundles of packages that you install via Pip. The alternative is for you to download the source installation for a package and then compile it yourself, which takes time. Pip automatically tries finding & using wheels for packages if they're available.

- Different wheels depending on OS such as Windows, Mac, or Linux.
- Some packages don't offer wheels because of how complex they are.
- Wheels are typically smaller in size to download, and faster to install from than a source distribution.
- Installing from source distributions often requires special compilation libraries like gcc or OpenSSL. With wheels, you dont have to worry about this.
- Wheels target specific OS platform's and Python versions.

Python Egg or .egg-info is metadata related to the package to help specify package dependencies and other things. Users aren't affected by it.

# Polars
[Guide](https://pola-rs.github.io/polars-book/user-guide/)

Polars is a Python DataFrame Library built in Rust and uses a Rust implementation of `Arrow` as its foundation for data types.

The goal of Polars:
- Utilize all available cores on your machine
- Optimize your queries + processing tasks to reduce unneeded work + memory allocations
- Handle datasets that are larger than what you can fit in your available RAM
- Strict (static) data types

## Installation
`pip install polars`

`import polars as pl`

Polars has optional dependencies you can specify when installing the package, such as `numpy, fsspec, pandas`, among others.
- `pip install polars[numpy, fsspec]`
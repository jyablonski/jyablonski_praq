# Polars
[Guide](https://pola-rs.github.io/polars-book/user-guide/)
[Article](https://blog.jetbrains.com/dataspell/2023/08/polars-vs-pandas-what-s-the-difference/#:~:text=As%20you%20can%20see%2C%20Polars,out%2Dof%2Dmemory%20errors.)

Polars is a Python DataFrame Library built in Rust and uses a Rust implementation of `Arrow` as its foundation for data types.

The goal of Polars:
- Utilize all available cores on your machine
- Optimize your queries + processing tasks to reduce unneeded work + memory allocations
- Handle datasets that are larger than what you can fit in your available RAM
- Strict (static) data types

## Why Polars over Pandas?
Polars is written in Rust.  Pandas is written on top of Python using NumPy, and while that's written in C it's still hamstrung by inherent problems with how Python handles certain types in memory.  NumPy is great for Integers and Floats, but struggles with others.
- [Article](https://wesmckinney.com/blog/apache-arrow-pandas-internals/)

Polars is based on Apache Arrow to handle types which was created in response to many issues seen with Pandas over the years.  Polars built their own Arrow implementation which allows the library to avoid serializing and deserializing data while performing various transformations on data.  Arrow has sophisticated support for datetime, boolean, binary, and even other complex column types.  It also uses columnar storage so all column values are stored in a continuous block of memory which leads to better parallelism support and faster data retrieval.

Pandas uses eager evaluation which means it executes operations in the order you've written them.  Polars allows for either eager or lazy evaluation, where the query optimizer will take your operations and map out the most efficient way of executing it.

If eager evaluation, the groupby operation would be performed on the whole DataFrame and then filtered.  With lazy evaluation, the DataFrame can be filtered first and groupby would then only run on the specified columns.
``` py
(
df
.groupby(by = "Category").agg(pl.col("Number1").mean())
.filter(pl.col("Category").is_in(["A", "B"]))
)
```

Polars also has a larger API offering, whereas in Pandas you have to use lambdas or the `.apply` method often which don't allow for SIMD operations.  The issue with that is it loops over the rows of a DataFrame, sequentially executing the operation on each one.  Polars offers parallel support for these kinds of operations and takes advantage of SIMD.

Polars has no indexes and instead takes advantage of its columnar data storage & properties for efficient data retreival processing and it enables vectorized operations.

If your data doesn't fit into memory, you can scan your dataset and iteratively apply some transformations to it bit-by-bit and save it to some output file.

## Downsides
No Plotting Libraries available, `matplotlib` and `plotly` don't work with Polars.

Compability with other APIs such as Scikit-Learn, Seaborn, PyTorch isn't really there yet because of how new Polars is.

## Arrow
Apache Arrow is an open-source, columnar, in-memory data representation format and associated libraries for efficient data interchange between different systems and languages. It is designed to address the challenges of sharing and processing large datasets across different platforms and programming languages with minimal overhead.

Key features of Apache Arrow include:

1. **Columnar Memory Layout**: Apache Arrow represents data in a columnar memory layout, where each column is stored separately. This layout is highly efficient for analytical and statistical processing, as it allows for vectorized operations and improved cache locality.

2. **Cross-Language Compatibility**: Apache Arrow provides libraries and tools for working with data in multiple programming languages, including Python, C++, Java, JavaScript, and more. This cross-language compatibility enables seamless data interchange between different systems and components.

3. **Zero-Copy Data Sharing**: Apache Arrow enables zero-copy data sharing between different systems and processes. Instead of copying data when transferring between systems, Arrow allows systems to share memory buffers directly, reducing memory overhead and improving performance.

4. **Columnar Compression**: Apache Arrow supports various compression techniques for reducing the memory footprint of data, including dictionary encoding, run-length encoding, and delta encoding. These compression techniques help optimize memory usage and reduce data transfer times.

5. **Parallel and Distributed Processing**: Apache Arrow is designed for parallel and distributed processing of data. It provides support for efficient data partitioning, distributed computing frameworks (such as Apache Spark and Dask), and parallel execution of operations across multiple cores and nodes.

6. **Integration with Ecosystem Tools**: Apache Arrow integrates with various data processing and analytics tools, including Apache Parquet, Apache Spark, Pandas, TensorFlow, and more. This integration allows users to leverage Arrow's capabilities within their existing data pipelines and workflows.

Overall, Apache Arrow aims to provide a standardized, efficient, and cross-platform data representation format for improving the interoperability, performance, and scalability of data processing and analytics systems.

## Installation
`pip install polars`

`import polars as pl`

Polars has optional dependencies you can specify when installing the package, such as `numpy, fsspec, pandas`, among others.
- `pip install polars[numpy, fsspec]`


# Duck DB
[Article](https://boilingdata.medium.com/lightning-fast-aggregations-by-distributing-duckdb-across-aws-lambda-functions-e4775931ab04)
[Article](https://marclamberti.com/blog/duckdb-getting-started-for-beginners/#:~:text=Under%20the%20hood%2C%20DuckDB%20uses,partitions%2C%20JSON%2C%20and%20more.)
[Article](https://duckdb.org/2024/01/26/multi-database-support-in-duckdb.html)

DuckDB is an embedded Database Management System to handle complex queries on large volumes of data.  It's known for its high performance and compatability with SQL.  It's basically a OLAP focused version of SQLite hosted on 1 machine.

It's goal is to be the fasest way to ingest some data and perform various queries and exploratory data analysis.  There is no concept of a client & server, no networking overhead (which means lightning fast data transfer to & from the database), and is straightforward to install.
- `pip install duckdb`
- `brew install duckdb`
- https://github.com/duckdb/duckdb/releases/download/v0.10.0/duckdb_cli-linux-amd64.zip

DuckDB is highly optimized for analytical query workloads (OLAP).  It's a columnar-oriented database which allows it to only read in specific columns to improve performance.  Supports reading & writing with a variety of File Formats such as CSV, JSON, Parquet etc.

Columnar enables multiple things:
- Data for each column is organized & stored together in memory
- Data can be compressed for improved storage efficiency
- Data only needs to be pulled for the requested columns, improving query performance by reducing the amount of data read from disk
- Column-level statistics can be created for things like row count and min / max values, making any queries that request these statistics very fast
- Can leverage vectorized operations & SIMD operations because the data is stored together unlike row-based formats


## Extensions
DuckDB comes with an Extension system that allows you to install various Extensions to extend the functionality of DuckDB. Extensions are signed with a cryptographic key and DuckDB uses its built-in public keys to verify the integrity of each Extension before loading them in.  All extensions provided by the DuckDB Core team are signed.
- To load your own extensions or ones from 3rd parties, you must enable the `allow_unsigned_extensions` flag.

``` py
import duckdb
con = duckdb.connect(config = {"allow_unsigned_extensions": "true"})
```

There are 3 types of Extensions:
- Built in
- Autoloadable
- Explicitly Loadable

To keep DuckDB lightweight, it only comes with a few fundamental built-in extensions such as JSON & Parquet to allow you to read in those file formats.

Autoloadable extensions will be automatically loaded when you try performing various DuckDB operations, such as below:
``` sql
SELECT *
FROM 'https://raw.githubusercontent.com/duckdb/duckdb-web/main/data/weather.csv';
```

Explicitly Loadable extensions make several changes to the running DuckDB instance so they cannot be autoloadable.  You must install and load them using the following SQL Statements:

``` sql
INSTALL spatial;
LOAD spatial;
```

Some other explicitly loadable extensions include:
- Postgres
- MySQL
- AWS (S3)
- Iceberg
- TPCH
- [Full List](https://duckdb.org/docs/extensions/official_extensions.html)

## Downsides
Runs on 1 machine.  If you have thousands of GBs of data to process, you could run into OOM issues.

Doesn't scale well to share across a team & organization as it only runs either locally or on 1 machine in the Cloud.
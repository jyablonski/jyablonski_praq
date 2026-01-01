# dlt

dlt is a library to extract and load data from various sources such as databases, blob storage (S3), or REST APIs in a standardized format.

- It supports a variety of sources and destinations
- It infers schemas and data types, normalizes the data, and handles nested structures
- Also supports advanced maintenance features like incremental loads, schema evolution, and data contracts

## Installation

```sh
uv add dlt
# Or with specific destination support
uv add "dlt[duckdb]"
uv add "dlt[postgres]"
```

## Quick Start

For REST APIs, it has functionality to include pagination options, authentication handling, and destination to store the data.

```sh
dlt init rest_api duckdb
python rest_api_pipeline.py
dlt pipeline rest_api_pokemon show
```

## Basic REST API Example

```python
import dlt
from dlt.sources.rest_api import rest_api_source

source = rest_api_source({
    "client": {
        "base_url": "https://api.example.com/",
    },
    "resources": [
        {
            "name": "users",
            "endpoint": {
                "path": "users",
            },
        },
    ],
})

pipeline = dlt.pipeline(
    pipeline_name="my_pipeline",
    destination="duckdb",
    dataset_name="my_data",
)

load_info = pipeline.run(source)
```

## Pagination Support

dlt supports multiple pagination strategies:

### Page Number Pagination

```python
"paginator": {
    "type": "page_number",
    "page_param": "page",
    "base_page": 1,        # Start page (default: 0)
    "maximum_page": 5,     # Stop after N pages
}
```

### Offset-Limit Pagination

```python
"paginator": {
    "type": "offset",
    "limit": 100,
    "offset_param": "offset",
    "limit_param": "limit",
}
```

### Cursor Pagination

```python
"paginator": {
    "type": "json_link",
    "next_url_path": "pagination.next",  # JSONPath to next URL
}
```

## In-Memory DuckDB

For testing or temporary analysis, use in-memory DuckDB:

```python
import duckdb
import dlt

db = duckdb.connect(":memory:")

pipeline = dlt.pipeline(
    pipeline_name="my_pipeline",
    destination=dlt.destinations.duckdb(db),
    dataset_name="my_data",
)

pipeline.run(source)

# Query directly with the same connection
result = db.sql("SELECT * FROM my_data.table_name").fetchdf()
```

Note: In-memory databases are destroyed when the script exits.

## Authentication

dlt supports various auth methods:

```python
"client": {
    "base_url": "https://api.example.com/",
    "auth": {
        # Bearer token
        "token": dlt.secrets["api_token"],

        # Or API key in header
        "type": "api_key",
        "api_key": dlt.secrets["api_key"],
        "name": "X-API-Key",
        "location": "header",
    },
}
```

## Querying Data

After loading, query using pipeline methods:

```python
# Method 1: SQL client (read/write)
with pipeline.sql_client() as client:
    with client.execute_query("SELECT * FROM my_table") as cursor:
        rows = cursor.fetchall()

# Method 2: Dataset (read-only, recommended)
dataset = pipeline.dataset()
table = dataset.my_table
df = table.df()  # Returns pandas DataFrame
```

## CLI Commands

```sh
# Show pipeline info
dlt pipeline <pipeline_name> show

# List tables in destination
dlt pipeline <pipeline_name> info

# Drop pipeline data
dlt pipeline <pipeline_name> drop

# Sync pipeline state
dlt pipeline <pipeline_name> sync
```

## Metadata Tables

dlt automatically creates internal tables with `_dlt_` prefix:

- `_dlt_loads` - Tracks pipeline runs
- `_dlt_pipeline_state` - Stores pipeline state
- `_dlt_version` - Schema version tracking

## When to Use dlt

Good for:

- Production data pipelines with multiple sources
- Need for incremental loading and state management
- Large-scale data (millions of records)
- Schema evolution requirements
- Loading to multiple destinations (BigQuery, Snowflake, etc.)

Overkill for:

- Simple one-off API calls (\<1000 records)
- Ad-hoc data exploration
- When you need full control over pagination logic
- Performance-critical applications (adds overhead)

## Simple Alternative

For basic REST API -> DuckDB workflows:

```python
import requests
import duckdb

# Fetch data
data = requests.get("https://api.example.com/data").json()

# Load into DuckDB
db = duckdb.connect(":memory:")
db.execute("CREATE TABLE my_table AS SELECT * FROM data")
```

This is simpler, faster, and has fewer dependencies for straightforward use cases.

## Dependency Notes

dlt has ~25+ dependencies including:

- Heavy: GitPython, sqlglot, fsspec (~50-100MB total)
- Useful: orjson (fast JSON), requests, tenacity (retries)
- Questionable: pendulum (datetime alternative), humanize

For simple pipelines, these dependencies may be overkill compared to using `requests` + `duckdb` directly.

## Resources

- [Official Docs](https://dlthub.com/docs/)
- [DuckDB Destination](https://dlthub.com/docs/dlt-ecosystem/destinations/duckdb)

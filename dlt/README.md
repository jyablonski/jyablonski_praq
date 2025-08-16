# dlt

dlt is a library to etract and load data from various sources such as databases, blob storage (S3), or REST APIs.

- It supports a variety of sources and destinations
- It infers schemas and data types, normalizes the data, and handles nested structures
- Also supports advanced maintenance features like incremental loads, schema evolution, and data contracts

```sh
pip install dlt
uv add dlt
```

For REST APIs, it has functionality to include pagination options, authentication handling, and destination to store the data.

``` sh
dlt init rest_api duckdb
python rest_api_pipeline.py
dlt pipeline rest_api_pokemon show
```
import os

import boto3
import polars as pl

# https://github.com/apache/iceberg-python
# poetry add polars pyiceberg
session = boto3.Session()

table_path = "s3://jyablonski2-iceberg/prod/nba_elt_iceberg.db/reddit_comment_data/metadata/00000-88d79099-3157-4a0c-bfc0-ef1a377bb295.metadata.json"
storage_options = {
    "s3.region": "us-east-1",
    "s3.access-key-id": session.get_credentials().access_key,
    "s3.secret-access-key": session.get_credentials().secret_key,
}
pl.scan_iceberg(table_path, storage_options=storage_options).collect()

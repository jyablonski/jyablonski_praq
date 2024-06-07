from datetime import datetime, timedelta

import boto3
import duckdb
import pandas as pd

from utils import setup_iceberg, setup_aws_creds

date = (datetime.now() - timedelta(days=1)).date()

# reads from ~/.aws/credentials by default
session = boto3.Session()
s3_key = session.get_credentials().access_key
s3_secret = session.get_credentials().secret_key

# in memory db
con = duckdb.connect(database=":memory:", read_only=False)

setup_iceberg(conn=con)
setup_aws_creds(conn=con, access_key=s3_key, secret_key=s3_secret)

# this doesnt work, some bug with how iceberg tables created w/ spark won't work here or something
df = con.execute(
    """\
SELECT count(*)
FROM iceberg_scan('s3://jyablonski2-iceberg/prod/nba_elt_iceberg.db/pbp_data/data');"""
).fetchdf()

# it keeps trying to look for an s3 file in `s3a://` which is some spark shit
df = con.execute(
    """\
SELECT *
FROM iceberg_scan('s3://jyablonski2-iceberg/prod/nba_elt_iceberg.db/reddit_comment_data/metadata/00000-88d79099-3157-4a0c-bfc0-ef1a377bb295.metadata.json');"""
).fetchdf()

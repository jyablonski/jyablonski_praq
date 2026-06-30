from datetime import datetime, timedelta
import os

import boto3
import duckdb
import pandas as pd

from utils import setup_aws_creds, setup_postgres, setup_tpch

date = (datetime.now() - timedelta(days=1)).date()

# reads from ~/.aws/credentials by default
session = boto3.Session()
s3_key = session.get_credentials().access_key
s3_secret = session.get_credentials().secret_key

# persistent db
con = duckdb.connect(database=":memory:", read_only=False)

# setup data sources to pull data from s3, postgres, or tpch extension
setup_aws_creds(conn=con, access_key=s3_key, secret_key=s3_secret)
setup_postgres(
    conn=con,
    username=os.environ.get("RDS_USER"),
    password=os.environ.get("RDS_PW"),
    host=os.environ.get("IP"),
    database="jacob_db",
)
setup_tpch(conn=con)

# pull data from s3 into duckdb
df = con.execute(
    f"SELECT * FROM parquet_scan('s3://jyablonski-nba-elt-prod/boxscores/validated/year=2023/month=12/boxscores-2023-12-31.parquet');"
).fetch_df()

# pull data from s3 into duckdb
df = con.execute(f"SELECT * FROM jacob_db.nba_prod.feature_flags;").fetch_df()


# pull data from s3 into duckdb
df = con.execute(f"SELECT * FROM main.customer limit 10;").fetch_df()

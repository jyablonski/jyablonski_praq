from datetime import datetime

import boto3
import duckdb
import pandas as pd

# reads from ~/.aws/credentials by default
session = boto3.Session()
s3_key = session.get_credentials().access_key
s3_secret = session.get_credentials().secret_key

con = duckdb.connect(database=":memory:", read_only=False)

# httpfs is used to connect directly w/ s3
con.execute(
    f"""
    INSTALL httpfs;
    LOAD httpfs;
    SET s3_region='us-east-1';
    SET s3_access_key_id='{s3_key}';
    SET s3_secret_access_key='{s3_secret}';
"""
)

df = con.execute(
    f"SELECT * FROM parquet_scan('s3://nba-elt-prod/boxscores/validated/year=2023/month=03/boxscores-2023-03-21.parquet');"
).fetchdf()


def df_to_duckdb(conn: duckdb.DuckDBPyConnection, df: pd.DataFrame, table: str):
    # register the df in the database so it can be queried
    try:
        # doesn't create the table, but creates a pointer for the database to reference the existing dataframe in memory.
        conn.register("df", df)

        print(f"Creating table {table} in duckdb")
        query = f"create or replace table {table} as select * from df"
        conn.execute(f"{query}")

        print(f"Finished creating table")
        pass
    except BaseException as e:
        print(f"Error occurred while creating table {table} with df {df}, {e}")

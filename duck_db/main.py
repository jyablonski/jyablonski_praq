from datetime import datetime, timedelta

import boto3
import duckdb
import pandas as pd

date = (datetime.now() - timedelta(days=1)).date()

# reads from ~/.aws/credentials by default
session = boto3.Session()
s3_key = session.get_credentials().access_key
s3_secret = session.get_credentials().secret_key

# in memory db
con = duckdb.connect(database=":memory:", read_only=False)

# persistent db
con = duckdb.connect(database="nba_duck_db", read_only=False)
schema = "nba_prod"

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
    f"SELECT * FROM parquet_scan('s3://jyablonski-nba-elt-prod/boxscores/validated/year=2023/month=12/boxscores-2023-12-31.parquet');"
).fetchdf()

con.execute(f"drop schema if exists {schema} cascade;")
con.execute(f"create schema {schema};")


def create_duckdb_table(
    conn: duckdb.DuckDBPyConnection,
    schema: str,
    table: str,
    df: pd.DataFrame,
):
    # register the df in the database so it can be queried
    try:
        # doesn't create the table, but creates a pointer for the database to reference the existing dataframe in memory.
        conn.register("df", df)

        print(f"Creating table {schema}.{table} in duckdb")
        query = f"create or replace table {schema}.{table} as select * from df"
        conn.execute(f"{query}")

        print(f"Finished creating table")
        pass
    except BaseException as e:
        print(f"Error occurred while creating table {table} with df {df}, {e}")


create_duckdb_table(
    conn=con,
    schema=schema,
    table="boxscores",
    df=df,
)

create_duckdb_table(
    conn=con,
    schema=schema,
    table="boxscores2",
    df=df,
)

con.execute(f"delete from nba_prod.boxscores2 where team = 'GSW';")

missing_query = f"""
delete from nba_prod.boxscores2 where team = 'GSW';

with new_table as (
	select *
	from nba_prod.boxscores
),

old_table as (
	select *
	from nba_prod.boxscores2
)

-- find the missing records in the new_table that aren't in the old_table
select *
from new_table
except
select *
from old_table;"""

df = con.execute(missing_query).fetchdf()

con.close()

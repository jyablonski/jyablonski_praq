from datetime import datetime, timedelta
import os
import uuid
from typing import List

import awswrangler as wr
import requests
from bs4 import BeautifulSoup
import pandas as pd
import psycopg2
from sqlalchemy import exc, create_engine

# took like a minute and a half as of 2023-02-04
date = datetime.now().date()
print(f"Starting Export at {datetime.now()}")

def write_to_sql(con, table_name: str, df: pd.DataFrame, table_type: str) -> None:
    """
    SQL Table function to write a pandas data frame in aws_dfname_source format
    Args:
        con (SQL Connection): The connection to the SQL DB.
        table_name (str): The Table name to write to SQL as.
        df (DataFrame): The Pandas DataFrame to store in SQL
        table_type (str): Whether the table should replace or append to an existing SQL Table under that name
    Returns:
        Writes the Pandas DataFrame to a Table in Snowflake in the {nba_source} Schema we connected to.
    """
    try:
        if len(df) == 0:
            print(f"{table_name} is empty, not writing to SQL")
        else:
            df.to_sql(
                con=con,
                name=f"aws_{table_name}_source",
                index=False,
                if_exists=table_type,
            )
            print(
                f"Writing {len(df)} {table_name} rows to aws_{table_name}_source to SQL"
            )
    except BaseException as error:
        print(f"SQL Write Script Failed, {error}")

def sql_connection(rds_schema: str):
    """
    SQL Connection function connecting to my postgres db with schema = nba_source where initial data in ELT lands.
    Args:
        rds_schema (str): The Schema in the DB to connect to.
    Returns:
        SQL Connection variable to a specified schema in my PostgreSQL DB
    """
    RDS_USER = os.environ.get("RDS_USER")
    RDS_PW = os.environ.get("RDS_PW")
    RDS_IP = os.environ.get("IP")
    RDS_DB = os.environ.get("RDS_DB")
    try:
        connection = create_engine(
            f"postgresql+psycopg2://{RDS_USER}:{RDS_PW}@{RDS_IP}:5432/{RDS_DB}",
            connect_args={"options": f"-csearch_path={rds_schema}"},
            # defining schema to connect to
            echo=False,
        )
        print(f"SQL Connection to schema: {rds_schema} Successful")
        return connection
    except exc.SQLAlchemyError as e:
        return e

conn = sql_connection(rds_schema='nba_source')

with conn.connect() as connection:
    df = pd.read_sql("SELECT * FROM information_schema.tables where table_schema = 'nba_source';", connection)

    tables = df["table_name"]

    for i in tables:
        table_name = f"tables/{i}-{date}.parquet"
        df = pd.read_sql(f"select * from {i};", connection)
        df.to_parquet(table_name)
        print(f"Querying {i}")
        print(f"Storing {i} to {table_name}")

print(f"Finished nba_source at {datetime.now()}, starting ml_models")

conn = sql_connection(rds_schema='ml_models')
with conn.connect() as connection:
    df = pd.read_sql("SELECT * FROM information_schema.tables where table_name = 'tonights_games_ml' and table_schema = 'ml_models';", connection)

    tables = df["table_name"]

    for i in tables:
        table_name = f"tables/{i}-{date}.parquet"
        df = pd.read_sql(f"select * from {i};", connection)
        df.to_parquet(table_name)
        print(f"Querying {i}")
        print(f"Storing {i} to {table_name}")

print(f"Finished at {datetime.now()}")
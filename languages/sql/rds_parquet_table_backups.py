from datetime import datetime
import os

import pandas as pd
from jyablonski_common_modules.sql import sql_connection, write_to_sql

# took like a minute and a half as of 2023-02-04
date = datetime.now().date()
print(f"Starting Export at {datetime.now()}")


engine = sql_connection(
    database=os.environ.get("RDS_DB"),
    schema="nba_source",
    user=os.environ.get("RDS_USER"),
    pw=os.environ.get("RDS_PW"),
    host=os.environ.get("IP"),
)


with engine.connect() as connection:
    df = pd.read_sql(
        "SELECT * FROM information_schema.tables where table_schema = 'nba_source';",
        connection,
    )

    tables = df["table_name"]

    for i in tables:
        table_name = f"tables/{i}-{date}.parquet"
        df = pd.read_sql(f"select * from {i};", connection)
        df.to_parquet(table_name)
        print(f"Querying {i}")
        print(f"Storing {i} to {table_name}")

print(f"Finished nba_source at {datetime.now()}, starting ml_models")

conn = sql_connection(rds_schema="ml_models")
with conn.connect() as connection:
    df = pd.read_sql(
        "SELECT * FROM information_schema.tables where table_name = 'tonights_games_ml' and table_schema = 'ml_models';",
        connection,
    )

    tables = df["table_name"]

    for i in tables:
        table_name = f"tables/{i}-{date}.parquet"
        df = pd.read_sql(f"select * from {i};", connection)
        df.to_parquet(table_name)
        print(f"Querying {i}")
        print(f"Storing {i} to {table_name}")

print(f"Finished at {datetime.now()}")

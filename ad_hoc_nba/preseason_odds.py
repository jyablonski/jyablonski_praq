import os

import pandas as pd
from sqlalchemy.engine import create_engine, Engine


url = "https://www.basketball-reference.com/leagues/NBA_2025_preseason_odds.html"
df = pd.read_html(url)[0]
df

df = df.rename(columns={"Team": "team", "Odds": "odds"})


def sql_connection(
    database: str,
    schema: str,
    user: str,
    pw: str,
    host: str,
    port: int,
) -> Engine:
    """
    SQL Engine function to define the SQL Driver + connection variables needed to connect to the DB.
    This doesn't actually make the connection, use conn.connect() in a context manager to create 1 re-usable connection

    Args:
        database(str): The Database to connect to

        schema (str): The Schema to connect to

        user (str): The User for the connection

        pw (str): The Password for the connection

        host (str): The Host Endpoint of the Database

        port (int): Database Port

    Returns:
        SQL Engine variable to a specified schema in my PostgreSQL DB
    """
    connection = create_engine(
        f"postgresql+psycopg2://{user}:{pw}@{host}:{port}/{database}",
        # pool_size=0,
        # max_overflow=20,
        connect_args={
            "options": f"-csearch_path={schema}",
        },
        # defining schema to connect to
        echo=False,
    )
    print(f"SQL Engine for schema: {schema} Successful")
    return connection


engine = sql_connection(
    database=os.environ.get("RDS_DB"),
    schema="nba_source",
    user=os.environ.get("RDS_USER"),
    pw=os.environ.get("RDS_PW"),
    host=os.environ.get("IP"),
    port=17841,
)

df.to_sql("aws_preseason_odds_source", con=engine, if_exists="append", index=False)

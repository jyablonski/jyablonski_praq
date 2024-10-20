from datetime import datetime
import os

from sqlalchemy.engine import create_engine, Engine
import pandas as pd


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


file_date = "2024-08-08"

engine = sql_connection(
    database=os.environ.get("RDS_DB"),
    schema="nba_source",
    user=os.environ.get("RDS_USER"),
    pw=os.environ.get("RDS_PW"),
    host=os.environ.get("IP"),
    port=17841,
)

ml_tables = [
    "tonights_games_ml",
]

nba_prod_tables = [
    "feature_flags",
    "feature_flags_audit",
    "incidents",
    "incidents_audit",
    "rest_api_users",
    "rest_api_users_audit",
    "shiny_feature_flags",
    "user_predictions",
    "user_predictions_audit",
]

nba_source_tables = [
    "aws_adv_stats_source",
    "aws_boxscores_source",
    "aws_contracts_source",
    "aws_injury_data_source",
    "aws_odds_source",
    "aws_opp_stats_source",
    "aws_pbp_data_source",
    "aws_player_attributes_source",
    "aws_preseason_odds_source",
    "aws_reddit_comment_data_source",
    "aws_reddit_data_source",
    "aws_schedule_source",
    "aws_shooting_stats_source",
    "aws_stats_source",
    "aws_team_attributes_source",
    "aws_transactions_source",
    "aws_twitter_data_source",
    "aws_twitter_tweepy_data_source",
    "aws_twitter_tweets_source",
    "inactive_dates",
    "staging_seed_player_attributes",
    "staging_seed_team_attributes",
    "staging_seed_top_players",
]

public_tables = [
    "rest_api_users",
    "user_predictions",
]


def load_sql_table(connection, table: str, schema: str, date: str):
    df = pd.read_parquet(f"sql/tables/{schema}/{table}-{date}.parquet")

    df.to_sql(
        name=table, con=connection, schema=schema, if_exists="replace", index=False
    )
    print(f"Reading {table}, writing to {schema}.{table}")
    pass


with engine.connect() as connection:
    # for table in ml_tables:
    #     load_sql_table(
    #         connection=connection, table=table, schema="ml", date=file_date
    #     )

    for table in nba_prod_tables:
        load_sql_table(
            connection=connection, table=table, schema="marts", date=file_date
        )

    for table in nba_source_tables:
        load_sql_table(
            connection=connection, table=table, schema="nba_source", date=file_date
        )

    for table in public_tables:
        load_sql_table(
            connection=connection, table=table, schema="public", date=file_date
        )

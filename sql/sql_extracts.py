from datetime import datetime
import os

from jyablonski_common_modules.sql import sql_connection, write_to_sql
import pandas as pd

engine = sql_connection(
    database=os.environ.get("RDS_DB"),
    schema="nba_source",
    user=os.environ.get("RDS_USER"),
    pw=os.environ.get("RDS_PW"),
    host=os.environ.get("IP"),
)

ml_models_tables = [
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


def store_sql_table(connection, table: str, schema: str):
    todays_date = datetime.now().date()

    try:
        df = pd.read_sql(f"select * from {schema}.{table};", con=connection)
        print(f"Queried {len(df)} Records from {schema}.{table}")

        df.to_parquet(f"sql/tables/{schema}/{table}-{todays_date}.parquet")
        print(
            f"Wrote {schema}.{table} to tables/{schema}/{table}-{todays_date}.parquet"
        )

        pass
    except BaseException as e:
        print(f"Error Occurred while Reading {schema}.{table}, {e}")
        raise e


with engine.connect() as connection:
    for table in ml_models_tables:
        store_sql_table(connection=connection, table=table, schema="ml_models")

    for table in nba_prod_tables:
        store_sql_table(connection=connection, table=table, schema="nba_prod")

    for table in nba_source_tables:
        store_sql_table(connection=connection, table=table, schema="nba_source")

    for table in public_tables:
        store_sql_table(connection=connection, table=table, schema="nba_prod")

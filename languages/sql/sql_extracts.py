from datetime import datetime
import os

from jyablonski_common_modules.sql import create_sql_engine
import pandas as pd

engine = create_sql_engine(
    database=os.environ.get("RDS_DB"),
    schema="nba_source",
    user=os.environ.get("RDS_USER"),
    password=os.environ.get("RDS_PW"),
    host=os.environ.get("IP"),
    port=17841,
)

ml_models_tables = ["ml_game_predictions"]

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
    "player_attributes",
    "play_in_details",
    "boxscores",
    "internal_player_attributes",
    "reddit_posts",
    "reddit_comments",
    "bbref_player_contracts",
    "bbref_league_transactions",
    "bbref_player_stats_snapshot",
    "bbref_team_opponent_shooting_stats",
    "bbref_team_preseason_odds",
    "bbref_player_pbp",
    "internal_league_inactive_dates",
    "twitter_tweets",
    "twitter_tweepy_legacy",
    "bbref_player_boxscores",
    "bbref_team_adv_stats_snapshot",
    "aws_twitter_tweets_source",
    "internal_team_top_players",
    "internal_team_attributes",
    "draftkings_game_odds",
    "bbref_player_shooting_stats",
    "bbref_player_injuries",
    "bbref_league_schedule",
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
    year = todays_date.year
    output_dir = f"tables/{year}/{schema}"
    output_path = f"{output_dir}/{table}-{todays_date}.parquet"

    try:
        df = pd.read_sql(f"SELECT * FROM {schema}.{table};", con=connection)
        print(f"Queried {len(df)} records from {schema}.{table}")

        # Create directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        df.to_parquet(output_path)
        print(f"Wrote {schema}.{table} to {output_path}")

    except BaseException as e:
        print(f"Error occurred while reading {schema}.{table}: {e}")
        raise


with engine.connect() as connection:
    for table in ml_models_tables:
        store_sql_table(connection=connection, table=table, schema="ml")

    for table in nba_prod_tables:
        store_sql_table(connection=connection, table=table, schema="marts")

    for table in nba_source_tables:
        store_sql_table(connection=connection, table=table, schema="nba_source")

    for table in public_tables:
        store_sql_table(connection=connection, table=table, schema="marts")

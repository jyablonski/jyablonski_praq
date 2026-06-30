import os

from jyablonski_common_modules.sql import create_sql_engine
from sqlalchemy import text

TABLES_TO_TRUNCATE = [
    "boxscores",
    "reddit_posts",
    "reddit_comments",
    "bbref_player_contracts",
    "bbref_league_transactions",
    "bbref_player_stats_snapshot",
    "bbref_team_opponent_shooting_stats",
    "bbref_team_preseason_odds",
    "bbref_player_pbp",
    "twitter_tweets",
    "twitter_tweepy_legacy",
    "bbref_player_boxscores",
    "bbref_team_adv_stats_snapshot",
    "aws_twitter_tweets_source",
    "draftkings_game_odds",
    "bbref_player_shooting_stats",
    "bbref_player_injuries",
    "bbref_league_schedule",
]

engine = create_sql_engine(
    database=os.environ.get("RDS_DB"),
    schema="nba_source",
    user=os.environ.get("RDS_USER"),
    password=os.environ.get("RDS_PW"),
    host=os.environ.get("IP"),
    port=17841,
)


def truncate_tables():
    """Truncate all tables in the TABLES_TO_TRUNCATE list."""
    with engine.connect() as conn:
        for table in TABLES_TO_TRUNCATE:
            try:
                print(f"Truncating nba_source.{table}...")
                conn.execute(text(f"TRUNCATE TABLE nba_source.{table} CASCADE;"))
                conn.commit()
                print(f"Successfully truncated nba_source.{table}")
            except Exception as e:
                print(f"Error truncating nba_source.{table}: {e}")
                conn.rollback()

    print(f"\nCompleted truncation of {len(TABLES_TO_TRUNCATE)} tables.")


if __name__ == "__main__":
    truncate_tables()

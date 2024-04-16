import os
import pandas as pd
from nba_api.stats.static import players

from jyablonski_common_modules.sql import sql_connection


def clean_player_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Function to remove suffixes from player names for joining downstream.
    Assumes the column name is ['player']

    Args:
        df (DataFrame): The DataFrame you wish to alter

    Returns:
        df with transformed player names
    """
    try:
        df["player"] = df["player"].str.replace(" Jr.", "", regex=True)
        df["player"] = df["player"].str.replace(" Sr.", "", regex=True)
        df["player"] = df["player"].str.replace(
            " III", "", regex=True
        )  # III HAS TO GO FIRST, OVER II
        df["player"] = df["player"].str.replace(
            " II", "", regex=True
        )  # Robert Williams III -> Robert WilliamsI
        df["player"] = df["player"].str.replace(" IV", "", regex=True)
        return df
    except BaseException as e:
        raise e


# Create an instance of the NBAStats class
nba_players = players.get_players()

df = pd.DataFrame(nba_players).query(f"is_active == True")
df["headshot"] = df["id"].apply(
    lambda x: f"https://ak-static.cms.nba.com/wp-content/uploads/headshots/nba/latest/260x190/{x}.png"
)

df = df.rename(columns={"full_name": "player", "id": "player_id"})
df = df[["player", "headshot"]]
df = clean_player_names(df)
df["yrs_exp"] = 0
df["is_rookie"] = False


engine = sql_connection(
    database=os.environ.get("RDS_DB"),
    schema="nba_source",
    user=os.environ.get("RDS_USER"),
    pw=os.environ.get("RDS_PW"),
    host=os.environ.get("IP"),
)

df.to_sql("aws_player_attributes_source", con=engine, if_exists="append", index=False)

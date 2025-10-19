import os

import pandas as pd
from jyablonski_common_modules.sql import create_sql_engine

url = "https://www.basketball-reference.com/leagues/NBA_2026_preseason_odds.html"
df = pd.read_html(url)[0]

df = df.rename(columns={"Team": "team", "Odds": "odds"})


engine = create_sql_engine(
    database=os.environ.get("RDS_DB"),
    schema="nba_source",
    user=os.environ.get("RDS_USER"),
    password=os.environ.get("RDS_PW"),
    host=os.environ.get("IP"),
    port=17841,
)

df.to_sql("bbref_team_preseason_odds", con=engine, if_exists="append", index=False)

from datetime import datetime
import os

import pandas as pd
import requests

# pandas equivalent of https://github.com/jyablonski/pyspark_prac/blob/master/local_files/rest_api_scraping.py
api = f"https://api.jyablonski.dev/game_types"

response = requests.get(api)

df = pd.DataFrame(response.json())

# new agg column grouping by 1 column
df["games_avg"] = df.groupby(["type"])["n"].transform("sum")

# new agg column grouping by 2 columns
df["games_avg_2"] = df.groupby(["type", "game_type"])["n"].transform("sum")

# create new column

df_filtered = df.query("games_avg_2 == 24")

df["fake_col"] = df["n"] + 35

# only select a few columns
df_selected = df[["explanation", "fake_col"]]

# create new agg df - with multiple aggs from same `.agg` function
df_aggs = (
    df.groupby(["type", "game_type"])
    .agg({"n": "sum", "n": "avg", "n": "min", "n": "max"})
    .reset_index()
)

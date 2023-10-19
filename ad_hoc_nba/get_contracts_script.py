import os

import pandas as pd
from jyablonski_common_modules.sql import sql_connection


def get_contracts():
    df = pd.read_html(
        "https://www.basketball-reference.com/contracts/players.html", header=1
    )[0]
    df = df.rename(columns={df.columns[2]: "team", df.columns[3]: "season_salary"})
    df = df[["Player", "team", "season_salary"]]
    df.columns = df.columns.str.lower()
    df = df.drop_duplicates()
    df = df.query(
        'season_salary != "Salary" & season_salary != "2022-23" & player != "Player"'
    ).reset_index()
    df["season_salary"] = df["season_salary"].str.replace("$", "").str.replace(",", "")
    df["season_salary"].fillna(3000000, inplace=True)
    df["team"] = df["team"].str.replace("PHO", "PHX")
    df["team"] = df["team"].str.replace("CHO", "CHA")
    df["team"] = df["team"].str.replace("BRK", "BKN")
    df["season_salary"] = pd.to_numeric(df["season_salary"])
    df["player"] = (
        df["player"]
        .str.normalize("NFKD")
        .str.encode("ascii", errors="ignore")
        .str.decode("utf-8")
    )
    df["player"] = df["player"].str.replace(" IV", "", regex=True)
    df["player"] = df["player"].str.replace(" III", "", regex=True)
    df["player"] = df["player"].str.replace(" II", "", regex=True)
    df["player"] = df["player"].str.replace(" Jr.", "", regex=True)
    df["player"] = df["player"].str.replace(" Sr.", "", regex=True)
    df = df.drop(["index"], axis=1)
    df = df.reset_index(drop=True)
    return df


contracts = get_contracts()

engine = sql_connection(
    database=os.environ.get("RDS_DB"),
    schema="nba_source",
    user=os.environ.get("RDS_USER"),
    pw=os.environ.get("RDS_PW"),
    host=os.environ.get("IP"),
)

contracts.to_sql("aws_contracts_source", con=engine, if_exists="append", index=False)

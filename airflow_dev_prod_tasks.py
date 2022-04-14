import os
from datetime import datetime, timezone, timedelta

import numpy as np
import pandas as pd

# from urllib.error import URLError, HTTPError


class RunTypeError(BaseException):
    pass


def get_contracts(run_type: str):
    if run_type == "dev":
        records_pct = 0.05
    elif run_type == "prod":
        records_pct = 1
    else:
        raise RunTypeError(
            f"Please Select either dev or prod for run_type; you chose {run_type}"
        )
    df = pd.read_html(
        "https://www.basketball-reference.com/contracts/players.html", header=1
    )[0]
    df = df.rename(columns={df.columns[2]: "team", df.columns[3]: "season_salary"})
    df = df[["Player", "team", "season_salary"]]
    df.columns = df.columns.str.lower()
    df = df.drop_duplicates()
    df = df.query(
        'season_salary != "Salary" & season_salary != "2021-22"'
    ).reset_index()
    df["season_salary"] = df["season_salary"].str.replace(",", "", regex=True)
    df["season_salary"] = df["season_salary"].str.replace("$", "", regex=True)
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
    df["player"] = df["player"].str.replace(" Jr.", "", regex=True)
    df["player"] = df["player"].str.replace(" Sr.", "", regex=True)
    df["player"] = df["player"].str.replace(" II", "", regex=True)
    df["player"] = df["player"].str.replace(" III", "", regex=True)
    df["player"] = df["player"].str.replace(" IV", "", regex=True)
    df = df.reset_index(drop=True)
    df = df.sample(frac=records_pct)
    return df


contracts = get_contracts("prod")  # this will return 100% of records
contracts = get_contracts(
    "dev"
)  # this will return 0.5% of records to test integration.
contracts = get_contracts("test_fail")  # test that the exception works.

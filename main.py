import os
import logging
from urllib.request import urlopen
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import praw
from bs4 import BeautifulSoup
from sqlalchemy import exc, create_engine
import boto3
from botocore.exceptions import ClientError

print("Loading Python ELT Script Version: 0.1.33")

logging.basicConfig(
    filename="example.log",
    level=logging.DEBUG,
    format="%(asctime)s %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
)

print("Starting Logging Function")
logging.info("Starting Logging Function")

print("LOADED FUNCTIONS")
logging.info("LOADED FUNCTIONS")

today = datetime.now().date()
todaytime = datetime.now()
yesterday = today - timedelta(1)
day = (datetime.now() - timedelta(1)).day
month = (datetime.now() - timedelta(1)).month
year = (datetime.now() - timedelta(1)).year
season_type = "Regular Season"



def get_player_stats_data():
    """
    Web Scrape function w/ BS4 that grabs aggregate season stats
    Args:
        None
    Returns:
        Pandas DataFrame of Player Aggregate Season stats
    """
    try:
        year_stats = 2022
        url = "https://www.basketball-reference.com/leagues/NBA_{}_per_game.html".format(
            year_stats
        )
        html = urlopen(url)
        soup = BeautifulSoup(html, "html.parser")

        headers = [th.getText() for th in soup.findAll("tr", limit=2)[0].findAll("th")]
        headers = headers[1:]

        rows = soup.findAll("tr")[1:]
        player_stats = [
            [td.getText() for td in rows[i].findAll("td")] for i in range(len(rows))
        ]

        stats = pd.DataFrame(player_stats, columns=headers)
        logging.info(
            f"General Stats Extraction Function Successful, retrieving {len(stats)} updated rows"
        )
        print(
            f"General Stats Extraction Function Successful, retrieving {len(stats)} updated rows"
        )
        return stats
    except BaseException as error:
        logging.info(f"General Stats Extraction Function Failed, {error}")
        print(f"General Stats Extraction Function Failed, {error}")
        df = []
        return df

def get_player_stats_transform(df):
    """
    Web Scrape function w/ BS4 that grabs aggregate season stats
    Args:
        None
    Returns:
        Pandas DataFrame of Player Aggregate Season stats
    """
    stats = df
    try:
        stats["PTS"] = pd.to_numeric(stats["PTS"])

        stats = stats.query("Player == Player").reset_index()
        stats["Player"] = (
            stats["Player"]
            .str.normalize("NFKD")
            .str.encode("ascii", errors="ignore")
            .str.decode("utf-8")
        )
        stats.columns = stats.columns.str.lower()
        stats["scrape_date"] = datetime.now().date()
        stats = stats.drop("index", axis=1)
        logging.info(
            f"General Stats Function Successful, retrieving {len(stats)} updated rows"
        )
        print(
            f"General Stats Function Successful, retrieving {len(stats)} updated rows"
        )
        return stats
    except BaseException as error:
        logging.info(f"General Stats Transformation Function Failed, {error}")
        print(f"General Stats Transformation Function Failed, {error}")
        df = []
        return df

# stats_data = get_player_stats_data()

# stats_data_transformed = get_player_stats_transform(stats_data)
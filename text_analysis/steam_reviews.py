from datetime import datetime
import os
from typing import List

from bs4 import BeautifulSoup
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import numpy as np
import pandas as pd
import requests

# https://andrew-muller.medium.com/scraping-steam-user-reviews-9a43f9e38c92
# to get more than 100 reviews, you have to use the cursor.  you basically make a loop where you use the cursor to identify where you last left off,
#  and you can make another request for 100 reviews after that

# everything works, something to add would be to grab the game name during the bs4 scrape step instead of just the app id name.


def get_reviews(appid, params={"json": 1}):
    try:
        url = f"https://store.steampowered.com/appreviews/{appid}"
        response = requests.get(
            url=url, params=params, headers={"User-Agent": "Mozilla/5.0"}
        ).json()
        return response
    except BaseException as e:
        print(f"Error Occurred, {e}")


def get_n_reviews(appid, n=1000):
    try:
        reviews = []
        cursor = "*"
        params = {
            "json": 1,
            "filter": "all",
            "language": "english",
            "day_range": 9223372036854775807,
            "review_type": "all",
            "purchase_type": "all",
        }

        while n > 0:
            params["cursor"] = cursor.encode()
            params["num_per_page"] = min(100, n)
            n -= 100

            response = get_reviews(appid, params)
            cursor = response["cursor"]
            for i in response["reviews"]:
                i["app_id"] = appid
            reviews += response["reviews"]

            if len(response["reviews"]) < 100:
                break

        return reviews
    except BaseException as e:
        print(f"Error Occurred, {e}")


def get_app_id(game_name):
    try:
        response = requests.get(
            url=f"https://store.steampowered.com/search/?term={game_name}&category1=998",
            headers={"User-Agent": "Mozilla/5.0"},
        )
        soup = BeautifulSoup(response.text, "html.parser")
        app_id = soup.find(class_="search_result_row")["data-ds-appid"]
        return app_id
    except BaseException as e:
        print(f"Error Occurred, {e}")


def get_n_appids(n=100, filter_by="topsellers"):
    try:
        appids = []
        url = f"https://store.steampowered.com/search/?category1=998&filter={filter_by}&page="
        page = 0

        while page * 25 < n:
            page += 1
            response = requests.get(
                url=url + str(page), headers={"User-Agent": "Mozilla/5.0"}
            )
            soup = BeautifulSoup(response.text, "html.parser")
            for row in soup.find_all(class_="search_result_row"):
                appids.append(row["data-ds-appid"])

        return appids[:n]
    except BaseException as e:
        print(f"Error Occurred, {e}")


def gather_reviews(app_ids_num, num_reviews: int) -> pd.DataFrame:
    """
    Function which grabs a random # of Steam Reviews and applies Sentiment Analysis with NLTK Vader Lexicon.
    50 Games with 100 Reviews each returns 5000 reviews.

    Args:
        app_ids_num (int) - The Number of Games to scrape

        num_reviews (int) - The Number of Reviews per game to scrape

    Returns:
        DataFrame of Steam Reviews for the specified number of reviews to be scraped
    """
    try:
        reviews = []
        app_ids = get_n_appids(app_ids_num)

        for appid in app_ids:
            reviews += get_n_reviews(appid, 100)

        df = pd.DataFrame(reviews)
        df = df.join(
            pd.DataFrame(df["author"].values.tolist(), index=df.index).add_prefix(
                "author_"
            )
        )
        df[["timestamp_created", "timestamp_updated", "author_last_played"]] = df[
            ["timestamp_created", "timestamp_updated", "author_last_played"]
        ].apply(pd.to_numeric)
        df["timestamp_created"] = df["timestamp_created"].apply(
            lambda x: datetime.utcfromtimestamp(x)
        )
        df["timestamp_updated"] = df["timestamp_updated"].apply(
            lambda x: datetime.utcfromtimestamp(x)
        )
        df["author_last_played"] = df["author_last_played"].apply(
            lambda x: datetime.utcfromtimestamp(x)
        )
        df = df.drop("author", axis=1)

        analyzer = SentimentIntensityAnalyzer()
        df["compound"] = [analyzer.polarity_scores(x)["compound"] for x in df["review"]]
        df["neg"] = [analyzer.polarity_scores(x)["neg"] for x in df["review"]]
        df["neu"] = [analyzer.polarity_scores(x)["neu"] for x in df["review"]]
        df["pos"] = [analyzer.polarity_scores(x)["pos"] for x in df["review"]]
        df["sentiment"] = np.where(df["compound"] > 0, 1, 0)

        return df
    except BaseException as e:
        print(f"Error Occurred, {e}")


df = gather_reviews(app_ids_num=50, num_reviews=100)
df.head(5)

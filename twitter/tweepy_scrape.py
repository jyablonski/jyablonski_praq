import os
from datetime import datetime, timedelta
import time

import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import numpy as np
import pandas as pd
import tweepy
from tweepy import OAuthHandler

yesterday = datetime.now().date() - timedelta(days=1)


def scrape_tweets(search_parameter: str, count: int, result_type: str) -> pd.DataFrame:
    auth = tweepy.OAuthHandler(
        os.environ.get("twitter_consumer_api_key"),
        os.environ.get("twitter_consumer_api_secret"),
    )

    # auth.set_access_token(
    #     os.environ.get("twitter_access_api_key"),
    #     os.environ.get("twitter_access_api_secret"),
    # )

    api = tweepy.API(auth, wait_on_rate_limit=True)

    df = pd.DataFrame()
    try:
        for tweet in tweepy.Cursor(  # result_type can be mixed, recent, or popular.
            api.search_tweets,
            search_parameter,
            count=count,
            result_type=result_type,
            until=yesterday,
        ).items(count):
            # print(status)
            df = df.append(
                {
                    "created_at": tweet._json["created_at"],
                    "tweet_id": tweet._json["id_str"],
                    "username": tweet._json["user"]["screen_name"],
                    "user_id": tweet._json["user"]["id"],
                    "tweet": tweet._json["text"],
                    "likes": tweet._json["favorite_count"],
                    "retweets": tweet._json["retweet_count"],
                    "language": tweet._json["lang"],
                    "scrape_ts": datetime.now(),
                    "profile_img": tweet._json["user"]["profile_image_url"],
                    "url": f"https://twitter.com/twitter/statuses/{tweet._json['id']}",
                },
                ignore_index=True,
            )

        analyzer = SentimentIntensityAnalyzer()
        df["compound"] = [analyzer.polarity_scores(x)["compound"] for x in df["tweet"]]
        df["neg"] = [analyzer.polarity_scores(x)["neg"] for x in df["tweet"]]
        df["neu"] = [analyzer.polarity_scores(x)["neu"] for x in df["tweet"]]
        df["pos"] = [analyzer.polarity_scores(x)["pos"] for x in df["tweet"]]
        df["sentiment"] = np.where(df["compound"] > 0, 1, 0)

        print(f"Twitter Scrape Successful, retrieving {len(df)} Tweets")
        return df
    except BaseException as e:
        print(f"Error Occurred, {e}")
        # sentry_sdk.capture_exception(e)
        df = []
        return df


def scrape_tweets_combo():
    df1 = scrape_tweets("nba", 1000, "popular")
    df2 = scrape_tweets("nba", 1000, "mixed")

    # so the scrape_ts column screws up with filtering duplicates out so
    # this code ignores that column to correctly drop the duplicates
    df_combo = pd.concat([df1, df2])
    df_combo = df_combo.drop_duplicates(
        subset=df_combo.columns.difference(["scrape_ts"])
    )

    print(
        f"Grabbing {len(df1)} Popular Tweets and {len(df2)} Mixed Tweets for {len(df_combo)} Total, {(len(df1) + len(df2) - len(df_combo))} were duplicates"
    )
    return df_combo


twitter_tweets = scrape_tweets_combo()

# upsert using tweet_id so if that tweet already exists in my database, just update the record values (likes, retweets etc).
write_to_sql_upsert(
    connection, "twitter_tweets", twitter_tweets, "upsert", ["tweet_id"],
)

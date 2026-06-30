import os
from datetime import datetime, timedelta
import time

import tweepy
from tweepy import OAuthHandler
import pandas as pd

auth = tweepy.OAuthHandler(
    os.environ.get("twitter_consumer_api_key"),
    os.environ.get("twitter_consumer_api_secret"),
)
auth.set_access_token(
    os.environ.get("twitter_access_api_key"),
    os.environ.get("twitter_access_api_secret"),
)


client = tweepy.Client(bearer_token=os.environ.get("bearer_token"))

start_time = datetime.now() - timedelta(days=1)
df2 = client.search_recent_tweets(
    "nba",
    start_time=start_time,
    tweet_fields=["id", "text", "created_at", "lang", "public_metrics"],
    expansions=["author_id"],
    user_fields=["name", "username", "profile_image_url", "url"],
    max_results=100,
)

users = {u["id"]: u for u in df2.includes["users"]}
df = pd.DataFrame()
for tweet in df2.data:
    if users[tweet.author_id]:
        user = users[tweet["author_id"]]
        df = df.append(
            {
                "created_at": tweet.data["created_at"],
                "tweet_id": tweet.data["id"],
                "username": user["username"],
                "user_id": user["id"],
                # "user_id": tweet.data["user"]["id"],
                "tweet": tweet.data["text"],
                "likes": tweet.data["public_metrics"]["like_count"],
                "retweets": tweet.data["public_metrics"]["retweet_count"],
                "replies": tweet.data["public_metrics"]["reply_count"],
                "language": tweet.data["lang"],
                "scrape_ts": datetime.now(),
                "profile_img": user["profile_image_url"],
                "url": f"https://twitter.com/twitter/statuses/{tweet.data['id']}",
            },
            ignore_index=True,
        )

df.head()

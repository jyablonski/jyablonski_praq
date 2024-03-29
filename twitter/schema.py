import numpy as np

twitter_cols = [
    "created_at",
    "tweet_id",
    "username",
    "user_id",
    "tweet",
    "likes",
    "retweets",
    "language",
    "scrape_ts",
    "profile_img",
    "url",
    "compound",
    "neg",
    "neu",
    "pos",
    "sentiment",
]

twitter_dtypes = {
    "created_at": np.dtype("O"),
    "tweet_id": np.dtype("O"),
    "username": np.dtype("O"),
    "user_id": np.dtype("float64"),
    "tweet": np.dtype("O"),
    "likes": np.dtype("float64"),
    "retweets": np.dtype("float64"),
    "language": np.dtype("O"),
    "scrape_ts": np.dtype("<M8[ns]"),
    "profile_img": np.dtype("O"),
    "url": np.dtype("O"),
    "compound": np.dtype("float64"),
    "neg": np.dtype("float64"),
    "neu": np.dtype("float64"),
    "pos": np.dtype("float64"),
    "sentiment": np.dtype("int64"),
}

"""
Data generation functions for article recommendation POC.
Generates synthetic users, articles, and interaction data.
"""

import pandas as pd
import numpy as np
from dataclasses import dataclass


@dataclass
class Config:
    """Feature schema and generation parameters."""

    n_users: int = 1000
    n_articles: int = 50
    n_interactions: int = 10000
    random_seed: int = 42

    # Numeric features (will be scaled)
    numeric_features: tuple = (
        "time_on_site_mins",
        "articles_visited",
        "pages_viewed",
        "scroll_depth_pct",
        "account_age_days",
        "total_articles_read",
        "avg_session_duration_mins",
    )

    # Categorical features (will be one-hot encoded)
    categorical_features: tuple = (
        "hour_of_day",
        "is_weekend",
        "favorite_article_type",
        "subscription_tier",
    )

    article_types: tuple = ("tech", "sports", "politics", "entertainment")


def generate_users(config: Config) -> pd.DataFrame:
    """
    Generate synthetic user feature data.
    Simulates what would live in a feature store.

    Returns:
        DataFrame with columns: user_id, favorite_article_type, account_age_days,
        total_articles_read, avg_session_duration_mins, subscription_tier
    """
    n = config.n_users

    return pd.DataFrame(
        {
            "user_id": range(n),
            "favorite_article_type": np.random.choice(config.article_types, n),
            "account_age_days": np.random.exponential(scale=365, size=n)
            .astype(int)
            .clip(1, 2000),
            "total_articles_read": np.random.exponential(scale=50, size=n)
            .astype(int)
            .clip(0, 500),
            "avg_session_duration_mins": np.random.gamma(shape=2, scale=5, size=n)
            .round(1)
            .clip(0.5, 60),
            "subscription_tier": np.random.choice(
                ["free", "basic", "premium"], n, p=[0.6, 0.25, 0.15]
            ),
        }
    )


def generate_articles(config: Config) -> pd.DataFrame:
    """
    Generate synthetic article metadata.

    Returns:
        DataFrame with columns: article_id, article_type, popularity_score
    """
    n = config.n_articles

    return pd.DataFrame(
        {
            "article_id": range(n),
            "article_type": np.random.choice(config.article_types, n),
            "popularity_score": np.random.beta(a=2, b=5, size=n).round(3),
        }
    )


def generate_interactions(config: Config) -> pd.DataFrame:
    """
    Generate synthetic user interaction/session logs.
    This is the training data with labels.

    Returns:
        DataFrame with columns: user_id, time_on_site_mins, articles_visited,
        pages_viewed, scroll_depth_pct, hour_of_day, is_weekend, clicked_ids
    """
    n = config.n_interactions

    # Generate session-level features
    time_on_site = np.random.gamma(shape=2, scale=4, size=n).round(1).clip(0.5, 60)
    articles_visited = np.random.poisson(lam=3, size=n).clip(1, 20)
    pages_viewed = (articles_visited + np.random.poisson(lam=2, size=n)).clip(1, 30)
    scroll_depth = np.random.beta(a=3, b=2, size=n).round(2) * 100

    # Time-based features
    hour_of_day = np.random.choice(range(24), n, p=_hour_distribution())
    day_of_week = np.random.choice(range(7), n)
    is_weekend = (day_of_week >= 5).astype(int)

    # Generate clicked article IDs (variable length lists as comma-separated strings)
    clicked_ids = [
        ",".join(
            map(
                str, np.random.choice(config.n_articles, size=num_clicks, replace=False)
            )
        )
        for num_clicks in articles_visited
    ]

    return pd.DataFrame(
        {
            "user_id": np.random.randint(0, config.n_users, n),
            "time_on_site_mins": time_on_site,
            "articles_visited": articles_visited,
            "pages_viewed": pages_viewed,
            "scroll_depth_pct": scroll_depth,
            "hour_of_day": hour_of_day,
            "is_weekend": is_weekend,
            "clicked_ids": clicked_ids,
        }
    )


def _hour_distribution() -> list[float]:
    """
    Generate realistic hour-of-day probability distribution.
    Peaks around morning (8-9am) and evening (7-9pm).
    """
    hours = np.arange(24)
    # Two peaks: morning commute and evening
    morning_peak = np.exp(-0.5 * ((hours - 8) / 2) ** 2)
    evening_peak = np.exp(-0.5 * ((hours - 20) / 3) ** 2)
    combined = morning_peak + evening_peak * 1.2
    return (combined / combined.sum()).tolist()


def generate_all_data(
    config: Config,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Generate all synthetic datasets.

    Returns:
        Tuple of (users_df, articles_df, interactions_df)
    """
    np.random.seed(config.random_seed)
    return (
        generate_users(config),
        generate_articles(config),
        generate_interactions(config),
    )

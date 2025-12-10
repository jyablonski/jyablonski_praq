"""
Model training pipeline for article recommendations.
Uses sklearn Pipeline to bundle preprocessing with the model.
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.multioutput import MultiOutputClassifier
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score

from data_generator import Config


# Feature columns used for training (must match wrapper expectations)
SESSION_FEATURES = [
    "time_on_site_mins",
    "articles_visited",
    "pages_viewed",
    "scroll_depth_pct",
    "hour_of_day",
    "is_weekend",
]

USER_FEATURES = [
    "favorite_article_type",
    "account_age_days",
    "total_articles_read",
    "avg_session_duration_mins",
    "subscription_tier",
]

NUMERIC_FEATURES = [
    "time_on_site_mins",
    "articles_visited",
    "pages_viewed",
    "scroll_depth_pct",
    "account_age_days",
    "total_articles_read",
    "avg_session_duration_mins",
]

CATEGORICAL_FEATURES = [
    "hour_of_day",
    "is_weekend",
    "favorite_article_type",
    "subscription_tier",
]


def build_preprocessor() -> ColumnTransformer:
    """
    Build the preprocessing step using ColumnTransformer.
    Routes numeric features to StandardScaler, categorical to OneHotEncoder.

    Returns:
        Configured ColumnTransformer
    """
    return ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), NUMERIC_FEATURES),
            (
                "cat",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                CATEGORICAL_FEATURES,
            ),
        ],
        # this ignores any columns not explicitly listed (safety net)
        remainder="drop",
    )


def build_pipeline() -> Pipeline:
    """
    Build the full sklearn Pipeline with preprocessing and classifier.

    Returns:
        sklearn Pipeline ready for fitting
    """
    preprocessor = build_preprocessor()

    # RandomForest to handle the multi-label problem (predicting click probability for
    # each of the N articles independently)
    #   When you call pipeline.fit(X, y), it fits the scaler/encoder on X, transforms X, then trains the classifier
    #   When you call pipeline.predict(X_new), it transforms X_new using the already-fitted scaler/encoder, then predicts
    classifier = MultiOutputClassifier(
        RandomForestClassifier(
            n_estimators=50,
            max_depth=10,
            random_state=42,
            n_jobs=-1,
        )
    )

    # The key benefit: preprocessing params (means, std devs, category mappings) are saved with the pipeline.
    # So when the REST API loads the model and calls predict on new data, it applies the exact same
    # transformations that were learned during training. No train/serve skew.
    return Pipeline(
        [
            ("preprocessor", preprocessor),
            ("classifier", classifier),
        ]
    )


def prepare_training_data(
    interactions_df: pd.DataFrame,
    users_df: pd.DataFrame,
    config: Config,
) -> tuple[pd.DataFrame, np.ndarray]:
    """
    Prepare features (X) and labels (y) for training.
    Joins interaction data with user features.

    Returns:
        Tuple of (X DataFrame, y multi-label array of shape (n_samples, n_articles))
    """
    # Join session-level data with user features we synthetically generated
    # in production, this would be pulled from snowflake or a feature store for training
    merged = interactions_df.merge(
        users_df[["user_id"] + USER_FEATURES],
        on="user_id",
        how="left",
    )

    # Extract feature columns
    feature_cols = SESSION_FEATURES + USER_FEATURES
    X = merged[feature_cols]

    # Convert clicked_ids string to multi-label binary array
    # clicked_ids is comma-separated string like "1,5,12"
    n_samples = len(merged)
    n_articles = config.n_articles
    y = np.zeros((n_samples, n_articles), dtype=int)

    # Converts "1,5,12" -> [0,1,0,0,0,1,0,0,0,0,0,0,1,0,...] which is the format
    # the MultiOutputClassifier expects for multi-label classification
    for idx, clicked_str in enumerate(merged["clicked_ids"]):
        if clicked_str:
            clicked_ids = [int(x) for x in clicked_str.split(",")]
            y[idx, clicked_ids] = 1

    return X, y


def train_model(
    users_df: pd.DataFrame,
    articles_df: pd.DataFrame,
    interactions_df: pd.DataFrame,
    config: Config,
) -> tuple[Pipeline, dict]:
    """
    Train the recommendation model.

    Returns:
        Tuple of (fitted sklearn Pipeline, metrics dict)
    """
    # Prepare training data
    X, y = prepare_training_data(interactions_df, users_df, config)

    # 80/20 Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=config.random_seed
    )

    # Build and fit pipeline on the 80% training set
    pipeline = build_pipeline()
    pipeline.fit(X_train, y_train)

    # Evaluate on 20% test set
    y_pred = pipeline.predict(X_test)

    # Calculate performance metrics so we can log them to this run in MLflow
    # Exact match accuracy (all articles correct for a sample)
    exact_match = (y_pred == y_test).all(axis=1).mean()

    # Per-article average accuracy
    per_article_acc = accuracy_score(y_test.flatten(), y_pred.flatten())

    # Hamming score (1 - hamming loss)
    hamming = 1 - (y_pred != y_test).mean()

    metrics = {
        "exact_match_accuracy": round(exact_match, 4),
        "per_label_accuracy": round(per_article_acc, 4),
        "hamming_score": round(hamming, 4),
        "n_train_samples": len(X_train),
        "n_test_samples": len(X_test),
        "n_articles": config.n_articles,
    }

    print("Training complete:")
    print(f"  Exact match accuracy: {metrics['exact_match_accuracy']:.2%}")
    print(f"  Per-label accuracy:   {metrics['per_label_accuracy']:.2%}")
    print(f"  Hamming score:        {metrics['hamming_score']:.2%}")

    return pipeline, metrics

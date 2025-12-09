"""
MLflow PyFunc wrapper for article recommendations.
Handles feature enrichment and prediction formatting for production use.
"""

import pandas as pd
import numpy as np
import mlflow.pyfunc
import mlflow.sklearn


class ArticleRecommenderWrapper(mlflow.pyfunc.PythonModel):
    """
    Production wrapper that:
    1. Loads user features and sklearn pipeline on startup
    2. Enriches incoming requests with user features (simulates feature store lookup)
    3. Runs predictions through the pipeline
    4. Formats output for API consumption
    """

    def load_context(self, context):
        """
        Called once when model is loaded (e.g., server startup).
        Load artifacts from MLflow.

        Available in context.artifacts:
            - "users_db": path to users parquet file
            - "articles_db": path to articles parquet file
            - "sklearn_pipeline": path to saved sklearn pipeline
        """
        self.users_df = pd.read_parquet(context.artifacts["users_db"])
        self.articles_df = pd.read_parquet(context.artifacts["articles_db"])
        self.pipeline = mlflow.sklearn.load_model(context.artifacts["sklearn_pipeline"])

        # Cache feature columns expected by pipeline (exclude user_id and target cols)
        self._user_feature_cols = [
            "favorite_article_type",
            "account_age_days",
            "total_articles_read",
            "avg_session_duration_mins",
            "subscription_tier",
        ]
        self._session_feature_cols = [
            "time_on_site_mins",
            "articles_visited",
            "pages_viewed",
            "scroll_depth_pct",
            "hour_of_day",
            "is_weekend",
        ]

    def predict(self, context, model_input: pd.DataFrame) -> list[dict]:
        """
        Generate article recommendations for users.

        Args:
            context: MLflow context (unused here, artifacts already loaded)
            model_input: DataFrame with columns:
                - user_id (required)
                - session features: time_on_site_mins, articles_visited,
                  pages_viewed, scroll_depth_pct, hour_of_day, is_weekend

        Returns:
            List of recommendation dicts, one per input row:
            [{"user_id": 123, "recommendations": [{"article_id": 1, "score": 0.85, ...}, ...]}, ...]
        """
        if "user_id" not in model_input.columns:
            raise ValueError("model_input must contain 'user_id' column")

        # Enrich with user features (simulates feature store lookup)
        enriched = model_input.merge(
            self.users_df[["user_id"] + self._user_feature_cols],
            on="user_id",
            how="left",
        )

        # Check for unknown users
        if enriched[self._user_feature_cols[0]].isna().any():
            unknown_ids = model_input.loc[
                enriched[self._user_feature_cols[0]].isna(), "user_id"
            ].tolist()
            raise ValueError(f"Unknown user_id(s): {unknown_ids}")

        # Select features in expected order for pipeline
        feature_cols = self._session_feature_cols + self._user_feature_cols
        X = enriched[feature_cols]

        # Get probabilities for each article (shape: n_samples x n_articles)
        # Pipeline outputs list of arrays for MultiOutput, need to stack
        proba_list = self.pipeline.predict_proba(X)
        # Each element is (n_samples, 2) for binary classification - take P(click=1)
        probabilities = np.column_stack([p[:, 1] for p in proba_list])

        # Format recommendations for each input row
        results = []
        for idx, row in enumerate(model_input.itertuples()):
            recs = self._format_recommendations(row.user_id, probabilities[idx])
            results.append(recs)

        return results

    def _format_recommendations(
        self, user_id: int, probabilities: np.ndarray, top_k: int = 5
    ) -> dict:
        """
        Format raw probabilities into ranked recommendations.

        Args:
            user_id: The user ID
            probabilities: Array of click probabilities per article (length = n_articles)
            top_k: Number of recommendations to return

        Returns:
            Dict with user_id and list of top_k recommendations sorted by score
        """
        # Get top k article indices by probability (descending)
        top_indices = np.argsort(probabilities)[::-1][:top_k]

        recommendations = []
        for article_idx in top_indices:
            article_row = self.articles_df[
                self.articles_df["article_id"] == article_idx
            ].iloc[0]

            recommendations.append(
                {
                    "article_id": int(article_idx),
                    "score": round(float(probabilities[article_idx]), 4),
                    "article_type": article_row["article_type"],
                    "popularity_score": round(
                        float(article_row["popularity_score"]), 3
                    ),
                }
            )

        return {
            "user_id": int(user_id),
            "recommendations": recommendations,
        }

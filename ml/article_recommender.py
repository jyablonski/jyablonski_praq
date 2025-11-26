"""
Production-Grade MRE: Article Recommendation Pipeline
Best Practices: Scikit-Learn Pipelines + MLflow PyFunc Wrapper + Feature Store Simulation
"""

import polars as pl
import pandas as pd  # sklearn pipelines play nicest with pandas
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.multioutput import MultiOutputClassifier
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import mlflow
import mlflow.pyfunc
import mlflow.sklearn
from dataclasses import dataclass
from pathlib import Path
import warnings
import shutil

warnings.filterwarnings("ignore")

# Clean up previous runs
if Path("mlruns").exists():
    shutil.rmtree("mlruns")
if Path("model_artifacts").exists():
    shutil.rmtree("model_artifacts")
Path("model_artifacts").mkdir(exist_ok=True)


# =============================================================================
# 1. Configuration
# =============================================================================


@dataclass
class Config:
    n_users: int = 1000
    n_articles: int = 50
    n_interactions: int = 10000
    n_recommendations: int = 5
    # Features that need scaling (Numerical)
    numeric_features: tuple = (
        "time_on_site_mins",
        "articles_visited",
        "pages_viewed",
        "scroll_depth_pct",
        "account_age_days",
        "total_articles_read",
        "avg_session_duration_mins",
    )
    # Features that need encoding (Categorical)
    categorical_features: tuple = (
        "hour_of_day",
        "is_weekend",
        "favorite_article_type",
        "subscription_tier",
    )
    article_types: tuple = ("tech", "sports", "politics", "entertainment")
    random_seed: int = 42


# =============================================================================
# 2. Data Generation (Same as before, but returns clean DataFrames)
# =============================================================================


def generate_data(config: Config):
    """Generates synthetic relational data."""
    np.random.seed(config.random_seed)

    # --- Users (The "Feature Store" Data) ---
    users_df = pl.DataFrame(
        {
            "user_id": list(range(1, config.n_users + 1)),
            "favorite_article_type": np.random.choice(
                config.article_types, config.n_users
            ),
            "account_age_days": np.random.randint(1, 1000, config.n_users),
            "total_articles_read": np.random.randint(0, 500, config.n_users),
            "avg_session_duration_mins": np.round(
                np.random.exponential(15, config.n_users), 2
            ),
            "subscription_tier": np.random.choice(
                ["free", "basic", "premium"], config.n_users
            ),
        }
    )

    # --- Articles (Content Data) ---
    articles_df = pl.DataFrame(
        {
            "article_id": list(range(1, config.n_articles + 1)),
            "article_type": [
                config.article_types[i % len(config.article_types)]
                for i in range(config.n_articles)
            ],
            "popularity_score": np.random.beta(2, 5, config.n_articles) * 100,
        }
    )

    # --- Interactions (Training Logs) ---
    interactions = []
    for _ in range(config.n_interactions):
        user_id = np.random.randint(1, config.n_users + 1)
        # Simplified interaction logic for brevity
        interactions.append(
            {
                "user_id": user_id,
                "time_on_site_mins": np.random.exponential(10),
                "articles_visited": np.random.poisson(3),
                "pages_viewed": np.random.randint(1, 10),
                "scroll_depth_pct": np.random.beta(2, 2) * 100,
                "hour_of_day": np.random.randint(0, 24),
                "is_weekend": np.random.choice([0, 1]),
                # Random clicks for MRE purposes
                "clicked_ids": np.random.choice(
                    range(1, config.n_articles + 1),
                    size=np.random.randint(0, 4),
                    replace=False,
                ).tolist(),
            }
        )

    return users_df, articles_df, pl.DataFrame(interactions)


# =============================================================================
# 3. The "Feature Store" Wrapper (Best Practice)
# =============================================================================


class ArticleRecommenderWrapper(mlflow.pyfunc.PythonModel):
    """
    This class wraps the pipeline and simulates the Production environment.
    It encapsulates the logic of:
    1. Accepting partial input (Session data only)
    2. Fetching User Features (simulating Redis lookup)
    3. Merging them
    4. Running the Scikit-Learn Pipeline
    5. Formatting the output
    """

    def load_context(self, context):
        # This runs when model is loaded (e.g., server startup)
        # We load our "Simulated Redis" (parquet files)
        self.users_df = pd.read_parquet(context.artifacts["users_db"])
        self.articles_df = pd.read_parquet(context.artifacts["articles_db"])

        # Load the actual trained pipeline
        # Note: We use the sklearn loader inside the pyfunc loader
        self.pipeline = mlflow.sklearn.load_model(context.artifacts["sk_pipeline"])

        self.n_articles = len(self.articles_df)

    def predict(self, context, model_input):
        """
        Args:
            context: MLflow context
            model_input: Pandas DataFrame containing Session Data + User ID
        """
        # 1. Simulate "Feature Store" Lookup
        # Join session data (input) with user data (lookup)
        if "user_id" not in model_input.columns:
            raise ValueError("Input must contain 'user_id'")

        # Left join to enrich session data with static user traits
        enriched_input = model_input.merge(self.users_df, on="user_id", how="left")

        # 2. Run the Scikit-Learn Pipeline (Scaling + Encoding + Prediction)
        # The pipeline handles the raw strings/numbers automatically
        # Predict_proba returns a list of arrays (one per output class)
        probas_list = self.pipeline.predict_proba(enriched_input)

        # 3. Format Recommendations
        # Extract the probability of "Class 1" (Click) for each article
        # Shape: (n_samples, n_articles)
        click_probs = np.array([prob_col[:, 1] for prob_col in probas_list]).T

        results = []
        for i, row_probs in enumerate(click_probs):
            user_id = model_input.iloc[i]["user_id"]

            # Get Top 5 indices
            top_indices = np.argsort(row_probs)[::-1][:5]

            recs = []
            for rank, idx in enumerate(top_indices, 1):
                # Article IDs are 1-based in our data, indices are 0-based
                art_id = idx + 1
                art_meta = self.articles_df[
                    self.articles_df["article_id"] == art_id
                ].iloc[0]

                recs.append(
                    {
                        "rank": rank,
                        "article_id": int(art_id),
                        "type": art_meta["article_type"],
                        "score": round(row_probs[idx], 4),
                    }
                )

            results.append({"user_id": int(user_id), "recommendations": recs})

        return results


# =============================================================================
# 4. Training Pipeline
# =============================================================================


def train_pipeline():
    config = Config()

    print("📦 Generating Data...")
    users_pl, articles_pl, interactions_pl = generate_data(config)

    # Prep Training Data
    # We join HERE for training, but the Wrapper joins dynamically during inference
    train_df = interactions_pl.join(users_pl, on="user_id", how="left").to_pandas()

    X = train_df[list(config.numeric_features) + list(config.categorical_features)]

    # Create Targets (Multi-label)
    y = np.zeros((len(train_df), config.n_articles), dtype=int)
    for i, clicked in enumerate(train_df["clicked_ids"]):
        for art_id in clicked:
            y[i, art_id - 1] = 1

    # --- BEST PRACTICE: The Pipeline ---
    # We do NOT manually scale. We let the pipeline do it.

    # handle unknown = false means if a column appears in inference that wasn't in training,
    # it won't error out
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), list(config.numeric_features)),
            (
                "cat",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                list(config.categorical_features),
            ),
        ],
        verbose_feature_names_out=False,
    )

    # Bundle Preprocessing + Model
    sk_pipeline = Pipeline(
        [
            ("preprocessor", preprocessor),
            (
                "classifier",
                MultiOutputClassifier(
                    RandomForestClassifier(n_estimators=50, max_depth=5, n_jobs=-1)
                ),
            ),
        ]
    )

    print("🏋️ Training Pipeline...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    sk_pipeline.fit(X_train, y_train)

    # Quick eval
    print(
        f"  ✓ Training Accuracy (Exact Match): {sk_pipeline.score(X_test, y_test):.4f}"
    )

    # --- BEST PRACTICE: Saving to MLflow ---
    print("💾 Logging to MLflow...")
    mlflow.set_experiment("Production_Recommender")

    with mlflow.start_run() as run:
        # 1. Save artifacts LOCALLY first
        # We need physical files to pass to the artifacts dictionary
        users_pl.write_parquet("model_artifacts/users.parquet")
        articles_pl.write_parquet("model_artifacts/articles.parquet")

        # Save the pipeline to a local folder explicitly
        # We use save_model instead of log_model for this step to get a local copy
        if Path("model_artifacts/local_sk_pipeline").exists():
            shutil.rmtree("model_artifacts/local_sk_pipeline")

        mlflow.sklearn.save_model(sk_pipeline, "model_artifacts/local_sk_pipeline")

        # 2. Log the Wrapper (The Logic)
        mlflow.pyfunc.log_model(
            artifact_path="recommender_engine",
            python_model=ArticleRecommenderWrapper(),
            artifacts={
                # Point to the LOCAL folder we just created
                "sk_pipeline": "model_artifacts/local_sk_pipeline",
                "users_db": "model_artifacts/users.parquet",
                "articles_db": "model_artifacts/articles.parquet",
            },
        )

        run_id = run.info.run_id
        print(f"  ✓ Model saved with Run ID: {run_id}")
        return run_id


# =============================================================================
# 5. Production Inference Simulation
# =============================================================================

if __name__ == "__main__":
    # 1. Run Training
    run_id = train_pipeline()

    # 2. Simulate Production API
    print("\n🚀 SIMULATING PRODUCTION API")
    print("=" * 50)

    # Load the model Generic (PyFunc) - This is what your API does
    # It doesn't know it's a Random Forest. It just knows it's a "PythonModel"
    model_uri = f"runs:/{run_id}/recommender_engine"
    production_model = mlflow.pyfunc.load_model(model_uri)

    # 3. The Frontend Request (Session Data ONLY)
    # Notice: We do NOT send "subscription_tier" or "age". The model looks that up.
    frontend_request = pd.DataFrame(
        [
            {
                "user_id": 42,
                "time_on_site_mins": 45.5,
                "articles_visited": 8,
                "pages_viewed": 12,
                "scroll_depth_pct": 88.0,
                "hour_of_day": 20,
                "is_weekend": 0,
            }
        ]
    )

    print("\n📨 Received Request:")
    print(frontend_request.to_dict(orient="records")[0])

    # 4. Generate Recommendations
    # The wrapper automatically: Joins User Data -> Scales -> Encodes -> Predicts -> Ranks
    response = production_model.predict(frontend_request)

    print("\n✅ API Response:")
    import json

    print(json.dumps(response, indent=2))

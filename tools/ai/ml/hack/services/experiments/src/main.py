"""
Main entrypoint for training and registering the article recommender.
Orchestrates data generation, training, and MLflow logging.
"""

import os
import shutil
from pathlib import Path

import mlflow
import mlflow.pyfunc
import mlflow.sklearn
from mlflow.tracking import MlflowClient

from data_generator import Config, generate_all_data
from model_train import train_model
from model_wrapper import ArticleRecommenderWrapper


# Artifact directory for local saves before MLflow logging
ARTIFACT_DIR = Path("model_artifacts")


def setup_mlflow():
    """Configure MLflow tracking URI and experiment."""
    tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment("Article_Recommender")
    print(f"MLflow tracking URI: {tracking_uri}")


def save_artifacts_locally(sk_pipeline, users_df, articles_df) -> dict:
    """
    Save artifacts to local directory before logging to MLflow.

    Returns:
        Dict of artifact paths for mlflow.pyfunc.log_model
    """
    # Clean and create artifact directory
    if ARTIFACT_DIR.exists():
        shutil.rmtree(ARTIFACT_DIR)
    ARTIFACT_DIR.mkdir(parents=True)

    # Save dataframes as parquet
    users_path = ARTIFACT_DIR / "users_db.parquet"
    articles_path = ARTIFACT_DIR / "articles_db.parquet"
    users_df.to_parquet(users_path, index=False)
    articles_df.to_parquet(articles_path, index=False)

    # Save sklearn pipeline
    sklearn_path = ARTIFACT_DIR / "sklearn_pipeline"

    # this is just using MLflow's serialization format to save to a local directory,
    # not uploading to the MLflow server yet.
    # we want to bundle all the artifacts (data, pipeline, and wrapper class) together
    # when we log the pyfunc model to MLflow in `log_model_to_mlflow`
    mlflow.sklearn.save_model(sk_pipeline, sklearn_path)

    return {
        "users_db": str(users_path),
        "articles_db": str(articles_path),
        "sklearn_pipeline": str(sklearn_path),
    }


def log_model_to_mlflow(artifact_paths: dict, metrics: dict, config: Config) -> str:
    """
    Log the pyfunc wrapper, artifacts, and metrics to MLflow.

    Returns:
        Run ID
    """
    with mlflow.start_run() as run:
        # Log parameters
        mlflow.log_params(
            {
                "n_users": config.n_users,
                "n_articles": config.n_articles,
                "n_interactions": config.n_interactions,
                "random_seed": config.random_seed,
            }
        )

        # Log metrics
        mlflow.log_metrics(metrics)

        # Log the pyfunc model with all artifacts
        # code_paths bundles the wrapper source so it can be loaded without the original module structure
        mlflow.pyfunc.log_model(
            artifact_path="recommender_model",
            python_model=ArticleRecommenderWrapper(),  # this gets pickled and saved, and then loaded back in for the rest api
            # save users and articles data along w/ the model, simulating a feature store lookup that would happen in production
            artifacts=artifact_paths,
            code_paths=[
                "model_wrapper.py"
            ],  # this is needed to ensure the source code and imports are available when loading the model
            pip_requirements=[
                "pandas",
                "numpy",
                "scikit-learn",
                "mlflow",
                "pyarrow",
            ],
        )

        print(f"Logged model to run: {run.info.run_id}")
        return run.info.run_id


def register_model(run_id: str, model_name: str = "article_recommender"):
    """
    Register model to MLflow Model Registry and set alias.
    """
    model_uri = f"runs:/{run_id}/recommender_model"

    # Register the model
    model_version = mlflow.register_model(model_uri, model_name)
    print(f"Registered model '{model_name}' version {model_version.version}")

    # Set alias to 'production' (replaces deprecated stage transitions)
    client = MlflowClient()
    client.set_registered_model_alias(model_name, "production", model_version.version)
    print(f"Set alias 'production' -> version {model_version.version}")


def cleanup_artifacts():
    """Remove local artifact directory after logging."""
    if ARTIFACT_DIR.exists():
        shutil.rmtree(ARTIFACT_DIR)


def main():
    """Main training and registration flow."""
    # Setup
    setup_mlflow()
    config = Config()

    # Generate data
    print("\n--- Generating synthetic data ---")
    users_df, articles_df, interactions_df = generate_all_data(config)
    print(
        f"Users: {len(users_df)}, Articles: {len(articles_df)}, Interactions: {len(interactions_df)}"
    )

    # Train
    print("\n--- Training model ---")
    sk_pipeline, metrics = train_model(users_df, articles_df, interactions_df, config)

    # Save pipeline + model and log it to MLflow under a new run ID
    print("\n--- Logging to MLflow ---")
    artifact_paths = save_artifacts_locally(sk_pipeline, users_df, articles_df)
    run_id = log_model_to_mlflow(artifact_paths, metrics, config)

    # Register the model so the API can pick it up like `models:/article_recommender@production` and
    # not some random run ID
    print("\n--- Registering model ---")
    register_model(run_id)

    # Cleanup local artifacts
    cleanup_artifacts()

    print("\nDone! View in MLflow UI: http://localhost:5000")


if __name__ == "__main__":
    main()

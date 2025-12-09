"""
REST API for article recommendations.
Loads model from MLflow and serves predictions.
"""

import os
import logging
from contextlib import asynccontextmanager

import pandas as pd
import mlflow.pyfunc
from mlflow.tracking import MlflowClient
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# Global model reference and metadata
model = None
model_metadata = {"name": None, "version": None}


class RecommendationRequest(BaseModel):
    """Input schema for recommendation endpoint."""

    user_id: int
    time_on_site_mins: float
    articles_visited: int
    pages_viewed: int
    scroll_depth_pct: float
    hour_of_day: int
    is_weekend: int


class ArticleRecommendation(BaseModel):
    """Single article recommendation."""

    article_id: int
    score: float
    article_type: str
    popularity_score: float


class RecommendationResponse(BaseModel):
    """Output schema for recommendation endpoint."""

    user_id: int
    recommendations: list[ArticleRecommendation]
    model_name: str
    model_version: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load model on startup."""
    global model, model_metadata

    mlflow_uri = os.getenv("MLFLOW_CONN_URI", "http://localhost:5000")
    model_name = os.getenv("MODEL_NAME", "article_recommender")
    model_alias = os.getenv("MODEL_ALIAS", "production")

    logger.info(f"Connecting to MLflow at {mlflow_uri}")
    mlflow.set_tracking_uri(mlflow_uri)

    # Get version number from alias
    client = MlflowClient()
    version_info = client.get_model_version_by_alias(model_name, model_alias)
    model_version = version_info.version

    model_uri = f"models:/{model_name}@{model_alias}"
    logger.info(f"Loading model: {model_uri} (version {model_version})")

    model = mlflow.pyfunc.load_model(model_uri)
    model_metadata = {"name": model_name, "version": model_version}
    logger.info("Model loaded successfully")

    yield

    logger.info("Shutting down...")


app = FastAPI(title="Article Recommender API", lifespan=lifespan)


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "model_name": model_metadata["name"],
        "model_version": model_metadata["version"],
    }


@app.post("/recommend", response_model=RecommendationResponse)
async def recommend(request: RecommendationRequest):
    """
    Get article recommendations for a user session.
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    # Convert request to DataFrame (model expects DataFrame input)
    input_df = pd.DataFrame([request.model_dump()])

    try:
        results = model.predict(input_df)
        return {
            **results[0],
            "model_name": model_metadata["name"],
            "model_version": model_metadata["version"],
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        logger.exception("Prediction failed")
        raise HTTPException(status_code=500, detail="Prediction failed")

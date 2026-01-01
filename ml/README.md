## ML Model Packaging with MLflow PyFunc and Sklearn Pipeline

1. Define the Feature Schema

Explicitly separate the numeric and categorical features upfront. This drives the preprocessing pipeline.

```python
@dataclass
class Config:
    numeric_features: tuple = ("time_on_site_mins", "articles_visited", ...)
    categorical_features: tuple = ("hour_of_day", "is_weekend", ...)
```

This becomes the contract between the data generation, training, and inference steps.

______________________________________________________________________

2. Generate/Load Training Data

Produce three datasets that mirror what you'd have in production: user features (what lives in the feature store), content metadata (articles/products/etc), and interaction logs (the training signal).

```python
def generate_data(config: Config) -> tuple[pl.DataFrame, pl.DataFrame, pl.DataFrame]:
    # users_df: static user attributes (feature store simulation)
    # articles_df: content metadata
    # interactions_df: session logs with labels (clicked_ids, purchased, etc)
    return users_df, articles_df, interactions_df
```

Keep these separate—you'll join them for training but the inference wrapper needs to do that join dynamically.

______________________________________________________________________

3. Build the Preprocessing + Model Pipeline

Use `ColumnTransformer` to route feature types to appropriate transformers, then wrap everything in a `Pipeline` so preprocessing is serialized with the model.

```python
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder

preprocessor = ColumnTransformer(
    transformers=[
        ("num", StandardScaler(), list(config.numeric_features)),
        ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False),
         list(config.categorical_features)),
    ]
)

sk_pipeline = Pipeline([
    ("preprocessor", preprocessor),
    ("classifier", YourModel(...)),
])
```

Key methods: `sk_pipeline.fit(X, y)` learns preprocessing params + model weights. `sk_pipeline.predict()` or `predict_proba()` transforms then predicts in one call.

______________________________________________________________________

4. Create the PyFunc Wrapper

This is the "production logic" layer. It handles feature enrichment (simulating feature store lookups) and output formatting. The REST API calls this, not the raw sklearn pipeline.

```python
class YourModelWrapper(mlflow.pyfunc.PythonModel):

    def load_context(self, context):
        # Called once when model loads (server startup)
        self.users_df = pd.read_parquet(context.artifacts["users_db"])
        self.pipeline = mlflow.sklearn.load_model(context.artifacts["sk_pipeline"])

    def predict(self, context, model_input: pd.DataFrame):
        # 1. Enrich input with feature store data
        enriched = model_input.merge(self.users_df, on="user_id", how="left")

        # 2. Run pipeline (preprocessing happens automatically)
        predictions = self.pipeline.predict_proba(enriched)

        # 3. Format output for the API contract
        return self._format_response(predictions)
```

The wrapper's job: accept minimal input -> enrich -> predict -> format. The sklearn pipeline inside handles the transform.

______________________________________________________________________

5. Log Everything to MLflow

Save artifacts locally first, then log the pyfunc wrapper with references to those artifacts.

```python
with mlflow.start_run() as run:
    # Save supporting data
    users_df.write_parquet("artifacts/users.parquet")
    mlflow.sklearn.save_model(sk_pipeline, "artifacts/sk_pipeline")

    # Log the wrapper + all its dependencies
    mlflow.pyfunc.log_model(
        artifact_path="my_model",
        python_model=YourModelWrapper(),
        artifacts={
            "sk_pipeline": "artifacts/sk_pipeline",
            "users_db": "artifacts/users.parquet",
        },
    )
```

Key methods: `mlflow.sklearn.save_model()` for the pipeline, `mlflow.pyfunc.log_model()` for the wrapper that uses it.

______________________________________________________________________

6. Register and Promote the Model

Push to MLflow's model registry so the REST API can pull by name/stage rather than run ID.

```python
client = mlflow.tracking.MlflowClient()

model_uri = f"runs:/{run_id}/my_model"
mv = mlflow.register_model(model_uri, "my_model_name")

client.transition_model_version_stage(
    name="my_model_name",
    version=mv.version,
    stage="Production"
)
```

______________________________________________________________________

7. Load and Serve

The REST API loads the production model and calls predict. The wrapper handles everything else.

```python
# In your FastAPI/Flask service
model = mlflow.pyfunc.load_model("models:/my_model_name/Production")

@app.post("/predict")
def predict(session_data: dict):
    input_df = pd.DataFrame([session_data])
    return model.predict(input_df)
```

Key method: `mlflow.pyfunc.load_model()` returns an object with a `.predict()` that routes to your wrapper's predict.

______________________________________________________________________

Summary of the flow:

```
Training:  raw data -> join -> fit Pipeline -> save Pipeline -> wrap in PyFunc -> log to MLflow -> register

Inference: session input -> PyFunc.predict() -> enrich from artifacts -> Pipeline.predict_proba() -> format -> return
```

The sklearn `Pipeline` guarantees preprocessing consistency. The `pyfunc` wrapper guarantees your production logic (enrichment, formatting) travels with the model.

## Steps

### 1. Define feature schema

- Create a config class/dict that explicitly lists `numeric_features` and `categorical_features`
- This schema is shared across training and inference

### 2. Generate synthetic data

- Create 3 dataframes:
  - `users_df`: static user attributes (simulates feature store)
  - `articles_df`: content metadata
  - `interactions_df`: session logs with labels (e.g., `clicked_ids`)
- Keep them separate—don't pre-join

### 3. Build the sklearn Pipeline

- Use `ColumnTransformer` to route features to appropriate transformers:
  - `StandardScaler` for numeric features
  - `OneHotEncoder(handle_unknown="ignore")` for categorical features
- Wrap in `Pipeline` with your classifier:
  ```python
  Pipeline([
      ("preprocessor", preprocessor),
      ("classifier", YourModel()),
  ])
  ```
- Call `sk_pipeline.fit(X_train, y_train)`

### 4. Create the PyFunc wrapper class

- Subclass `mlflow.pyfunc.PythonModel`
- Implement `load_context(self, context)`:
  - Load feature store data from `context.artifacts["users_db"]`
  - Load sklearn pipeline via `mlflow.sklearn.load_model(context.artifacts["sk_pipeline"])`
- Implement `predict(self, context, model_input)`:
  - Enrich input by joining with feature store data
  - Call `self.pipeline.predict_proba(enriched_input)`
  - Format and return results

### 5. Log to MLflow

- Save artifacts locally first:
  - `users_df.write_parquet("artifacts/users.parquet")`
  - `mlflow.sklearn.save_model(sk_pipeline, "artifacts/sk_pipeline")`
- Log the wrapper with `mlflow.pyfunc.log_model()`:
  ```python
  mlflow.pyfunc.log_model(
      artifact_path="model_name",
      python_model=YourWrapper(),
      artifacts={
          "sk_pipeline": "artifacts/sk_pipeline",
          "users_db": "artifacts/users.parquet",
      },
  )
  ```

### 6. Register model to MLflow registry

- `mlflow.register_model(model_uri, "model_name")`
- `client.transition_model_version_stage(name, version, stage="Production")`

### 7. Load in REST API

- `model = mlflow.pyfunc.load_model("models:/model_name/Production")`
- Call `model.predict(input_df)` — wrapper handles enrichment and preprocessing automatically

______________________________________________________________________

**Key point to emphasize:** The sklearn `Pipeline` guarantees preprocessing travels with the model. The `pyfunc` wrapper guarantees your production logic (feature lookups, output formatting) travels with it too.

## Commands

```sh
curl -X POST http://localhost:8083/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 42,
    "time_on_site_mins": 5.2,
    "articles_visited": 3,
    "pages_viewed": 5,
    "scroll_depth_pct": 72.5,
    "hour_of_day": 14,
    "is_weekend": 0
  }'

{
  "user_id": 42,
  "recommendations": [
    {
      "article_id": 20,
      "score": 0.1106,
      "article_type": "sports",
      "popularity_score": 0.332
    },
    {
      "article_id": 34,
      "score": 0.0967,
      "article_type": "tech",
      "popularity_score": 0.367
    },
    {
      "article_id": 36,
      "score": 0.0936,
      "article_type": "tech",
      "popularity_score": 0.47
    },
    {
      "article_id": 25,
      "score": 0.0929,
      "article_type": "entertainment",
      "popularity_score": 0.109
    },
    {
      "article_id": 11,
      "score": 0.0902,
      "article_type": "sports",
      "popularity_score": 0.527
    }
  ],
  "model_name": "article_recommender",
  "model_version": "2"
}

```

## Production Setting

In Prod, the wrapper class would only need to load the model artifact. The API would handle feature enrichment before calling `predict`.

```py
def load_context(self, context):
    # Just the model - that's all MLflow needs to provide
    self.pipeline = mlflow.sklearn.load_model(context.artifacts["sklearn_pipeline"])

def predict(self, context, model_input: pd.DataFrame) -> list[dict]:
    # model_input already has everything:
    # - session features (from frontend)
    # - user features (API enriched from Redis/feature store before calling predict)

    probabilities = self.pipeline.predict_proba(model_input)
    # ... format and return
```

```py
@app.post("/recommend")
async def recommend(request: RecommendationRequest):
    # 1. Get Session data from the frontend request,
    # and user features from the feature store
    session_data = request.model_dump()
    user_features = await get_user_features(request.user_id)

    # 2. Combine into model input
    model_input = pd.DataFrame([{**session_data, **user_features}])

    # 3. Call model
    results = model.predict(model_input)
    return results
```

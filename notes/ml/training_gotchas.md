# Gotchas

## Part 1: The Core Philosophy

Moving from a Jupyter Notebook to a Production System requires a shift in mindset. We are not just training a model; we are building a software artifact that must function reliably in a live environment.

### 1\. The "Golden Rule": Prevent Training-Serving Skew

The Problem: If you manually scale data in your training script (e.g., `(x - mean) / std`), you must perfectly replicate that math in your production API. If the API uses a _new_ scaler or forgets to scale, the model receives "alien" numbers and fails.

The Solution: The "Model" is not just the algorithm (Random Forest). The "Model" is the entire transformation pipeline:
$$Model = \text{Scalers} + \text{Encoders} + \text{Algorithm}$$

### 2\. Production Architecture

In a live recommendation system, the Frontend cannot send everything (it doesn't know the user's subscription tier or account age).

- Frontend sends: _Session Context_ (Time on site, current page).
- Feature Store (Redis) provides: _User History_ (Age, Subscription, Favorites).
- Model API: Joins these two data sources together -> Uses Model to generate predictions -> Returns Prediction to client

You can also just pre-compute recommendations offline and store them to a database or a feature store (Redis), and then serve them directly.

- In this case, the frontend would still query an API to get the recommendations, but the API would just read from the database instead of loading the model and generating the predictions in real-time.
- Both approaches are valid, depending on the use case and latency requirements.

---

## Part 2: Data Preprocessing Standards

We never train on raw data. We must convert all inputs into a format the math can understand.

### 1\. Numerical Data (Scaling)

- Why: To prevent large numbers (Income: 1,000,000) from overpowering small numbers (Age: 30).
  - Age gap of 25 to 50 is significant, whereas income gap of $50,000 to $50,025 is nothing.
- Tool: `StandardScaler` (Z-Score Normalization).
- Effect: Centers data around 0 with a standard deviation of 1.
- Required for: Neural Networks, KNN, Linear/Logistic Regression.
- Good practice for: Tree-based models (allows for easy model swapping later).

### 2\. Categorical Data (Encoding)

- Why: Models cannot multiply strings like "Premium".
- Tool: `OneHotEncoder`.
- Effect: Converts "Premium" into `[0, 1, 0]`.
- Config: Always use `handle_unknown='ignore'` so the pipeline doesn't crash if a new category appears in production.

### 3\. Text Data (Varchar)

- Rule: Never use raw text strings.
- Strategy:
  - Simple: Extract features like `len(text)` or Sentiment Score.
  - Advanced: Use Embeddings (Vectors) to represent semantic meaning in N-dimensional space.
  - These have to be computed in advance before training the model, or before using the model to generate predictions.

---

## Part 3: The Code Implementation (Best Practices)

### Step 1: The Scikit-Learn Pipeline

Instead of manual transformations, we bundle everything into a single object. This guarantees that inference performs the exact same steps as training.

```python
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.multioutput import MultiOutputClassifier

# 1. Define the Traffic Cop (ColumnTransformer)
# It routes numeric cols to Scaler and categorical cols to Encoder
preprocessor = ColumnTransformer(
    transformers=[
        ("num", StandardScaler(), numeric_features_list),
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features_list),
    ],
    verbose_feature_names_out=False,
)

# 2. Define the Assembly Line (Pipeline)
# Raw Data -> Preprocessor -> Model -> Prediction
sk_pipeline = Pipeline([
    ("preprocessor", preprocessor),
    ("classifier", MultiOutputClassifier(RandomForestClassifier())),
])

# 3. Train the WHOLE thing
sk_pipeline.fit(X_train, y_train)
```

### Step 2: The MLflow Wrapper (PyFunc)

We wrap the pipeline in a custom Python class. This allows us to bundle the "Feature Store" logic (joining user data) alongside the model.

```python
import mlflow.pyfunc
import pandas as pd

class ArticleRecommenderWrapper(mlflow.pyfunc.PythonModel):
    def load_context(self, context):
        # Runs once when the API starts
        # Load the Pipeline AND the User Database (simulating Redis)
        self.pipeline = mlflow.sklearn.load_model(context.artifacts["sk_pipeline"])
        self.users_df = pd.read_parquet(context.artifacts["users_db"])

    def predict(self, context, model_input):
        # 1. Enrichment (The Feature Store Step)
        # Join the session input with the static user database
        # Note: We merge on user_id to fill in the missing gaps
        enriched_input = model_input.merge(self.users_df, on="user_id", how="left")

        # 2. Prediction (The Math Step)
        # The pipeline handles scaling/encoding automatically
        raw_predictions = self.pipeline.predict_proba(enriched_input)

        # 3. Formatting
        # Convert raw arrays into a nice JSON response
        return self._format_results(raw_predictions)
```

### Step 3: Saving to MLflow (The Artifact)

We save the pipeline locally first to avoid URI path errors (`file://`), then log the entire package.

```python
import mlflow
import shutil

with mlflow.start_run():
    # A. Save Pipeline Locally first (Crucial for artifacts pathing)
    if Path("local_pipeline").exists(): shutil.rmtree("local_pipeline")
    mlflow.sklearn.save_model(sk_pipeline, "local_pipeline")

    # B. Log the Wrapper + Dependencies
    mlflow.pyfunc.log_model(
        artifact_path="recommender_engine",
        python_model=ArticleRecommenderWrapper(),
        artifacts={
            "sk_pipeline": "local_pipeline",  # Point to local folder
            "users_db": "data/users.parquet", # Point to local file
        }
    )
```

### Step 4: Production Inference

The API becomes incredibly simple. It doesn't need to know about scaling, math, or user lookups. It just connects to MLFlow, loads the model, and has access to the `predict()` method that was defined during training / the model building phase.

```python
# API Code
model = mlflow.pyfunc.load_model("models:/ArticleRecommender/Production")

# The request only needs session info
client_data = pd.DataFrame([{
    "user_id": 42,
    "time_on_site_mins": 5.5,
    "current_page": "sports"
}])

# The model handles the rest (in this example, it joins user data internally)
recs = model.predict(client_data=client_data)

# you could also pull user data separately and pass it in if desired

user_data = get_data_from_feature_store(user_id=42)

recs = model.predict(client_data=client_data, user_data=user_data)
```

---

## Part 4: Feature Importance & Interpretation

- It is an Output, not an Input: You cannot force the model to prioritize a field. You can only measure what it found useful.
- MDI (Mean Decrease in Impurity): The default Random Forest metric. Measures how much "cleaner" the data gets when splitting on a specific feature.
- Permutation Importance: The "Gold Standard." It shuffles a column randomly and measures how much the accuracy _drops_. If accuracy crashes, the feature was important.

### Troubleshooting Common Errors

1.  URI Error (`file://...`):

    - _Cause:_ MLflow trying to read a URI as a local file path during logging.
    - _Fix:_ Save the Scikit-Learn model to a local folder first (`save_model`), then point to that folder in `artifacts`.

2.  Column Collision (`Avg Duration` exists in input and lookup):

    - _Cause:_ Pandas `merge` renames duplicate columns to `col_x` and `col_y`.
    - _Fix:_ Ensure the input request only contains session data, and the lookup only provides user data. Do not pass the same field in both.

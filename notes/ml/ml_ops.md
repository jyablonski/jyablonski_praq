# ML Ops

ML Ops (Machine Learning Operations) is the practice of applying DevOps principles to machine learning systems. It's about making ML development, deployment, and maintenance reliable, scalable, and reproducible.

It's a bridge between:

- Data Scientists building models
- ML Engineers deploying models
- Operations teams maintaining systems
- Business stakeholders needing reliable predictions & systems

## Why ML Ops

ML Ops matters because traditional systems are relatively static - you deploy code and it behaves predictably. ML systems are different and have unique challenges.

1. Models can decay, and performance degrades as real-world data drifts
2. Models are only as good as their training data, so this is a big dependency to getting good quality systems
3. Lots of experiments must be completed to find the best model
4. Hard to recreate results without proper tracking and systems in place
5. Model performance needs to be tracked, not just system health
6. Cross functional requirements because you need data scientists, engineers, and domain experts

## Core Principles

1. Automation - minimize as much manual intervention in the ML lifecycle as possible, from data validation to model deployment
2. Versioning and keeping everything in Code
   - This includes all code, Data, Models, Infrastructure, and Pipeline definitions
3. CI / CD to test, validate, evaluate models and deploy them automatically when they pass criteria
4. Monitoring & Observability to track model performance in production, in addition to system metrics
5. Reproducibility - anyone should be able to re-create any model at any time
6. Collaboration between data scientists, data engineers, DevOps / Infra engineers, and business stakeholders

## Tools

Airflow

- Purpose: Workflow orchestration
- Usage: Schedules and orchestrates ML training pipelines
- Role: Runs containerized tasks (data validation, feature engineering, model training, evaluation) as DAGs

DVC

- Purpose: Data and artifact versioning
- Usage: Tracks datasets, models, and ML artifacts using Git-like semantics
- Storage: Stores actual data in S3/GCS/Azure, keeps lightweight pointers (`.dvc` files) in Git
- Formats: CSV, JSON, Parquet, model files, etc.
- Benefit: Enables reproducibility - recreate any model training run from any Git commit

MLFlow

- Purpose: ML lifecycle management
- Usage: Experiment tracking, model registry, and deployment
- Tracks: Parameters, metrics, artifacts, code versions, and dependencies
- Storage:
  - Metadata -> Postgres/MySQL
  - Artifacts (models, plots) -> S3/GCS/Azure
  - Models serialized as pickle, joblib, ONNX, or framework-specific formats
- Features:
  - Model registry with staging/production stages
  - Model serving capabilities
  - LLM tracking (prompts, tokens, costs)
  - Model comparison and visualization UI

Python Libraries

- scikit-learn: Classical ML algorithms (regression, classification, clustering)
- XGBoost/LightGBM: Gradient boosting frameworks
- PyTorch: Deep learning and neural networks
- TensorFlow/Keras: Deep learning framework
- Pandas: Data manipulation and analysis
- NumPy: Numerical computing

## Lifecycle

### Phase 1: Problem Definition & Data Collection

Before starting, you have to sit down with stakeholders and define:

1. Business objectives and ML success metrics
2. Determine if ML is the right solution
3. Identify stakeholders to own the project and establish requirements

After establishing the problem definition, you move into the data collection part.

- Identify how to source data needed for this particular problem
- Find metadata related to the data sources, like when it's loaded, how often, and how it's transformed etc.
- Manage permissions for sensitive data

### Phase 2: Data Preparation & Feature Engineering

Before building models, ensure the data is of certain quality and standards before proceeding. Garbage in = garbage out.

- Make sure you have a representative sample, not half the dataset is missing etc, columns are properly tested

ML Ops typically utilizes feature stores. These are custom built models specifically for ML use cases, and are often different than the types of models you build out for reporting or analytics.

- These allow you to create and store feature definitions over time, so you can use the same features in training and serving across multiple models.
- Enables feature discovery so folks can easily find and use specific features they need for their models
- Helps manage feature freshness

### Phase 3: Model Development & Experimentation

When starting to build & train ML models, track everything about each experiment:

- Hyperparameters
- Metrics (accuracy, loss, etc.)
- Model architecture
- Training data version
- Code version (Git commit)
- Environment (dependencies)
- Training duration
- Hardware used

MLFlow allows you to do this within `mlflow.start_run()` blocks with the `.log_param()` and `log.metric()` methods.

Before elevating an experiment to a model, validate:

- Are performance metrics & criteria met?
- Are predictions fair across groups and not biased?
- Is the model robust enough to handle edge cases?
- Can we understand the predictions, or is a complete black box model?

### Phase 4: Model Training Pipeline

Pipelines are used to automate the entire training workflow - think Airflow, DVC, and MLFlow

- A typical pipeline might look like: validate_data >> feature_engineering >> train_model >> evaluate_model >> register_model
- This would run on a consistent basis to pull new data, ensure it passes qualtiy and validation checks, train new model, evaluate its results, and register it if everything passes

### Phase 5: Model Deployment

In terms of actually using these models in production, there are various different strategies here

1. Batch Prediction
   - Run predictions on a schedule in batches
   - Example: My ML Pipeline Script for the NBA Project
   - Simple, effective, easy to do.
2. Real Time Serving
   - Run the model on demand via a REST API
   - Model gets used when specific endpoints are hit, and results are provided in the response
   - Allows for low latency, real time responses that can be ran on-demand
3. Streaming
   - Run the model in Spark or Python by reading data in from something like Kafka or Kinesis, and immediately applying the model on the input records before writing the data back out someplace

Deployment methods here are similar to traditional software deployment strategies.

- Shadow Mode where you run the new model alongside the old one, and compare across the 2 versions without affecting users
- Canary deployment where you deploy the new model and use it for only a small % of traffic. Gradually increase usage if performance is fine, or rollback if not.
- Blue-green deployment where you have 2 identical environments and you switch between the current and old version instantly. Easy rollback
- A/B testing where you split users into groups and measure model performance w/ new and old on the different groups

### Phase 6: Monitoring and Maintenance

1. System and Infrastructure Metrics
   - Latency, throughput, error rates (on HTTP endpoints serving the models etc)
   - CPU, memory utilization
   - Request rates
2. Model Performance Metrics
   - Prediction quality: accuracy, precision, recall
   - Business metrics: revenue impact, user satisfaction
   - Statistical metrics: Distribution shifts, correlation changes
3. Data Quality Metrics
   - Missing Values
   - Outliers
   - Feature Distributions
   - Drift reports - how is the data changing over the last x days / weeks etc
4. Alerting
   - Model degradation
   - Data Drift
   - Prediciton distribution shifts
   - System errors

### Phase 7: Model Retraining

Retraining should be a continuous and ongoing processs to make sure your models are up to date.

- Done weekly, monthly, or quarterly
- Based on business cycles
- Automatically trigger retraining when drift is detected, performance drops, or new data is available

## Best Practice Workflow

```text
Git Repo
  ├── code (Python scripts)
  └── data.dvc (pointer)
          .
      DVC Remote (S3)
          └── actual data files

Training -> MLflow Tracking Server
             ├── Experiments DB (params, metrics)
             └── Artifact Store (S3)
                   └── model files

REST API -> MLflow Model Registry
                   └── Load model which gets used in endpoints to serve requests
```

## Generalized ML Use Cases

Use ML to enhance core value drivers of your business.

1. Increase user content consumption -> more page views -> more ad impressions -> more revenue
2. Reduce user churn -> retain audience -> stable growth + reach -> sustained ad inventory value
3. Optimize content placement -> right content to right users -> better engagement -> higher ad performance -> more revenue

Prioritize consumption first, this is the fastest to implement and has the most direct revenue impact. Layer in churn afterwards to protect the gains from the increased content consumption. And then refine content placement afterwards, squeezing out more value from existing traffic.

For content consumption, you typically start out by just having simple rule-based approaches like showing the "most popular today" content first, or "trending in your region" where it's filtered by geo or recency.

- ML recommendations get smarter by learning patterns like collaborative filtering: "users who read articles A + B also read C"
- Content-based looks at similar articles beyond just topic tags and uses things like writing style, sentiment, and complexity

You'd train ML models offline using historical data (what users clicked, how long they stayed, what they clicked next). The model learns patterns and generates predictions. Then:

- Model outputs predictions -> Article X has an 8% predicted click-through rate for this user
- Serving system uses those predictions -> Ranks articles and displays top recommendations on the page
- Users interact -> New data feeds back to retrain/improve the model

## ML Model Serving

Choosing whether to go with batch-based ML runs vs hosting them in a REST API and then serving results out in real-time as services request it depends on your latency requirements and how much personalization you want to include.

Batch-based (pre-computed)

- How it works: Run model daily/hourly, generate top N recommendations per user or per article, store in warehouse/cache, frontend queries these pre-computed results
- Simple, predictable costs, handles high traffic, no complex architecture needed
- But, recommendations can be stale and can't react to current session behavior
- Best for "similar articles", homepage "recommended for you" type use cases

Real-time API (on-demand)

- How it works: Frontend calls ML service with context (user ID, current article, recent clicks), model predicts and returns recommendations instantly
- Fresh recommendations based on current session, can incorporate real-time signals (what they just clicked)
- But, more complex infrastructure, latency concerns (need <100ms response), higher compute costs
- Best for highly personalized "you might also like" based on the current session and reading habits. Dynamic homepage that adapts as users browse

Typically you want to start with batch based, and then move to a real-time solution once you have experience and enough data to make it worth pursuing.

Option 1: Batch (Airflow-orchestrated)

```text
dbt models -> Data Warehouse feature tables ->
Airflow pulls data -> Apply ML model in memory ->
Write predictions back to Data Warehouse ->
(Optional) Airflow also writes predictions to Redis for faster lookups ->
Frontend calls REST API (user_id) ->
REST API fetches pre-computed recommendations from Data Warehouse or Redis ->
Return recommendations to frontend
```

Option 2: Real-time (FastAPI)

```text
Frontend sends request with user_id/article_id + real-time context features ->
REST API receives request ->
API fetches historical features from Redis (fallback to Data Warehouse if cache miss) ->
API combines historical features + real-time context from request ->
API uses combined features to run the ML model + generate recommendations ->
API returns recommendations to frontend
```

- Best practice here is to cache features in Redis and pull them from there instead of Data Warehouse, this is complex but probably the way to go from the jump
- When we build the features and save them to Data Warehouse we'll want to also update them in Redis in parallel, and then the REST API pulls them primarily from Redis - saving both cost and also improving performance, and you can always pull from Data Warehouse for fresh data if needed

Important thing to keep in mind is if the ML recommendations are not driving better metrics or user retention, then we should just be using the simple rule-based approaches.

- ML is not inherently better than rules - it's only better if it measurably improves outcomes.
- Constantly have to review ML Model performance vs actual business outcomes.
- Is click-through rate increasing? Are session times increasing? Is churn getting reduced?
- If the answer is no, then step back and move towards a more simple approach.

### Frontend

In either case, the Frontend will always need to grab this data from a REST API, it should never have direct access to pull data from Redis or Snowflake as it's a major security risk to expose them to the browser.

For option 1, your API Layer would look something like below:

```py
@app.get("/recommendations/{user_id}")
def get_recommendations(user_id: int):
    # Batch: query Redis or Snowflake for pre-computed recs
    # Both: return clean JSON response
    return {"recommendations": [...]}
```

For option 2, your API Layer on both the frontend and REST API end would look something like:

```js
// Frontend sends context + user_id
fetch("/api/recommendations", {
  method: "POST",
  body: JSON.stringify({
    user_id: 12345,
    current_article_id: 789,
    session_context: {
      articles_read_this_session: [101, 205, 334],
      time_on_site: 320, // seconds
      device: "mobile",
    },
  }),
});
```

```py
@app.post("/recommendations")
def get_recommendations(request: RecommendationRequest):
    # Fetch historical features from Redis
    user_features = redis.hgetall(f"user:{request.user_id}")

    # Combine with real-time context from frontend
    features = {
        **user_features,
        **request.session_context
    }

    # Run model
    predictions = model.predict(features)
    return {"recommendations": predictions}
```

- This gives you the best of both worlds: leverage pre-computed features for efficiency while incorporating real-time context for relevance.

## SaaS

SaaS Vendors have limited value in this ML space for providing recommandation-type services. This is typically something you want to handle and build out internally. Your company data is your competitive moat, not the ML algorithms.

- No vendor can fix poor data collection, inconsistent tracking, or missing user signals.
- No vendor can understand your data, the user behavior, your content taxonomy, or your audience segments better than you.
- Building clean event tracking, user identity resolution, content metadata, feature engineering is 80% of the effort and can't be outsourced.

The reality is that recommendation systems are a competitive advantage for digital media. Netflix, Spotify, YouTube don't outsource this - they invest in it heavily because it's core to their business.

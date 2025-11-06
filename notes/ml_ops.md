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
  - Metadata → Postgres/MySQL
  - Artifacts (models, plots) → S3/GCS/Azure
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

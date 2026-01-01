# ML Model Production & Promotion

## Overview

Managing ML models through lifecycle stages ensures safe deployment and easy rollbacks. The typical flow:

```
Training -> Staging -> Production -> (Archived)
```

Key Concept: Never deploy directly to production. Always test in staging first.

______________________________________________________________________

## Model Lifecycle Stages

### 1. None (Default)

- Model just trained, logged to MLflow
- Not registered in Model Registry yet
- Experimental, not ready for use

### 2. Staging

- Model registered and ready for testing
- Deployed to staging environment
- Receives traffic from internal testing or limited users
- Performance monitored closely

### 3. Production

- Model serving real user traffic
- Battle-tested in staging
- Main model powering your application

### 4. Archived

- Old model no longer in use
- Kept for reference/rollback
- Can be restored if needed

______________________________________________________________________

## MLflow Model Registry

### Why Model Registry?

Without Registry:

```python
# Bad: Loading models by run_id
model = mlflow.pyfunc.load_model("runs:/abc123/model")  # Which version is this?
```

With Registry:

```python
# Good: Loading models by name + stage
model = mlflow.pyfunc.load_model("models:/article_recommender/Production")  # Clear!
```

Benefits:

- Named models: `article_recommender` vs random IDs
- Version tracking: v1, v2, v3, etc.
- Stage management: Staging vs Production
- Model lineage: See which run produced this model
- Annotations: Add notes, tags, descriptions

______________________________________________________________________

## Model Registration Workflow

### Step 1: Train Model

```python
import mlflow
import mlflow.pytorch

# Train model
with mlflow.start_run(run_name="train_article_recommender"):
    mlflow.log_param("epochs", 50)
    mlflow.log_param("learning_rate", 0.001)

    # Train your model
    model = train_model()

    # Log metrics
    mlflow.log_metric("f1_score", 0.45)
    mlflow.log_metric("precision", 0.62)

    # Log model artifact
    mlflow.pytorch.log_model(model, "model")

    run_id = mlflow.active_run().info.run_id
    print(f"Model trained. Run ID: {run_id}")
```

At this point: Model is logged but NOT registered.

______________________________________________________________________

### Step 2: Register Model

```python
# Register the model from the run
model_uri = f"runs:/{run_id}/model"

model_details = mlflow.register_model(
    model_uri=model_uri,
    name="article_recommender"
)

print(f"Model registered as version {model_details.version}")
# Output: Model registered as version 1
```

What happens:

- Model gets a name: `article_recommender`
- Gets version number: v1, v2, v3, etc.
- Stored in Model Registry
- Stage defaults to "None"

______________________________________________________________________

### Step 3: Transition to Staging

```python
from mlflow.tracking import MlflowClient

client = MlflowClient()

# Move to Staging
client.transition_model_version_stage(
    name="article_recommender",
    version=1,
    stage="Staging"
)

print("Model transitioned to Staging")
```

______________________________________________________________________

### Step 4: Test in Staging

Deploy to staging environment and monitor:

- Model performance metrics
- Business metrics (CTR, conversions)
- Latency, errors
- User feedback

Staging Checklist:

- [ ] F1 score >= production model
- [ ] Latency < 100ms (p95)
- [ ] Error rate < 1%
- [ ] CTR improvement or no degradation
- [ ] Ran for at least 48 hours
- [ ] No data quality issues

______________________________________________________________________

### Step 5: Promote to Production

```python
# If staging tests pass, promote to Production
client.transition_model_version_stage(
    name="article_recommender",
    version=1,
    stage="Production"
)

# Demote old production model to Archived
client.transition_model_version_stage(
    name="article_recommender",
    version=0,  # Previous production version
    stage="Archived"
)

print("Model promoted to Production!")
```

______________________________________________________________________

## Loading Models by Stage

### In Your API

```python
from flask import Flask, request, jsonify
import mlflow.pyfunc

app = Flask(__name__)

# Load production model at startup
model = mlflow.pyfunc.load_model("models:/article_recommender/Production")

@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.json
    predictions = model.predict(data)
    return jsonify({"recommendations": predictions.tolist()})
```

Key Points:

- Load by stage name: `"models:/article_recommender/Production"`
- When you promote a new version, API automatically uses it on next restart
- No code changes needed to update model

______________________________________________________________________

## A/B Testing: Staging vs Production

Test new model against production with real traffic:

```python
import random
import mlflow.pyfunc

# Load both models
model_prod = mlflow.pyfunc.load_model("models:/article_recommender/Production")
model_staging = mlflow.pyfunc.load_model("models:/article_recommender/Staging")

@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.json

    # can hash by user_id if you want to give the same users consistent results
    # during this A/B process
    # if hash(user_id) % 100 < 10:  # Consistent 10% of users
    #     model_version = "staging"

    # Randomly assign 10% of traffic to staging model
    if random.random() < 0.10:
        predictions = model_staging.predict(data)
        model_version = "staging"
    else:
        predictions = model_prod.predict(data)
        model_version = "production"

    # Log which model was used
    log_prediction(data, predictions, model_version)

    return jsonify({"recommendations": predictions.tolist()})
```

After 1-2 weeks:

- Compare metrics between staging and production
- If staging performs better -> promote to production
- If staging performs worse -> discard

______________________________________________________________________

## Automated Promotion Logic

### Safe Promotion Criteria

```python
def should_promote_to_production(staging_version):
    """Decide if staging model should be promoted"""

    client = MlflowClient()

    # Get staging model metrics
    staging_run = client.get_run(
        client.get_model_version("article_recommender", staging_version).run_id
    )
    staging_f1 = staging_run.data.metrics['f1_score']

    # Get production model metrics
    prod_versions = client.get_latest_versions("article_recommender", stages=["Production"])
    if prod_versions:
        prod_run = client.get_run(prod_versions[0].run_id)
        prod_f1 = prod_run.data.metrics['f1_score']
    else:
        prod_f1 = 0  # No production model yet

    # Promotion criteria
    checks = {
        "f1_improved": staging_f1 > prod_f1,
        "f1_absolute": staging_f1 > 0.40,  # Minimum acceptable
        "staging_tested": has_been_in_staging_for_days(staging_version, min_days=2),
        "no_recent_alerts": not has_recent_alerts(staging_version)
    }

    # All checks must pass
    should_promote = all(checks.values())

    print(f"Promotion checks: {checks}")
    print(f"Decision: {'PROMOTE' if should_promote else 'DO NOT PROMOTE'}")

    return should_promote

def has_been_in_staging_for_days(version, min_days=2):
    """Check if model has been in staging long enough"""
    client = MlflowClient()
    model_version = client.get_model_version("article_recommender", version)

    # Check last transition timestamp
    last_transition = model_version.last_updated_timestamp
    days_in_staging = (time.time() - last_transition/1000) / 86400

    return days_in_staging >= min_days

def has_recent_alerts(version):
    """Check if staging model triggered any alerts"""
    # Query your alerting system
    # Return True if alerts found in last 24 hours
    alerts = query_alerts(model_version=version, hours=24)
    return len(alerts) > 0
```

### Automated Promotion Script

```python
def auto_promote_if_ready():
    """Check if staging model should be auto-promoted"""

    client = MlflowClient()

    # Get staging model
    staging_versions = client.get_latest_versions("article_recommender", stages=["Staging"])

    if not staging_versions:
        print("No model in staging")
        return

    staging_version = staging_versions[0].version

    # Check promotion criteria
    if should_promote_to_production(staging_version):
        print(f"Promoting version {staging_version} to Production")

        # Archive current production
        prod_versions = client.get_latest_versions("article_recommender", stages=["Production"])
        if prod_versions:
            client.transition_model_version_stage(
                name="article_recommender",
                version=prod_versions[0].version,
                stage="Archived"
            )

        # Promote staging to production
        client.transition_model_version_stage(
            name="article_recommender",
            version=staging_version,
            stage="Production"
        )

        # Send notification
        send_slack_notification(
            f"✅ Model v{staging_version} auto-promoted to Production!\n"
            f"F1 Score: {get_f1_score(staging_version):.3f}"
        )
    else:
        print("Staging model not ready for promotion")
```

Run this as a daily Airflow task:

```python
from airflow import DAG
from airflow.operators.python import PythonOperator

promotion_dag = DAG(
    'model_promotion_check',
    schedule_interval='0 4 * * *',  # Daily at 4am
    default_args={'owner': 'ml_team'}
)

check_promotion = PythonOperator(
    task_id='check_auto_promotion',
    python_callable=auto_promote_if_ready,
    dag=promotion_dag
)
```

______________________________________________________________________

## Rollback Strategy

### When to Rollback

Triggers:

- Production model F1 drops >10%
- CTR drops >15%
- Error rate spikes >5%
- Latency exceeds SLA
- Critical bug discovered

### Manual Rollback

```python
def rollback_to_previous_version():
    """Rollback to last archived version"""

    client = MlflowClient()

    # Get current production version
    prod_versions = client.get_latest_versions("article_recommender", stages=["Production"])
    current_prod_version = prod_versions[0].version

    # Get archived versions (sorted by version desc)
    archived_versions = client.get_latest_versions("article_recommender", stages=["Archived"])

    if not archived_versions:
        print("No archived version to rollback to!")
        return

    # Get most recent archived version
    rollback_version = archived_versions[0].version

    # Archive current production
    client.transition_model_version_stage(
        name="article_recommender",
        version=current_prod_version,
        stage="Archived"
    )

    # Restore archived version to production
    client.transition_model_version_stage(
        name="article_recommender",
        version=rollback_version,
        stage="Production"
    )

    print(f"Rolled back from v{current_prod_version} to v{rollback_version}")

    send_alert(
        f"ROLLBACK executed\n"
        f"From: v{current_prod_version}\n"
        f"To: v{rollback_version}"
    )
```

### Automated Rollback

```python
def check_for_auto_rollback():
    """Automatically rollback if production metrics degrade"""

    # Get recent production metrics
    recent_metrics = get_production_metrics(hours=24)

    # Check degradation
    if recent_metrics['f1_score'] < 0.35:  # Critical threshold
        print("Critical degradation detected! Auto-rolling back...")
        rollback_to_previous_version()
        return True

    if recent_metrics['error_rate'] > 0.05:  # >5% errors
        print("High error rate! Auto-rolling back...")
        rollback_to_previous_version()
        return True

    return False

# Run every hour
schedule.every().hour.do(check_for_auto_rollback)
```

______________________________________________________________________

## Model Versioning Best Practices

### Version Annotations

Add metadata to model versions:

```python
client = MlflowClient()

# Add description
client.update_model_version(
    name="article_recommender",
    version=3,
    description="Trained on 30 days data. Added user_age feature. F1: 0.47"
)

# Add tags
client.set_model_version_tag(
    name="article_recommender",
    version=3,
    key="training_date",
    value="2024-01-15"
)

client.set_model_version_tag(
    name="article_recommender",
    version=3,
    key="data_source",
    value="production_db_30days"
)
```

### Tracking Production History

Keep log of what was in production when:

```python
def log_production_deployment(version):
    """Log production deployment event"""

    deployment_log = {
        "timestamp": datetime.utcnow().isoformat(),
        "model_name": "article_recommender",
        "version": version,
        "deployed_by": "auto_promotion_script",  # or username
        "previous_version": get_previous_production_version(),
        "f1_score": get_f1_score(version),
        "deployment_reason": "auto_promotion"  # or "manual", "hotfix", "rollback"
    }

    # Store in database
    db.deployments.insert_one(deployment_log)

    print(f"Logged deployment of v{version} to production")
```

______________________________________________________________________

## Multi-Model Management

If you have multiple models:

```python
models = {
    "article_recommender": {
        "production_version": 3,
        "staging_version": 4,
        "min_f1": 0.40
    },
    "spam_classifier": {
        "production_version": 2,
        "staging_version": None,
        "min_accuracy": 0.95
    },
    "sentiment_analyzer": {
        "production_version": 5,
        "staging_version": 6,
        "min_accuracy": 0.85
    }
}

def check_all_models_for_promotion():
    """Check all models for promotion eligibility"""
    for model_name, config in models.items():
        if config['staging_version']:
            if should_promote_model(model_name, config):
                promote_to_production(model_name, config['staging_version'])
```

______________________________________________________________________

## Staging Environment Setup

### Option 1: Separate API Instance

```
Production API (port 5000)
├── Load: models:/article_recommender/Production
└── Traffic: 100% real users

Staging API (port 5001)
├── Load: models:/article_recommender/Staging
└── Traffic: Internal testing only
```

### Option 2: Shadow Mode

```python
@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.json

    # Primary prediction (production model)
    predictions_prod = model_prod.predict(data)

    # Shadow prediction (staging model) - doesn't affect response
    try:
        predictions_staging = model_staging.predict(data)
        log_shadow_prediction(data, predictions_staging, predictions_prod)
    except Exception as e:
        # Staging errors don't affect production
        log_error(f"Staging model error: {e}")

    # Return production predictions
    return jsonify({"recommendations": predictions_prod.tolist()})
```

Benefits:

- Staging model sees real traffic
- Zero risk (errors don't affect users)
- Compare predictions side-by-side

### Option 3: Canary Deployment

Gradually increase staging traffic:

```python
# Week 1: 5% staging
# Week 2: 25% staging
# Week 3: 50% staging
# Week 4: 100% staging -> promote to production

staging_percentage = 0.25  # 25% traffic

@app.route('/recommend', methods=['POST'])
def recommend():
    if random.random() < staging_percentage:
        return recommend_staging()
    else:
        return recommend_production()
```

______________________________________________________________________

## Monitoring During Transitions

### Deployment Monitoring Checklist

First 1 hour after promotion:

- [ ] Error rate < 1%
- [ ] Latency within SLA
- [ ] No crashes/exceptions

First 24 hours:

- [ ] F1 score stable
- [ ] CTR not degraded
- [ ] User complaints in normal range

First 7 days:

- [ ] Business metrics trending positive
- [ ] No data drift alerts
- [ ] A/B test results positive (if applicable)

### Automated Health Check

```python
def post_deployment_health_check(version, hours_since_deployment):
    """Check model health after deployment"""

    metrics = get_production_metrics_since(hours_since_deployment)

    checks = {
        "error_rate_ok": metrics['error_rate'] < 0.01,
        "latency_ok": metrics['p95_latency'] < 100,
        "f1_ok": metrics['f1_score'] > 0.40,
        "ctr_ok": metrics['ctr'] > 0.10
    }

    if not all(checks.values()):
        send_alert(
            f"⚠️ Post-deployment health check FAILED for v{version}\n"
            f"Failed checks: {[k for k, v in checks.items() if not v]}"
        )

        # Consider auto-rollback
        if hours_since_deployment < 24:
            rollback_to_previous_version()

    return all(checks.values())

# Run checks at intervals after deployment
# 1 hour, 6 hours, 24 hours, 7 days
```

______________________________________________________________________

## Complete Promotion Workflow

### End-to-End Process

```python
def complete_model_lifecycle():
    """Full workflow from training to production"""

    # 1. Train model
    print("Step 1: Training model...")
    run_id = train_and_log_model()

    # 2. Register model
    print("Step 2: Registering model...")
    model_version = register_model(run_id)

    # 3. Transition to staging
    print("Step 3: Moving to Staging...")
    transition_to_staging(model_version)

    # 4. Deploy to staging environment
    print("Step 4: Deploying to Staging API...")
    deploy_to_staging(model_version)

    # 5. Monitor in staging
    print("Step 5: Monitoring in Staging (48 hours)...")
    time.sleep(48 * 3600)  # Wait 48 hours

    # 6. Check promotion criteria
    print("Step 6: Checking promotion criteria...")
    if should_promote_to_production(model_version):

        # 7. Promote to production
        print("Step 7: Promoting to Production...")
        promote_to_production(model_version)

        # 8. Deploy to production API
        print("Step 8: Deploying to Production API...")
        deploy_to_production(model_version)

        # 9. Monitor post-deployment
        print("Step 9: Monitoring production deployment...")
        for hours in [1, 6, 24]:
            time.sleep(hours * 3600)
            post_deployment_health_check(model_version, hours)

        print("✅ Model successfully deployed to production!")
    else:
        print("❌ Model did not meet promotion criteria")
```

______________________________________________________________________

## Summary

Model Lifecycle:

1. Train -> Log to MLflow
1. Register -> Get version number
1. Staging -> Test with limited traffic
1. Production -> Serve real users
1. Archived -> Keep for rollback

Key Operations:

- `mlflow.register_model()` - Register trained model
- `transition_model_version_stage()` - Move between stages
- `load_model("models:/name/Stage")` - Load by stage
- Automated promotion based on criteria
- Automated rollback on degradation

Best Practices:

- Always test in staging first
- Set clear promotion criteria
- Monitor closely after promotion
- Keep rollback plan ready
- Automate promotion/rollback"1\`
- Log all deployments
- Use A/B testing when possible

Integration with REST API:

```python
# API loads model by stage
model = mlflow.pyfunc.load_model("models:/article_recommender/Production")

# When you promote a new version, restart API
# API automatically loads newest production model
```

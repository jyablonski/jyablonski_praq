# ML Model Monitoring

## Overview

Model monitoring tracks three critical dimensions:

1. Model Performance - Technical metrics (F1, precision, accuracy)
1. Business Metrics - Real-world impact (CTR, sales, revenue)
1. Operational Metrics - System health (predictions/day, latency, errors)

Why monitor? Models degrade over time due to data drift, concept drift, and changing user behavior. Monitoring catches problems before they impact users.

______________________________________________________________________

## The Three Pillars of ML Monitoring

### 1. Model Performance Monitoring

What: Track ML metrics over time to detect model degradation

Key Metrics:

- Precision, Recall, F1 Score
- Accuracy
- AUC-ROC
- Confusion matrix
- Loss values

When to track:

- After each retraining (compare to baseline)
- On validation/test sets
- On production data (when ground truth is available)

______________________________________________________________________

### 2. Business Metrics Monitoring

What: Track real-world outcomes the model is supposed to improve

Key Metrics:

- Click-through rate (CTR)
- Conversion rate
- Revenue per user
- User engagement (time on site, pages viewed)
- Customer satisfaction (NPS, surveys)

When to track:

- Continuously in production
- Before/after model deployments
- A/B tests between model versions

______________________________________________________________________

### 3. Operational Metrics Monitoring

What: Track system health and usage patterns

Key Metrics:

- Prediction volume (requests/day)
- Prediction latency (p50, p95, p99)
- Error rate (4xx, 5xx)
- Model staleness (hours since last update)
- Data quality issues

When to track:

- Real-time in production
- Alert on anomalies

______________________________________________________________________

## Monitoring Architecture

### Components

```
┌─────────────┐
│   REST API  │ ← Serves predictions
└──────┬──────┘
       │
       ↓
┌──────────────────┐
│  Logging Layer   │ ← Log predictions + metadata
└──────┬───────────┘
       │
       ↓
┌──────────────────┐
│  Metrics Store   │ ← Store metrics (Prometheus, InfluxDB)
│  (Time series DB)│
└──────┬───────────┘
       │
       ↓
┌──────────────────┐
│  Dashboard       │ ← Visualize (Grafana, MLflow)
│  (Grafana)       │
└──────────────────┘
```

______________________________________________________________________

## 1. Model Performance Monitoring

### What to Log

Every prediction should log:

```python
{
    "timestamp": "2024-01-15T10:30:00Z",
    "model_name": "article_recommender",
    "model_version": "v2.3",
    "user_id": "user_12345",
    "input": {
        "article_ids_read": ["article_1", "article_5"],
        "time_on_site": 420
    },
    "prediction": ["article_10", "article_15", "article_20"],
    "prediction_scores": [0.92, 0.87, 0.83],
    "latency_ms": 12,
    "ground_truth": null  # Filled in later when user clicks
}
```

### Implementing Prediction Logging

```python
# In your REST API
from flask import Flask, request, jsonify
import mlflow
import time
import json
from datetime import datetime

app = Flask(__name__)

# Load model
model = mlflow.pyfunc.load_model("models:/article_recommender/Production")

@app.route('/recommend', methods=['POST'])
def recommend():
    start_time = time.time()
    data = request.json

    # Make prediction
    predictions = model.predict(data)

    # Calculate latency
    latency_ms = (time.time() - start_time) * 1000

    # Log prediction
    log_prediction({
        "timestamp": datetime.utcnow().isoformat(),
        "model_name": "article_recommender",
        "model_version": model.metadata.version,
        "user_id": data['user_id'],
        "input": data,
        "prediction": predictions.tolist(),
        "latency_ms": latency_ms,
        "ground_truth": None
    })

    return jsonify({"recommended_article_ids": predictions.tolist()})

def log_prediction(log_entry):
    """Write prediction log to file/database"""
    # Option 1: Write to file
    with open('/var/log/predictions.jsonl', 'a') as f:
        f.write(json.dumps(log_entry) + '\n')

    # Option 2: Write to database
    # db.predictions.insert_one(log_entry)

    # Option 3: Send to message queue
    # kafka_producer.send('predictions', log_entry)
```

### Collecting Ground Truth

When user interacts, log the outcome:

```python
@app.route('/feedback', methods=['POST'])
def log_feedback():
    """Log when user clicks on recommended article"""
    data = request.json

    # Update prediction log with ground truth
    update_prediction_log(
        user_id=data['user_id'],
        timestamp=data['prediction_timestamp'],
        clicked_articles=data['clicked_articles']
    )

    return jsonify({"status": "logged"})
```

### Calculating Performance Metrics

Batch job that runs daily:

```python
import pandas as pd
from sklearn.metrics import precision_score, recall_score, f1_score

def calculate_daily_metrics():
    """Calculate model performance for yesterday"""

    # Load prediction logs with ground truth
    df = pd.read_json('/var/log/predictions.jsonl', lines=True)
    df = df[df['ground_truth'].notna()]  # Only predictions with feedback
    df = df[df['timestamp'] >= yesterday]

    # Calculate metrics
    y_true = df['ground_truth']  # What user actually clicked
    y_pred = df['prediction']    # What model recommended

    # Precision: Of articles recommended, how many were clicked?
    precision = precision_score(y_true, y_pred, average='samples')

    # Recall: Of articles clicked, how many were recommended?
    recall = recall_score(y_true, y_pred, average='samples')

    # F1: Harmonic mean
    f1 = f1_score(y_true, y_pred, average='samples')

    # Log to metrics store
    log_metrics({
        "date": str(datetime.now().date()),
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
        "sample_count": len(df)
    })

    print(f"Daily metrics - Precision: {precision:.3f}, Recall: {recall:.3f}, F1: {f1:.3f}")
```

### Tracking Metrics in MLflow

```python
import mlflow

def log_production_metrics():
    """Log production metrics to MLflow"""

    metrics = calculate_daily_metrics()

    # Log to MLflow
    with mlflow.start_run(run_name=f"production_metrics_{date}"):
        mlflow.log_metric("precision", metrics['precision'])
        mlflow.log_metric("recall", metrics['recall'])
        mlflow.log_metric("f1_score", metrics['f1_score'])
        mlflow.log_metric("sample_count", metrics['sample_count'])
        mlflow.set_tag("environment", "production")
        mlflow.set_tag("model_version", "v2.3")
```

### Detecting Model Degradation

```python
def check_for_degradation():
    """Alert if model performance drops"""

    # Get last 7 days of F1 scores
    recent_f1_scores = get_last_n_days_metrics('f1_score', n=7)

    # Get baseline (training validation F1)
    baseline_f1 = 0.44  # From training

    # Calculate average recent performance
    avg_recent_f1 = sum(recent_f1_scores) / len(recent_f1_scores)

    # Alert if dropped more than 10%
    degradation = (baseline_f1 - avg_recent_f1) / baseline_f1

    if degradation > 0.10:
        send_alert(
            f"⚠️ Model degradation detected!\n"
            f"Baseline F1: {baseline_f1:.3f}\n"
            f"Recent F1: {avg_recent_f1:.3f}\n"
            f"Drop: {degradation*100:.1f}%"
        )
```

______________________________________________________________________

## 2. Business Metrics Monitoring

### Defining Business Metrics

For Article Recommender:

- Primary: CTR (Click-Through Rate) - % of recommendations clicked
- Secondary:
  - Time on site after recommendation
  - Articles read per session
  - User return rate

For E-commerce Recommender:

- Primary: Conversion rate, Revenue per user
- Secondary: Add-to-cart rate, Average order value

### Implementing CTR Tracking

```python
def calculate_daily_ctr():
    """Calculate click-through rate on recommendations"""

    # Load predictions with ground truth
    df = pd.read_json('/var/log/predictions.jsonl', lines=True)
    df = df[df['timestamp'] >= yesterday]

    # Count recommendations shown
    total_recommendations = len(df) * 5  # 5 articles per recommendation

    # Count clicks
    total_clicks = df['ground_truth'].apply(lambda x: len(x) if x else 0).sum()

    # Calculate CTR
    ctr = total_clicks / total_recommendations if total_recommendations > 0 else 0

    # Log to metrics
    log_business_metric({
        "date": str(datetime.now().date()),
        "metric": "ctr",
        "value": ctr,
        "total_recommendations": total_recommendations,
        "total_clicks": total_clicks
    })

    print(f"Daily CTR: {ctr*100:.2f}%")

    return ctr
```

### A/B Testing Model Versions

Compare business metrics between models:

```python
def compare_models_ab_test():
    """Compare CTR between two model versions"""

    # Group users randomly into A/B groups
    # Group A gets model v2.3, Group B gets model v2.4

    df = load_ab_test_data()

    # Calculate CTR for each group
    ctr_a = calculate_ctr(df[df['model_version'] == 'v2.3'])
    ctr_b = calculate_ctr(df[df['model_version'] == 'v2.4'])

    # Statistical significance test
    from scipy import stats
    t_stat, p_value = stats.ttest_ind(
        df[df['model_version'] == 'v2.3']['clicked'],
        df[df['model_version'] == 'v2.4']['clicked']
    )

    print(f"Model v2.3 CTR: {ctr_a*100:.2f}%")
    print(f"Model v2.4 CTR: {ctr_b*100:.2f}%")
    print(f"Improvement: {(ctr_b - ctr_a)/ctr_a*100:.1f}%")
    print(f"Statistical significance: p={p_value:.4f}")

    if p_value < 0.05 and ctr_b > ctr_a:
        return "Promote v2.4 to production"
    else:
        return "Keep v2.3 in production"
```

### Revenue Impact

```python
def calculate_revenue_impact():
    """Calculate revenue attributed to recommendations"""

    # Load user purchase data
    df_purchases = load_purchase_data()
    df_predictions = load_prediction_logs()

    # Join: Did user buy something that was recommended?
    df = df_purchases.merge(
        df_predictions,
        on=['user_id', 'session_id'],
        how='left'
    )

    # Calculate revenue from recommended items
    recommended_revenue = df[
        df['purchased_item'].isin(df['recommended_items'])
    ]['purchase_amount'].sum()

    total_revenue = df['purchase_amount'].sum()

    recommendation_attribution = recommended_revenue / total_revenue

    print(f"Total revenue: ${total_revenue:,.2f}")
    print(f"From recommendations: ${recommended_revenue:,.2f}")
    print(f"Attribution: {recommendation_attribution*100:.1f}%")
```

### Setting Business Metric Baselines

```python
# Before deploying ML model
baseline_ctr = 0.08  # 8% CTR with random recommendations

# After deploying ML model
ml_ctr = 0.12  # 12% CTR with ML recommendations

improvement = (ml_ctr - baseline_ctr) / baseline_ctr
print(f"ML model improved CTR by {improvement*100:.0f}%")  # 50% improvement
```

______________________________________________________________________

## 3. Operational Metrics Monitoring

### Prediction Volume

Track how many predictions are made:

```python
def log_prediction_volume():
    """Count predictions per hour/day"""

    df = pd.read_json('/var/log/predictions.jsonl', lines=True)
    df['hour'] = pd.to_datetime(df['timestamp']).dt.floor('H')

    # Predictions per hour
    hourly_volume = df.groupby('hour').size()

    # Alert if volume drops suddenly
    if hourly_volume.iloc[-1] < hourly_volume.mean() * 0.5:
        send_alert("⚠️ Prediction volume dropped 50%!")

    return hourly_volume
```

### Prediction Latency

Track how long predictions take:

```python
def monitor_latency():
    """Track prediction latency percentiles"""

    df = pd.read_json('/var/log/predictions.jsonl', lines=True)
    df = df[df['timestamp'] >= last_hour]

    # Calculate percentiles
    p50 = df['latency_ms'].quantile(0.50)
    p95 = df['latency_ms'].quantile(0.95)
    p99 = df['latency_ms'].quantile(0.99)

    print(f"Latency - p50: {p50:.1f}ms, p95: {p95:.1f}ms, p99: {p99:.1f}ms")

    # Alert if p95 exceeds SLA
    if p95 > 100:  # SLA: 95% of requests < 100ms
        send_alert(f"⚠️ Latency SLA violated! p95: {p95:.1f}ms")

    # Log to monitoring system
    prometheus_client.gauge('prediction_latency_p50').set(p50)
    prometheus_client.gauge('prediction_latency_p95').set(p95)
    prometheus_client.gauge('prediction_latency_p99').set(p99)
```

### Error Rate

Track prediction failures:

```python
def monitor_error_rate():
    """Track API errors and model exceptions"""

    # From API logs
    total_requests = get_api_request_count(last_hour)
    error_requests = get_api_error_count(last_hour)

    error_rate = error_requests / total_requests if total_requests > 0 else 0

    print(f"Error rate: {error_rate*100:.2f}%")

    # Alert if error rate spikes
    if error_rate > 0.01:  # > 1% error rate
        send_alert(f"⚠️ High error rate: {error_rate*100:.2f}%")

    return error_rate
```

### Data Quality Monitoring

Monitor input data for anomalies:

```python
def monitor_input_data():
    """Check for unusual input patterns"""

    df = pd.read_json('/var/log/predictions.jsonl', lines=True)
    df = df[df['timestamp'] >= last_hour]

    # Extract input features
    df['articles_count'] = df['input'].apply(lambda x: len(x['article_ids_read']))
    df['time_on_site'] = df['input'].apply(lambda x: x['time_on_site'])

    # Check for anomalies
    avg_articles = df['articles_count'].mean()
    avg_time = df['time_on_site'].mean()

    # Alert if significantly different from training distribution
    if avg_articles < 1 or avg_articles > 20:
        send_alert(f"⚠️ Unusual articles_count: {avg_articles:.1f}")

    if avg_time < 10 or avg_time > 3600:
        send_alert(f"⚠️ Unusual time_on_site: {avg_time:.0f}s")
```

______________________________________________________________________

## Monitoring Dashboards

### Grafana Dashboard Layout

Panel 1: Model Performance (Last 30 Days)

- Line chart: F1 score, Precision, Recall over time
- Threshold line: Baseline performance
- Alert annotations when degradation detected

Panel 2: Business Metrics (Last 7 Days)

- Line chart: CTR, Conversion rate over time
- Comparison: Current vs previous week
- Revenue attribution pie chart

Panel 3: Operational Metrics (Last 24 Hours)

- Gauge: Current predictions/hour
- Line chart: Latency (p50, p95, p99)
- Single stat: Error rate %

Panel 4: Data Distribution (Real-time)

- Histogram: time_on_site distribution
- Bar chart: Most recommended articles
- Heat map: Predictions by hour of day

### Sample Grafana Query (Prometheus)

```promql
# Prediction volume
rate(predictions_total[5m])

# Latency p95
histogram_quantile(0.95, prediction_latency_seconds_bucket)

# Error rate
rate(prediction_errors_total[5m]) / rate(predictions_total[5m])
```

______________________________________________________________________

## Alerting Rules

### Performance Degradation

```python
# Alert if F1 drops >10% from baseline
if current_f1 < baseline_f1 * 0.9:
    send_alert(
        severity="warning",
        message=f"F1 score dropped to {current_f1:.3f} (baseline: {baseline_f1:.3f})"
    )
```

### Business Metric Drop

```python
# Alert if CTR drops >15% week-over-week
if current_ctr < last_week_ctr * 0.85:
    send_alert(
        severity="critical",
        message=f"CTR dropped {(1-current_ctr/last_week_ctr)*100:.0f}% WoW"
    )
```

### System Health

```python
# Alert if prediction volume drops suddenly
if hourly_predictions < expected_predictions * 0.5:
    send_alert(
        severity="critical",
        message=f"Prediction volume abnormally low: {hourly_predictions}"
    )

# Alert if latency exceeds SLA
if p95_latency > 100:  # 100ms SLA
    send_alert(
        severity="warning",
        message=f"Latency SLA violated: p95={p95_latency}ms"
    )

# Alert if error rate spikes
if error_rate > 0.05:  # >5% errors
    send_alert(
        severity="critical",
        message=f"High error rate: {error_rate*100:.1f}%"
    )
```

______________________________________________________________________

## Data Drift Detection

### Input Distribution Monitoring

```python
from scipy import stats

def detect_input_drift():
    """Compare current input distribution to training distribution"""

    # Load training data distribution
    train_time_mean = 300  # seconds
    train_time_std = 120

    # Load recent production data
    df = load_recent_predictions(days=7)
    prod_time_mean = df['input'].apply(lambda x: x['time_on_site']).mean()
    prod_time_std = df['input'].apply(lambda x: x['time_on_site']).std()

    # Statistical test for distribution shift
    # KS test (Kolmogorov-Smirnov)
    train_sample = np.random.normal(train_time_mean, train_time_std, 1000)
    prod_sample = df['input'].apply(lambda x: x['time_on_site']).values

    statistic, p_value = stats.ks_2samp(train_sample, prod_sample)

    if p_value < 0.05:
        send_alert(
            f"⚠️ Input data drift detected!\n"
            f"Training mean: {train_time_mean}s\n"
            f"Production mean: {prod_time_mean:.0f}s\n"
            f"Consider retraining model"
        )
```

### Prediction Distribution Monitoring

```python
def detect_prediction_drift():
    """Check if model predictions have shifted"""

    # Load baseline prediction distribution (from validation set)
    baseline_avg_score = 0.75

    # Load recent predictions
    df = load_recent_predictions(days=7)
    current_avg_score = df['prediction_scores'].apply(lambda x: np.mean(x)).mean()

    # Check for significant shift
    if abs(current_avg_score - baseline_avg_score) > 0.1:
        send_alert(
            f"⚠️ Prediction distribution shifted!\n"
            f"Baseline avg: {baseline_avg_score:.2f}\n"
            f"Current avg: {current_avg_score:.2f}"
        )
```

______________________________________________________________________

## Complete Monitoring Pipeline

### Daily Monitoring Script

```python
import schedule
import time

def daily_monitoring_job():
    """Run all monitoring checks daily"""

    print("Starting daily monitoring job...")

    # 1. Model Performance
    metrics = calculate_daily_metrics()
    check_for_degradation()

    # 2. Business Metrics
    ctr = calculate_daily_ctr()
    revenue_impact = calculate_revenue_impact()

    # 3. Operational Metrics
    volume = log_prediction_volume()

    # 4. Data Quality
    detect_input_drift()
    detect_prediction_drift()

    # 5. Generate daily report
    generate_daily_report({
        'metrics': metrics,
        'ctr': ctr,
        'revenue': revenue_impact,
        'volume': volume
    })

    print("Daily monitoring job complete!")

# Schedule job
schedule.every().day.at("03:00").do(daily_monitoring_job)

while True:
    schedule.run_pending()
    time.sleep(60)
```

### Airflow DAG for Monitoring

```python
from airflow import DAG
from airflow.operators.python import PythonOperator

monitoring_dag = DAG(
    'ml_monitoring',
    schedule_interval='0 3 * * *',  # Daily at 3am
    default_args={'owner': 'ml_team'}
)

calculate_metrics_task = PythonOperator(
    task_id='calculate_metrics',
    python_callable=calculate_daily_metrics,
    dag=monitoring_dag
)

check_degradation_task = PythonOperator(
    task_id='check_degradation',
    python_callable=check_for_degradation,
    dag=monitoring_dag
)

calculate_ctr_task = PythonOperator(
    task_id='calculate_ctr',
    python_callable=calculate_daily_ctr,
    dag=monitoring_dag
)

detect_drift_task = PythonOperator(
    task_id='detect_drift',
    python_callable=detect_input_drift,
    dag=monitoring_dag
)

# Run checks in parallel, then generate report
[calculate_metrics_task, calculate_ctr_task, detect_drift_task] >> check_degradation_task
```

______________________________________________________________________

## Best Practices

### 1. Start Simple

Begin with the basics:

- Log all predictions
- Track one key business metric (CTR)
- Monitor prediction volume
- Expand from there

### 2. Set Realistic Baselines

- Benchmark before deploying ML
- Use validation metrics as initial production baseline
- Update baselines as model improves

### 3. Alert on Trends, Not Noise

- Use moving averages (7-day, 30-day)
- Require sustained degradation before alerting
- Avoid alert fatigue

### 4. Keep Ground Truth Collection Simple

- Don't wait for perfect labels
- Use implicit feedback (clicks, purchases)
- Collect subset of ground truth, not everything

### 5. Monitor Model AND Business

- ML metrics (F1) don't always correlate with business (revenue)
- Both matter - track both
- Optimize for business outcomes

### 6. Automate Everything

- Automated daily metrics calculation
- Automated alerting
- Automated report generation
- Manual analysis only for anomalies

______________________________________________________________________

## Summary

The three pillars:

1. Model Performance - F1, precision, recall -> Are predictions accurate?
1. Business Metrics - CTR, revenue, conversions -> Is the model driving value?
1. Operational Metrics - Volume, latency, errors -> Is the system healthy?

Key implementation steps:

1. Log every prediction with metadata
1. Collect ground truth asynchronously
1. Calculate metrics daily
1. Alert on degradation
1. Visualize in dashboards
1. Review weekly

Tools:

- Logging: JSON files, database, Kafka
- Metrics: Prometheus, InfluxDB, MLflow
- Dashboards: Grafana, MLflow UI
- Alerting: PagerDuty, Slack, Email

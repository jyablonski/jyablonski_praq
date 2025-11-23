# Airflow for ML Model Retraining

## 1. The "When": Trigger Strategies

_Don't just default to "Every Monday at 2 AM". Choose a strategy based on data velocity and drift sensitivity._

### A. Scheduled (Time-Based)

- Best for: Freshness-sensitive models (e.g., News Recommenders, Stock Forecasting) where new data _always_ implies better performance.
- Pattern: `Cron` schedule in Airflow.
- Gotcha: If your upstream ETL is late, your model trains on old data.
  - Fix: Use an Airflow Sensor (`ExternalTaskSensor` or `SqlSensor`) to check for a "Data Ready" flag in Snowflake/S3 before kicking off the training pod.

### B. Drift-Triggered (Performance-Based)

- Best for: Stable domains (e.g., Fraud Detection, Computer Vision) where patterns change rarely but drastically.
- Pattern: Decouple monitoring from training.
  1. A lightweight "Monitor DAG" runs daily to compute KL Divergence or PSI (Population Stability Index) on recent inference data vs. training baseline.
  2. If `drift_score > threshold`, it triggers the "Retraining DAG" via the `TriggerDagRunOperator`.
- Why: Saves massive compute costs by not retraining when the world hasn't changed.

### C. Hybrid (The "Big Tech" Standard)

- Strategy: Retrain on a loose schedule (e.g., weekly) to capture slow drift, but have an emergency trigger for sudden concept drift (e.g., a flash sale or breaking news event causes model performance to tank).

---

## 2. The "Why": Types of Decay

_Understanding what you are fixing determines your training window._

| Drift Type                   | What happened?                                                                                       | Detection Metric                                  | Remediation                                                               |
| :--------------------------- | :--------------------------------------------------------------------------------------------------- | :------------------------------------------------ | :------------------------------------------------------------------------ |
| Data Drift (Covariate Shift) | The input distribution changed (e.g., Users are now mostly on Mobile instead of Desktop).            | PSI or JS Divergence on feature columns.          | Retrain on the _new_ distribution (recent window).                        |
| Concept Drift                | The relationship changed (e.g., "Buying a mask" meant "Construction" in 2019, but "Health" in 2020). | Decline in F1 / Accuracy (requires ground truth). | Retrain immediately; potentially increase model complexity.               |
| Upstream Data Change         | Engineering broke a pipe (e.g., "Age" changed from `years` to `days`).                               | Schema Validation or `% Nulls`.                   | Do Not Retrain. Fix the pipeline. Retraining on broken data encodes bugs. |

---

## 3. Automation at Scale: The Promotion Gate

_How to automate the "Go / No-Go" decision without humans._

### The "Challenger" Pattern (Logic for your Branch Operator)

Never promote a model solely because `new_f1 > old_f1`. This is dangerous because small test sets have high variance.

Robust Logic for Airflow Branching:

1.  Metric Lift: `New Model F1` must beat `Baseline` by a margin (e.g., +2%) to justify the risk of deployment.
2.  Slicing Checks: The new model must not degrade performance on key demographics (e.g., "accuracy improved overall, but dropped 20% for iOS users").
    - _Implementation:_ Your training container should calculate metrics on slices and pass a `bias_report` JSON to XCom.
3.  Shadow Mode (Safe Rollout):
    - Instead of `mlflow.transition_model_version_stage(..., "Production")`, transition to "Shadow".
    - A separate system serves live traffic to _both_ models but returns the "Production" result to the user.
    - After 24h, an Airflow DAG analyzes the "Shadow" logs. If no errors/latency spikes, it promotes to "Production".

---

## 4. Monitoring & Feedback Loops

_How to close the loop._

### The "Ground Truth" Lag

- Immediate: You know the input (Features) and the output (Prediction). You can monitor Data Drift immediately.
- Delayed: You don't know if the prediction was _right_ (e.g., did they click the ad? Did the loan default?).
- Pattern:
  - Ingest DAG: Joins `Prediction_Logs` (from inference) with `Actuals` (from app DB) once the lag window passes (e.g., 7 days for attribution).
  - Evaluation DAG: Computes "Production Accuracy" on this joined dataset. This is the real trigger for retraining.

### Logging for Retraining

- Anti-Pattern: Training on raw DB tables.
- Best Practice: Feature Store.
  - At inference time, log the _exact feature vector_ used to make the prediction.
  - Retraining uses these logged vectors + outcome labels. This guarantees Training-Serving Consistency (avoiding the "I processed data differently in Airflow than in the API" bug).

---

## 5. Summary of Best Practices (The "Golden Path")

1.  Artifact Lineage: Every model in MLflow must link back to the Dataset Snapshot used to train it. (Use DVC).
2.  Immutability: Never overwrite a model version. Always increment.
3.  Container Decoupling:
    - Airflow handles _orchestration_ (Retries, SLAs, Dependencies).
    - Docker handles _environment_ (Python, Cuda, Libraries).
    - MLflow handles _metadata_ (Parameters, Metrics, Artifacts).
4.  Fail Safe: If the "Retraining DAG" fails, the old model stays in production. Ensure your inference service falls back gracefully to the "Last Known Good" version.

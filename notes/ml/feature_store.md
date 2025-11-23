# Feature Stores

A Feature Store is essentially a dual-database system designed to solve one specific problem: preventing "training-serving skew" (where the data you train on looks different from the data you predict on).

Here is the breakdown of your questions and the best practices for the architecture you proposed.

### 1\. Is a Feature Store included in MLflow?

Sort of, but mostly no.

- Open Source MLflow: Does not have a built-in feature store server. It has a client library (`mlflow.feature_store`) that allows you to _connect_ to other feature stores (like Feast or Tecton), but it doesn't store the features itself.
- Databricks MLflow: If you are using the hosted version on Databricks, yes, it has a fully integrated Feature Store that works natively with MLflow.

If you are running your own containerized ML experiments service, you typically need to pick a separate tool for this (like Feast, Tecton) and just use MLflow to track which features were used.

### 2\. Walkthrough: The "Dual Database" Concept

A feature store is not just "a place to put data." It splits your data into two places automatically:

1.  Offline Store (High Latency, Huge Scale):

    - What it is: Usually just tables in Snowflake.
    - Use Case: Training models.
    - Key Feature: "Time Travel." When you ask for "User 123's clicks," it doesn't give you their clicks _today_; it gives you their clicks _as of the moment the training label was created_ (e.g., last month). This prevents data leakage.

2.  Online Store (Low Latency, Recent Data):

    - What it is: A fast key-value store (like Redis or DynamoDB).
    - Use Case: Real-time prediction.
    - Key Feature: Speed. When your app asks "What is User 123's click count?", it returns the answer in \<10ms.

---

### 3. Proposed Workflow

#### The "Modern Data Stack" ML Pattern

Step 1: Feature Engineering (dbt)

- You write SQL in dbt to calculate features (e.g., `avg_order_value_7d`).
- dbt materializes this as a table in Snowflake. This Table IS your Offline Feature Store.
- _Best Practice:_ Tag these dbt models specifically (e.g., `+tags: ["feature_store"]`) so you can track them.

Step 2: Training (The "Point-in-Time" Join)

- Your training container connects directly to Snowflake.
- Crucial Step: You don't just `SELECT *`. You provide a "spine" (a list of UserIDs and Timestamp of when the event happened).
- The Feature Store logic performs an ASOF JOIN (or "point-in-time" join) to grab the feature values _as they existed at that timestamp_.
- _Why?_ If you train on `current_address`, but the user moved yesterday, your model learns the wrong correlation for a fraud event that happened last week.

Step 3: Serving (The Fork)

- Batch Prediction: If you predict overnight, just read from Snowflake. You are done.
- Real-time Prediction: If you need live scoring, you need a "Sync Job" (often orchestrated by Airflow) that pushes the _latest_ values from the dbt table in Snowflake into Redis (Online Store).

---

### Summary of Best Practices

| Phase       | Best Practice                                                                                                                                                                                                                     |
| :---------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Generation  | Do it in dbt. Don't write Python feature code inside your Airflow tasks. SQL is more stable and easier to test for data engineering teams.                                                                                        |
| Storage     | Don't duplicate data. Use Snowflake tables as your Offline Store. Only sync to Redis/Online Store if you have a strict \<100ms API latency requirement.                                                                           |
| Consistency | Use a Registry. Even if you don't use a fancy tool like Tecton, maintain a `feature_definitions.yaml` file. It maps `feature_name` -\> `dbt_model.column`. Your training code should read this config, not hardcoded SQL strings. |
| MLflow      | Log the Definition, not the Data. In MLflow, don't log the dataset. Log the _list of feature names_ and the _commit hash_ of the dbt repo used to generate them.                                                                  |

## DVC

DVC is not a feature store. With Snowflake + dbt`, you probably do not need DVC.

### 1\. What DVC actually does (and why it fights Snowflake)

DVC (Data Version Control) is essentially "Git for files." It works by replacing a large file (e.g., `training_data.csv`) with a small metadata file (`training_data.dvc`) that Git tracks.

- The Workflow DVC wants: You dump your data to a file (CSV/Parquet) -> DVC hashes it -> DVC pushes the file to S3.
- Your Workflow (Snowflake): Your data is already in a governed, versioned warehouse.
- The Conflict: To use DVC, you would have to export your clean Snowflake tables out to S3 as files just to "version" them. This is slow, expensive, and redundant.

### 2\. The Better Approach: "Warehouse-Native" Lineage

Since you are using dbt and Snowflake, you can achieve "Git-like" tracking of your training data without DVC by using Snowflake's native features combined with MLflow.

The Strategy: Zero-Copy Cloning (or Time Travel)
Instead of creating a `.dvc` file, you create a static "snapshot" of your table inside Snowflake at the exact moment of training.

#### The Workflow

1.  Airflow Trigger: The retraining DAG starts.
2.  Snapshot: Airflow executes a Snowflake query to create a clone of your training table.
    ```sql
    CREATE TABLE training_db.snapshots.train_data_2023_10_27
    CLONE training_db.gold.features_table;
    ```
    _(Note: In Snowflake, clones are "Zero-Copy"—they cost almost nothing in storage until the data changes.)_
3.  Train: Your container connects to Snowflake and reads `train_data_2023_10_27`.
4.  Log to MLflow: Instead of logging a git hash of a file, you log the Table Name as a parameter.
    ```python
    mlflow.log_param("training_table", "training_db.snapshots.train_data_2023_10_27")
    mlflow.log_param("dbt_version", "v1.4.2") # From your git repo
    ```

Result: You have perfect reproducibility. If you need to debug a model from 6 months ago, the table `train_data_2023_10_27` still exists (or can be restored) and contains the exact rows used.

---

### 3\. Do you need Feast?

Feast is a different tool for a different problem.

| Feature Store (Feast/Tecton)                                                              | Warehouse (Snowflake/dbt)                         |
| :---------------------------------------------------------------------------------------- | :------------------------------------------------ |
| Primary Goal: \<50ms latency for online serving.                                          | Primary Goal: High-throughput batch training.     |
| Storage: Redis / DynamoDB.                                                                | Storage: Columnar Storage.                        |
| Use Case: An app needs to know "User 123's last 5 clicks" _right now_ to recommend an ad. | Use Case: You are retraining the model overnight. |

The Verdict:

- Keep strictly Snowflake if your model pre-calculates recommendations in batch (e.g., "Email these 10 users tomorrow").
- Add Feast if your model needs to react to live user events in real-time (e.g., "User just clicked X, update their recommendation Y immediately").

### 4\. Summary: The Stack "Cheat Sheet"

| Requirement          | Recommended Tool  | Why?                                                    |
| :------------------- | :---------------- | :------------------------------------------------------ |
| Tracking Code        | Git               | Standard practice.                                      |
| Tracking Experiments | MLflow            | Tracks metrics, params, and artifacts.                  |
| Creating Features    | dbt               | Handles SQL logic, testing, and documentation.          |
| Versioning Data      | Snowflake Clones  | Cheaper/faster than DVC for warehouse-native teams.     |
| Serving Features     | Snowflake (Batch) | Only add Feast if you have a real-time API requirement. |

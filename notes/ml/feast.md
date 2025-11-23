# Feast

Feast (Feature Store) is an open-source feature store that helps teams operate production ML systems at scale by allowing them to define, manage, validate, and serve features for production AI/ML.

At its core, Feast is a specialized "Sync Engine" that solves one specific physics problem: getting feature data into something like Redis because your primary offline data store (Snowflake) is typically too slow for user-facing requests.

The Core Problem:

- Your API's Requirement: "I need to return a prediction in 50ms so the user doesn't wait."
- Snowflake's Reality: "I need 2–5 seconds to spin up a warehouse, scan a micro-partition, and return a row."

### 1. The "Why": What problem is Feast actually solving?

You might look at your current setup (dbt + Snowflake) and think, _"I already have features in tables. Why do I need another tool?"_

Feast solves exactly one hard problem: Latency at Inference Time.

- Without Feast: Your model is live behind an API. A user clicks "checkout." You need to calculate `fraud_score`. To do this, you need their `last_50_transactions_avg`. Querying Snowflake for this takes 2-5 seconds. The user leaves.
- With Feast: Feast automatically syncs that `last_50_transactions_avg` from Snowflake into Redis (or DynamoDB). The API queries Redis and gets the value in 5 milliseconds.

If you do not have a real-time inference requirement (latency \< 100ms), you generally do not need Feast.

---

### 2. Feast Architecture: The "Dual-Store" Concept

Feast does not compute features (dbt does that). Feast acts as the _transport layer_ to move features from your warehouse to your app.

1.  Offline Store (Snowflake): This is your "Source of Truth." It holds petabytes of history. You use this for Training models (because you need history).
2.  Online Store (Redis/DynamoDB): This is your "Cache." It holds _only the latest value_ for each user. You use this for Serving predictions.
3.  The Registry: A file (`registry.db` or S3 object) that maps feature names ("user_age") to their physical location (Snowflake Table X, Column Y).

---

### 3. The Workflow: From dbt to Production

Here is the step-by-step lifecycle of a feature using Feast in your environment.

#### Step 1: Create the Feature (dbt)

You write a dbt model `features_user_stats.sql`. It outputs a table in Snowflake:

```sql
-- Snowflake Table: ANALYTICS.FEATURES.USER_STATS
| user_id | avg_spend_30d | last_login_time | event_timestamp |
|---------|---------------|-----------------|-----------------|
| 101     | 50.25         | 10:00:00        | 10:00:00        |
```

- Requirement: You MUST have an `event_timestamp` column. Feast relies on this for "Point-in-Time" correctness.

#### Step 2: Register the Feature (Feast Python Repo)

In your repo, you define a `FeatureView` that points to that Snowflake table.

```python
from feast import FeatureView, Entity, SnowflakeSource, Field
from feast.types import Float32, String

# 1. Define the Entity (Primary Key)
user = Entity(name="user", join_keys=["user_id"])

# 2. Point to the dbt Table
user_stats_source = SnowflakeSource(
    database="ANALYTICS",
    schema="FEATURES",
    table="USER_STATS",
    timestamp_field="event_timestamp"
)

# 3. Define the View
user_stats_fv = FeatureView(
    name="user_stats",
    entities=[user],
    ttl=timedelta(days=30),  # Only look back 30 days
    schema=[
        Field(name="avg_spend_30d", dtype=Float32),
        Field(name="last_login_time", dtype=String),
    ],
    source=user_stats_source,
)
```

#### Step 3: Apply (CI/CD)

You run `feast apply`.

- Feast updates its Registry.
- It configures Snowflake and Redis (creating necessary schemas if they don't exist).

#### Step 4: Training (The Offline Path)

In your Airflow training DAG, you ask Feast for training data.

- Magic: You provide a list of Users + Timestamps. Feast writes a SQL query that goes to Snowflake and does a Point-in-Time Join (Asof Join).
- _Why this matters:_ It guarantees that for a training row dated "Jan 1st", the model _only_ sees data that existed on "Jan 1st", preventing data leakage.

#### Step 5: Materialization (The Airflow Sync)

This is the critical operational piece. You set up an Airflow task that runs periodically (e.g., hourly):

```bash
feast materialize-incremental 2024-01-01T00:00:00
```

- Feast asks Snowflake: "Give me all rows that changed since the last run."
- Feast pushes those new values into Redis.

#### Step 6: Prediction (The Online Path)

Your model service (FastAPI/Flask) receives a request for User 101.

```python
features = store.get_online_features(
    features=["user_stats:avg_spend_30d"],
    entity_rows=[{"user_id": "101"}]
)
# Returns: {'avg_spend_30d': 50.25} in 5ms
```

---

### 4. Production Best Practices & Gotchas

#### A. The "Materialization Lag" Gotcha

- Scenario: dbt runs at 1:00 AM. `feast materialize` runs at 1:30 AM.
- Risk: Between 1:00 and 1:30, your Snowflake data is fresh, but your Redis data is stale.
- Fix: Use Airflow to trigger `feast materialize` _immediately_ after the dbt job finishes, rather than on a separate rigid schedule.

#### B. Cost Management (Redis is Expensive)

- Risk: Developers define a TTL (Time To Live) of "Infinite" or add massive text features to the online store.
- Best Practice:
  1.  Only materialize features needed for _online_ inference.
  2.  Set aggressive TTLs (e.g., if the model only cares about the last 24h of clicks, don't store 30 days in Redis).
  3.  Use `Entity` types to filter. Don't sync "Guest Users" to Redis if you only predict for "Subscribers."

#### C. The "Repo" Structure

Treat your feature registry like code.

- Repo Structure:
  ```text
  /my_feature_repo
    /features
       user_features.py
       item_features.py
    feature_store.yaml
  ```
- Workflow: Data Scientists open a PR to add a feature file. CI runs `feast plan` (like Terraform plan) to show what will change. Merge to main triggers `feast apply`.

#### D. dbt Integration

- Don't write SQL inside Feast definitions. It makes lineage impossible to track.
- Do create a specific layer in dbt (e.g., `analytics.features.*`) specifically for Feast consumption.
- Do use dbt tags (`tags: ["feast"]`) so you can run `dbt run --select tag:feast` before materialization.

### Summary: Do you need it?

1.  YES, if: You have a user-facing app that needs to make decisions in \<100ms using historical data (e.g., "Is this credit card transaction fraudulent?" or "Customize this homepage based on last week's clicks").

2.  NO, if: You are doing batch predictions (e.g., "Email these 10k users a coupon tonight"). In this case, just read directly from Snowflake using the Offline Store API (or just SQL). You don't need the complexity of Redis and Materialization.

## Deployment

You can run Feast in two modes: "SDK Mode" (easier, no extra server) or "Service Mode" (standard production setup).

Here is the breakdown of how it actually runs in your infrastructure.

---

### Option 1: SDK Mode (The "Library" Approach)

_Best for: Getting started, smaller teams, lower complexity._

In this mode, Feast is just a Python package (`uv add feast`) that you install inside your existing API service. There is no separate "Feast Server" running 24/7.

1.  Your API (Inference Service): You import the Feast SDK code directly into your Flask/FastAPI app.
2.  The Connection: Your API connects directly to Redis (Online Store) to fetch features.
3.  The Registry: Your API reads a `registry.db` file (usually stored in S3) on startup to know which Redis keys map to which features.

Pros: No new Kubernetes services to manage.

Cons: Your API is now tightly coupled to Redis. If you change Redis credentials or network rules, you have to redeploy your ML model service.

### Option 2: Service Mode (The "Feature Server" Approach)

_Best for: Large scale, multiple teams, strict security._

In this mode, you deploy a separate Feast Feature Server (using the official Helm chart). This is a lightweight Python/Go HTTP server that runs 24/7.

1.  Feast Server: It sits in front of Redis. It handles all the connections, authentication, and decoding.
2.  Your API: It makes a simple HTTP request (`POST /get-online-features`) to the Feast Server. It knows nothing about Redis.

Pros: Decoupling. You can swap Redis for DynamoDB without touching your ML model code.
Cons: You have to manage a Deployment/Service in Kubernetes.

---

### The Architecture Visualization

### The "Hidden" Component: The Registry

Regardless of which mode you choose, you need a place to store the Registry.

- What it is: A central file (or DB table) that defines "What features exist."
- Where it lives: In production, do not use a local file. Point Feast to an S3 Bucket (e.g., `s3://my-corp-ml-registry/`) or a PostgreSQL table.
- Why: Airflow (the writer) needs to update it, and your API (the reader) needs to read it. They use S3 as the handover point.

---

### Your Airflow Role: The "Heartbeat"

Airflow is the engine that moves data into the system.

You will have one main DAG that runs continuously (or hourly).

The Script (`sync_features.py`):

```python
from feast import FeatureStore
import datetime

# 1. Connect to the S3 Registry
store = FeatureStore(repo_path="s3://my-bucket/feature_repo/")

# 2. Trigger Materialization
# This tells Feast: "Go to Snowflake, find new rows since yesterday,
# and push them into Redis."
store.materialize_incremental(end_date=datetime.datetime.now())
```

The Airflow DAG:

- Task: `KubernetesPodOperator` running a container with `feast` installed.
- Command: `python sync_features.py`
- Schedule: Matches your data freshness requirement (e.g., every 15 mins).

### Summary: How to Start

1.  Day 1 (SDK Mode):

    - `pip install feast` in your API container.
    - Configure `feature_store.yaml` to point to S3 (registry) and Redis (online).
    - Create an Airflow DAG to run `feast materialize-incremental`.
    - Result: You are in production with no extra servers.

2.  Day 100 (Service Mode):

    - You notice your API pods are consuming too much memory maintaining Redis connections.
    - You deploy the Feast Helm Chart to your cluster.
    - You change your API code to hit `http://feast-server` instead of Redis.

## Production Flow

### 1\. What does the data look like in Redis?

The data in Redis is optimized for speed, so it doesn't look like a SQL table or a JSON object.

If you inspected Redis, you wouldn't see readable columns. You would see something like this:

| Component  | What it looks like (Simplified)                                         |
| :--------- | :---------------------------------------------------------------------- |
| Redis Key  | `\x02user_101` (Binary prefix + Entity ID)                              |
| Redis Type | `HASH`                                                                  |
| Fields     | `_ts:article_recs` (Timestamp), `f28a:avg_clicks` (Hashed Feature Name) |
| Values     | `\x08\x96\x01` (Protocol Buffer Binary)                                 |

Why this mess instead of JSON?

- Speed: Parsing JSON takes CPU time. Protocol Buffers (Protobuf) are binary, so they are instant to read.
- Networking: Fetching 20 separate keys is slow. Feast stores features from the same "Feature View" together so it can grab them all in a single HMGET (Hash Multi-Get) command. This is how it achieves 1-3ms latency.

### 2\. The Production Workflow (The "Request Loop")

Your description of the flow is 100% correct. Here is the standard architecture diagram for that request:

Step-by-Step Walkthrough:

1.  The Trigger: User lands on the homepage.
2.  The Request: Frontend calls your API:
    - `POST /recommendations`
    - Payload: `{ "user_id": "101", "current_location": "NY", "device": "mobile" }`
    - Pass whatever context here that can increase accuracy and performance of the ML model
3.  The Fetch (Feast SDK):
    - Your API code says: _"I have User 101. Give me their history."_
    - ```python
        # This takes ~5ms
        features = store.get_online_features(
            features=["user_stats:clicks_7d", "user_stats:favorite_category"],
            entity_rows=[{"user_id": "101"}]
        ).to_dict()
      ```
4.  The Merge (Crucial Step):
    - Your API now has two types of data:
      - Context Features (from Feast): `clicks_7d=50`, `favorite_category=tech` (Historical context).
      - Request Features (from Frontend): `location=NY`, `device=mobile` (Current context).
    - It merges these into a single vector: `[50, "tech", "NY", "mobile"]`.
5.  The Inference:
    - The API passes this vector to your ML model (e.g., `model.predict()`).
6.  The Response:
    - The model returns `["Article_A", "Article_B"]`.
    - Your API sends this JSON back to the frontend.

### 3\. Key Takeaway: "Request Data" vs "Feature Store Data"

A common "Gotcha" here is thinking Feast handles _everything_.

- Feast handles "What happened yesterday?" (User history, stored in Redis).
- You handle "What is happening now?" (Current location, session token, passed by Frontend).

Your model usually needs both.

Best Practice:

When defining your model in training, explicitly separate these.

```python
# In your model training script
features = [
    "user_stats:clicks_7d",      # From Feast
    "user_stats:fav_category",   # From Feast
    "request:current_location"   # From Request (Feast can define this as 'RequestSource')
]
```

Feast has a concept called `RequestSource` that allows you to define inputs that _don't_ come from Redis but are expected to be passed by the API at runtime. This keeps your training and serving code identical.

from datetime import datetime, timezone

import pandas as pd

# neither of these 2 worked, they get saved into snowflake as unix epoch timestamps
# so the timestamp field in the database needs to be a number instead of a timestamp
# now = datetime.now()
# now = datetime.now(timezone.utc)

now = datetime.now().isoformat()

data = pd.DataFrame(
    data={
        "id": [1, 2, 3, 4, 5],
        "price": [10.99, 22.21, 34.99, 50.00, 69.99],
        "store_id": [1, 1, 1, 3, 4],
        "created_at": [now, now, now, now, now],
    }
)

data.to_parquet("s3://jyablonski-nba-elt-prod/test_table/try3.parquet")
data.to_csv("s3://jyablonski-nba-elt-prod/test_table_csv/try6.csv", index=False)
data.to_json(
    "s3://jyablonski-nba-elt-prod/test_table_json/try7.json",
    orient="records",
    index=False,
)

# this doesnt error it out
data = data.drop(columns=["store_id"])
data.to_csv("s3://jyablonski-nba-elt-prod/test_table_csv/try7.csv", index=False)

# this doesnt error it out
data["test"] = "DATASET_1"
data.to_csv("s3://jyablonski-nba-elt-prod/test_table_csv/try11.csv", index=False)

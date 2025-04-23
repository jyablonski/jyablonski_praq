from datetime import datetime

import pandas as pd

# neither of these 2 worked, they get saved into snowflake as unix epoch timestamps
# so the timestamp field in the database needs to be a number instead of a timestamp
# now = datetime.now()
# now = datetime.now(timezone.utc)
date = datetime.now().date()

now1 = datetime.now().isoformat()
data1 = pd.DataFrame(
    data={
        "id": [1, 2, 3],
        "price": [10.99, 22.21, 34.99],
        "store_id": [1, 2, 3],
        "created_at": [now1, now1, now1],
    }
)
data1.to_parquet(
    f"s3://jyablonski-nba-elt-prod/snowflake_table_loading/month=01/data1-{date}.parquet"
)

now2 = datetime.now().isoformat()
data2 = pd.DataFrame(
    data={
        "id": [4, 5, 6],
        "price": [10.99, 22.21, 34.99],
        "store_id": [1, 2, 4],
        "created_at": [now2, now2, now2],
    }
)
data2.to_parquet(
    f"s3://jyablonski-nba-elt-prod/snowflake_table_loading/month=01/data2-{date}.parquet"
)

# record 3: 10:99 -> 13.99
# record 4: 22.21 -> 25.99
now3 = datetime.now().isoformat()
data3 = pd.DataFrame(
    data={
        "id": [3, 4, 7],
        "price": [13.99, 25.99, 34.99],
        "store_id": [3, 1, 4],
        "created_at": [now3, now3, now3],
    }
)
data3.to_parquet(
    f"s3://jyablonski-nba-elt-prod/snowflake_table_loading/month=01/data3-{date}.parquet"
)

from datetime import datetime

import polars as pl

df = pl.DataFrame(
    {
        "id": [1, 2, 3, 4, 5],
        "sale_price": [4.0, 5.0, 6.0, 7.0, 8.0],
        "color": ["red", "red", "green", "blue", "green"],
        "created_at": [
            datetime(2022, 1, 1),
            datetime(2022, 1, 2),
            datetime(2022, 1, 3),
            datetime(2022, 1, 4),
            datetime(2022, 1, 5),
        ],
    }
)

print(df)

#
print(df.dtypes)

# basic filtering
# filter id == 1 or all records between jan 4 and jan 5 2022, inclusive
df_filtered = df.filter(
    (pl.col("id") == 1)
    | pl.col("created_at").is_between(datetime(2022, 1, 4), datetime(2022, 1, 5))
)

print(df_filtered)

# grouping
grouped_df = df.group_by("color").agg(
    pl.col("sale_price").mean().alias("color_avg_sale_price")
)

print(grouped_df)

# joins
df_for_joins = pl.DataFrame(
    {
        "id": [1, 2, 3, 4, 5],
        "origin": ["US", "US", "Mexico", "Canada", "France"],
    }
)

# this is really weird - you cant inner join if the 2 dfs dont have exactly the same amount of rows?
df_joined = df.join(df_for_joins, on="id", how="inner")
df_joined = df.join(df_for_joins, on="id", how="outer")

print(df_joined)

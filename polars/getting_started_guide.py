from datetime import date, datetime, timezone

import numpy as np
import polars as pl
import s3fs

# int / aggregations
s = pl.Series("a", [1, 2, 3, 4, 5])
print(s)
print(s[0])

print(s.min())
print(s.max())

# string objects
s = pl.Series("a", ["polar", "bear", "arctic", "polar fox", "polar bear"])
s2 = s.str.replace("polar", "pola")
print(s2)

# date objects
start = date(2001, 1, 1)
stop = date(2001, 1, 9)
s = pl.date_range(start, stop, interval="2d", eager=True)
print(s.dt.day())
print(s)

# dataframe objects
df = pl.DataFrame(
    {
        "integer": [1, 2, 3, 4, 5],
        "date": [
            datetime(2022, 1, 1),
            datetime(2022, 1, 2),
            datetime(2022, 1, 3),
            datetime(2022, 1, 4),
            datetime(2022, 1, 5),
        ],
        "float": [4.0, 5.0, 6.0, 7.0, 8.0],
    }
)

print(df)
print(df.head(3))
print(df.sample(2))
print(df.describe())

# writing data
## csv
df.write_csv("output.csv")
df2 = pl.read_csv("output.csv", try_parse_dates=True)

## json
df.write_json("output.json")
df_json = pl.read_json("output.json")

## parquet
df.write_parquet("output.parquet")
df_parquet = pl.read_parquet("output.parquet")

# selecting columns
df.select(pl.col("*"))
df.select(pl.col("integer"))
df.select(pl.col("integer")).limit(3)
df.select(pl.exclude("float"))

# filtering
df.filter(
    pl.col("date").is_between(datetime(2022, 1, 1), datetime(2022, 1, 3)),
)

df.filter((pl.col("float") <= 5) & (pl.col("float").is_not_nan()))

# creating new column
df.with_columns(
    pl.col("float").sum().alias("e"), (pl.col("integer") + 42).alias("b+42")
)


# group by
df2 = pl.DataFrame(
    {
        "x": np.arange(0, 8),
        "y": ["A", "A", "A", "B", "B", "C", "X", "X"],
    }
)
df2.group_by("y", maintain_order=True).count()
df2.group_by("y", maintain_order=True).agg(
    pl.col("*").count().alias("count"),
    pl.col("*").sum().alias("sum"),
)

# joins
df = pl.DataFrame(
    {
        "a": np.arange(0, 8),
        "b": np.random.rand(8),
        "d": [1, 2.0, np.NaN, np.NaN, 0, -5, -42, None],
    }
)

df2 = pl.DataFrame(
    {
        "x": np.arange(0, 8),
        "y": ["A", "A", "A", "B", "B", "C", "X", "X"],
    }
)
joined = df.join(df2, left_on="a", right_on="x")
print(joined)

# union
stacked = df.hstack(df2)
print(stacked)


# s3
df = pl.DataFrame(
    {
        "foo": ["a", "b", "c", "d", "d"],
        "bar": [1, 2, 3, 4, 5],
    }
)

fs = s3fs.S3FileSystem()
destination = "s3://jyablonski-test-bucket123/polars/my_file.parquet"

# write parquet
with fs.open(destination, mode="wb") as f:
    df.write_parquet(f)

import os

import polars as pl
import s3fs

# https://docs.pola.rs/user-guide/io/cloud-storage/
# read parquet
df = pl.read_parquet(
    "s3://jyablonski-nba-elt-prod/reddit_comment_data/validated/year=2024/month=02/reddit_comment_data-2024-02-27.parquet"
)

fs = s3fs.S3FileSystem()
destination = "s3://jyablonski97-dev/my_file.parquet"

# write parquet
with fs.open(destination, mode="wb") as f:
    df.write_parquet(f)

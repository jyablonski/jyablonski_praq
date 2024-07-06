from datetime import datetime
import os

import polars as pl
import s3fs

# poetry add connectorx
uri = f"postgresql://{os.environ.get('RDS_USER')}:{os.environ.get('RDS_PW')}@{os.environ.get('IP')}:5432/jacob_db"
query = "SELECT * FROM nba_prod.player_stats"

# read from database
df = pl.read_database_uri(query=query, uri=uri)

df2 = (
    df.group_by(pl.col("team"))
    .agg(pl.col("avg_mvp_score").mean().alias("team_avg_mvp_score"))
    .sort("team_avg_mvp_score", descending=True)
    .with_columns(
        team_avg_mvp_rank=pl.col("team_avg_mvp_score").rank(descending=True),
        scrape_ts=datetime.now(),
    )
)

df2

fs = s3fs.S3FileSystem()
destination = f"s3://jyablonski97-dev/polars-test-{datetime.now().date()}.parquet"

# write parquet
with fs.open(destination, mode="wb") as f:
    df2.write_parquet(f)

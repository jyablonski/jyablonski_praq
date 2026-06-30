from datetime import datetime
import os

import polars as pl
import s3fs

# poetry add connectorx
uri = f"postgresql://{os.environ.get('RDS_USER')}:{os.environ.get('RDS_PW')}@{os.environ.get('IP')}:17841/jacob_db"
query = "SELECT * FROM fact.fact_boxscores"

# read from database
df = pl.read_database_uri(query=query, uri=uri)

player_test = (
    df.filter(pl.col("game_date") <= pl.lit("2025-04-14").str.strptime(pl.Date))
    .with_columns(
        pl.col("game_date")
        .rank(method="dense", descending=False)
        .over("player")
        .alias("row_number")
    )
    .filter(pl.col("player") == pl.lit("Stephen Curry"))
    .sort(pl.col("game_date"))
)

lazy_df = df.lazy()
lazy_fg_aggs = (
    lazy_df.filter(pl.col("game_date") <= pl.lit("2025-04-14").str.strptime(pl.Date))
    .with_columns(
        pl.col("game_date")
        .rank(method="dense", descending=False)
        .over("player")
        .alias("row_number")
    )
    .group_by("player")
    .agg(
        [
            pl.col("fgpercent").mean().alias("avg_fg_percent"),
            pl.len().alias("games_played"),
        ]
    )
    .filter(pl.col("games_played") >= 70)
    .sort("avg_fg_percent", descending=True)
    .with_columns(
        [
            pl.col("avg_fg_percent").rank(descending=True).alias("fg_percent_rank"),
            pl.lit(datetime.now()).alias("scrape_ts"),
        ]
    )
)

lazy_fg_aggs.explain()
lazy_fg_aggs.show_graph(plan_stage="physical", engine="streaming")

fg_aggs_df = lazy_fg_aggs.collect(engine="streaming")

fs = s3fs.S3FileSystem()
destination = f"s3://jyablonski97-dev/polars-test-{datetime.now().date()}.parquet"

# write parquet
with fs.open(destination, mode="wb") as f:
    fg_aggs_df.write_parquet(f)

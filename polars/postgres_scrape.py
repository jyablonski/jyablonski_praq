from datetime import datetime
import os

import polars as pl

# poetry add connectorx
uri = f"postgresql://{os.environ.get('RDS_USER')}:{os.environ.get('RDS_PW')}@{os.environ.get('IP')}:5432/jacob_db"
query = "SELECT * FROM nba_prod.feature_flags"
scrape_time = datetime.now()

# read from database
df = pl.read_database_uri(query=query, uri=uri)
df2 = df.with_columns(
    new_column=pl.lit("hello world"),
    id_doubled=pl.col("id") * 2,
    bool_test=pl.when((pl.col("id") * 2) > 25).then(True).otherwise(False),
    scrape_ts=scrape_time,
)
print(df2)

# write back to database
df2.write_database(
    table_name="polars_test",
    connection=uri,
    if_exists="replace",
)

ctx = pl.SQLContext(frame=df2)

df3 = ctx.execute(
    """
    select *
    from frame
    limit 5;"""
)

df3.show_graph()

df3_data = df3.collect()

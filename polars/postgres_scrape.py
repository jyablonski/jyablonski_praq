import os

import polars as pl

# poetry add connectorx
uri = f"postgresql://{os.environ.get('RDS_USER')}:{os.environ.get('RDS_PW')}@{os.environ.get('IP')}:5432/jacob_db"
query = "SELECT * FROM nba_prod.feature_flags"

df = pl.read_database_uri(query=query, uri=uri)

print(df)

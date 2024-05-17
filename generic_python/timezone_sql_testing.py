from datetime import datetime, timedelta, timezone
import os

import pandas as pd
from jyablonski_common_modules.sql import sql_connection, write_to_sql

engine = sql_connection(
    database=os.environ.get("RDS_DB"),
    schema="public",
    user=os.environ.get("RDS_USER"),
    pw=os.environ.get("RDS_PW"),
    host=os.environ.get("IP"),
)

now = datetime.now()
now_utc = datetime.now(timezone.utc)

df = pd.DataFrame(
    data={
        "id": [1, 2, 3],
        # this is `timestamp_no_tz - datetime64[ns]`
        "timestamp_no_tz": [now, now, now],
        # and the utc one is `timestamp_utc - datetime64[ns, UTC]`
        "timestamp_utc": [now_utc, now_utc, now_utc],
    }
)

# created a table like this
# CREATE TABLE "public.timestamp_test" (
# 	id int8 NULL,
# 	timestamp_no_tz timestamp NULL,
# 	timestamp_utc timestamptz NULL
# );
with engine.begin() as connection:
    write_to_sql(con=connection, table="timestamp_test", df=df, table_type="replace")

# same exact types + data is read in fine
with engine.begin() as connection:
    df2 = pd.read_sql("SELECT * FROM timestamp_test", connection)

import os

import duckdb

from duck_db.utils import setup_postgres

con = duckdb.connect(database=":memory:", read_only=False)
setup_postgres(
    conn=con,
    username=os.environ.get("RDS_USER"),
    password=os.environ.get("RDS_PW"),
    host=os.environ.get("IP"),
    database="jacob_db",
)

# can easily read from both csv and parquet files and interact with their data
# in the same query
df = con.execute(
    """\
   select *
   from 'data/missing_users.csv' missing_users
      left join 'data/users.parquet' users
         on missing_users.id = users.id
"""
).fetch_df()

# create a table in duckdb of the data from the csv + parquet files
con.execute(
    f"""\
create or replace table main.load_example as
   select *
   from 'data/missing_users.csv' missing_users
      left join 'data/users.parquet' users
         on missing_users.id = users.id;"""
)

# make sure that table is available in duckdb
con.execute(
    f"""\
   select *
   from main.load_example;"""
).fetch_df()

# create a table in postgres database now
# * IMPORTANT * the database name here comes from the database name passed into
# the `duck_db_alias` parameter in the `setup_postgres` function
con.execute(
    f"""\
create table jacob_db.public.csv_load_test (id integer, name text)"""
)


# insert data from duckdb database transformation into postgres
con.execute(
    f"""\
insert into jacob_db.public.csv_load_test (id, name)
   select
      id,
      name
   from main.load_example;"""
)

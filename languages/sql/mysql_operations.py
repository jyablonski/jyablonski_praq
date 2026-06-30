from datetime import datetime

import mysql.connector
import pandas as pd
from sqlalchemy import create_engine, text

# https://stackoverflow.com/questions/70435792/pandas-mysql-how-to-update-some-columns-of-rows-using-a-dataframe

# mysql connector which is shit
cnx = mysql.connector.connect(
    user="mysqluser", password="mysqlpw", host="127.0.0.1", database="demo"
)
df = pd.read_sql_query(sql="select * from demo.movies;", con=cnx)
df2 = df.query("genres == 'Western'")

# this doesnt work
df2.to_sql(name="movies_test", con=cnx, if_exists="append", index=False)

cnx.close()

# sqlalchemy
connection_string = "mysql+mysqlconnector://mysqluser:mysqlpw@127.0.0.1:3306/demo"
mysql_engine = create_engine(connection_string, echo=True)
connection = mysql_engine.connect()
table = "movies_test"

# this also works
# df = pd.read_sql_query(sql = "select * from demo.movies;", con=mysql_engine)
df = pd.read_sql_query(sql="select * from demo.movies;", con=connection)
df2 = df.query("genres == 'Western'")

# insert new records
results = df2.to_sql(name=table, con=connection, if_exists="append", index=False)
print(f"{results} records inserted into {table}")


# update existing records
# cant get the results returned to see how many rows were affected
sql = "UPDATE movies_test SET release_year = 2023 WHERE genres = 'Western'"
z = connection.execute(sql)

# only keep the pk and the column(s) to update
df2["country"] = "Zimbabwe"
df2 = df2[["id", "country"]]

sql = """
UPDATE movies_test SET country = :country
WHERE id = :id
"""
params = df2.to_dict("records")
connection.execute(text(sql), params)

connection.close()

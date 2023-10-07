from datetime import datetime, timedelta
import uuid

import gspread
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine.base import Connection

# https://docs.gspread.org/en/latest/oauth2.html
# create new project from google developer console
# create new service account from `APIs & Services -> Credentials -> Service Account`
# create a new key for the service account
# share the google sheet with the `client_email` provided in the service account json creds
# enable google sheets api in the project

url = "https://docs.google.com/spreadsheets/d/1TMN5L0cfxQvKQdAHtXJrDbNepBKOJJCNQkC0bq6DdMA"

# creds = {
#   "type": "service_account",
#   "project_id": "z",
#   "private_key_id": "4",
#   "private_key": "-a",
#   "client_email": "d",
#   "client_id": "1b",
#   "auth_uri": "https://accounts.google.com/o/oauth2/auth",
#   "token_uri": "https://oauth2.googleapis.com/token",
#   "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
#   "client_x509_cert_url": "c",
#   "universe_domain": "googleapis.com"
# }
# gc = gspread.service_account_from_dict(creds)


gc = gspread.service_account(
    filename="g_service_creds.json"
)  # do this 1 time and get a saved token forever.
sh = gc.open_by_url(url)

worksheet = sh.get_worksheet(0)

new_records = pd.DataFrame(worksheet.get_all_records())
new_records = new_records.rename(
    columns={
        "Timestamp": "parkResponseDate",
        "What's your favorite color": "parkComment",
    }
)
new_records = new_records.drop("Select an Option", axis=1)
new_records["parkResponseDate"] = pd.to_datetime(new_records["parkResponseDate"])

# dump into mysql
connection_string = "mysql+mysqlconnector://mysqluser:mysqlpw@127.0.0.1:3306/demo"
mysql_engine = create_engine(connection_string, echo=True)
connection = mysql_engine.connect()
table = "movies_test"

# this also works
# df = pd.read_sql_query(sql = "select * from demo.movies;", con=mysql_engine)
df = pd.read_sql_query(sql="select * from demo.movies;", con=connection)
df2 = df.query("genres == 'Western'")

# insert new records
results = df2.to_sql(
    name="movies_test", con=connection, if_exists="replace", index=False
)
print(f"{results} records inserted into {table}")

reviews_json = {
    "postStaySurveyId": [1, 2, 3],
    "machineReviewStatus": ["REJECTED", "NEEDS_HUMAN_REVIEW", "APPROVED"],
    "humanReviewStatus": [None, None, None],
    "campspotResponse": [None, None, None],
    "campspotInternalComment": ["", "", ""],
    "parkResponse": [None, None, None],
    "parkComment": ["", "", ""],
    "viewable": [None, None, None],
    "language": ["eng", "eng", "eng"],
}

reviews = pd.DataFrame(data=reviews_json)
reviews["uuid"] = [str(uuid.uuid4()) for _ in range(len(reviews))]

reviews.to_sql(
    name="PostStaySurveyModeration", con=connection, if_exists="replace", index=False
)

sql_update = """
update PostStaySurveyModeration
set parkComment = :parkComment, parkResponseDate = :parkResponseDate, modified = now()
where uuid = :uuid
"""
params = new_records.to_dict("records")
connection.execute(text(sql_update), params)

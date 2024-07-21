import requests
import numpy as np

# need to convert pyton datetime objects to strings
# and need to fill all missing values with something, otherwise
# you'll get `InvalidJSONError: Out of range float values are not JSON compliant` error
df = df.head(100)

date_formats = {
    "game_date": "%Y-%m-%d",
    "created_at": "%Y-%m-%dT%H:%M:%S",
    "modified_at": "%Y-%m-%dT%H:%M:%S",
}

for column, date_format in date_formats.items():
    df[column] = pd.to_datetime(df[column]).dt.strftime(date_format)

df = df.where(df.notnull(), None)

df_json = df.to_dict(orient="records")

url = "https://api.jyablonski.dev"

response = requests.post(url=url, json=boxscores_json)

response.json()

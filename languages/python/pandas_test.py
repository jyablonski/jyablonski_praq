from datetime import datetime
import pandas as pd

cols = ["col1", "stamp", "timestamp"]
timestamp = datetime.now()

df1 = pd.DataFrame(
    data={
        "col1": [timestamp, timestamp, timestamp],
        "stamp": [timestamp, timestamp, timestamp],
    }
)
df2 = pd.DataFrame(
    data={
        "col1": [timestamp, timestamp, timestamp],
        "stamp": [timestamp, timestamp, timestamp],
        "timestamp": [timestamp, timestamp, timestamp],
    }
)

print(df1)
print(df1.dtypes)

for col in df1.columns:
    if col in cols:
        df1[col] = df1[col].astype(str)

print(df1.dtypes)

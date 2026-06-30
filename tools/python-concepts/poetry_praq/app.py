from datetime import datetime

import pandas as pd

timestamp = datetime.now()

df = pd.DataFrame(data={"col1": [1, 2], "col2": [3, 4]})
df["created_at"] = timestamp

print(f"Hello world df is {len(df)}")
print(df)

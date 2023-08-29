import pandas as pd

df1 = pd.DataFrame(data={"id": [1, 2, 3]})
df2 = pd.DataFrame(data={"id": [2, 3, 4]})

# this returns the rows with id = 2 + 3, as expected
identical_records = pd.merge(df1, df2, on="id")

# mismatch records - indicator adds a column called _merge showing
# which df the row came from (`left_only` or `right_only`)
df3 = df1.merge(df2, on="id", indicator=True, how="outer")

indicator_label = {"left_only": "df1", "right_only": "df2"}
mismatch_records = (
    df3.query('_merge != "both"').copy().rename(columns={"_merge": "origin"})
)
mismatch_records["origin"] = mismatch_records["origin"].map(indicator_label)

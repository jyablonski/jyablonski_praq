import pandas as pd

review_json = {
    "OriginalText": "hello world",
    "Misrepresentation": None,
    "Classification": {
        "ReviewRecommend": False,
        "Category1": {"Score": 0.0605},
        "Category2": {"Score": 0.0605},
        "Category3": {"Score": 0.0605},
    },
    "Language": "eng",
}

df = pd.DataFrame([review_json])

# create a separate dataframe to hold the new columns
classification_data = pd.json_normalize(df["Classification"])

# drop the massive column
df.drop("Classification", axis=1, inplace=True)

# join the new unnested columns back
df = df.join(classification_data)

print(df)

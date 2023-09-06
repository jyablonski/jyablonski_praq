from datetime import datetime, timedelta

import pandas as pd
import numpy as np

df = pd.DataFrame(
    data={
        "id": [1, 2, 3, 4, 5],
        "sales": [100, 200, 300, 0, 700],
        "is_valid": [True, True, False, False, True],
        "review_text": [
            "hellooo world this is a long striiiiiing whssich should have 8 partszzzzz",
            "hii",
            "hii v2",
            "x.",
            "y me",
        ],
    }
)

# set `viewable_status` to 'Approved' When `is_valid` is True,
# otherwise look at the sales column and reject any record that has a value of 0, and if it is not equal to 0 then set it to Needs Review
df["viewable_status"] = np.where(
    df["is_valid"] == True,
    "Approved",
    np.where(df["sales"] == 0, "Rejected", "Needs Review"),
)

len_limit = 10

for index, row in df.iterrows():
    total_len_review_text = len(row["review_text"])

    # split the text up based on the len limit
    if total_len_review_text > len_limit:
        chunks = [
            row["review_text"][i : i + len_limit]
            for i in range(0, total_len_review_text, len_limit)
        ]
        print(f"{len(chunks)} total chunks")

        review_recommended = []
        category_1 = []
        category_2 = []
        category_3 = []

        for review_chunk in chunks:
            # do some processing as usual

            # append
            review_recommended.append(False)
            category_1.append(1)
            category_2.append(1)
            category_3.append(1)
            # finish the processing, then aggregate the results together and take averages

        if True in review_recommended:
            df["review_recommended"] = True
        else:
            df["review_recommended"] = False

        df["category1"] = sum(category_1) / len(category_1)
        df["category2"] = sum(category_2) / len(category_2)
        df["category3"] = sum(category_3) / len(category_3)
    else:
        print(f"less than {len_limit}")

print(df)


ids = [1, 3, 5]


df_filtered = df.query(f"id.isin({ids})")

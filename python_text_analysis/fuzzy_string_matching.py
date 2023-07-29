from thefuzz import fuzz
import pandas as pd

# package seems okay.  depending on the type of string matching you're trying to do there are
# multiple different functions that you can use to get a more accurate match.
# it's still not going to be 100% though; if ever using this in an actual production setting
# you'd need some form of manual QA to comb through this and make sure the matching is doing its job correctly.
# https://stackoverflow.com/questions/16476924/how-to-iterate-over-rows-in-a-dataframe-in-pandas

names_df = pd.DataFrame(
    data={
        "id": [
            1,
            2,
            3,
            4,
        ],
        "name_1": ["Jacob Yablonski", "Terry Lewis", "Marie Obal", "Erin Booster"],
        "name_2": ["Jacob Yablonksi", "Terry Lewsi", "Mary Oble", "Aaron Booster"],
    }
)

# iterate through the rows in the dataframe
names_df["str_match_score"] = [
    fuzz.ratio(x, y) for x, y in zip(names_df["name_1"], names_df["name_2"])
]

names_df["str_match_partial_score"] = [
    fuzz.partial_ratio(x, y) for x, y in zip(names_df["name_1"], names_df["name_2"])
]

print(names_df)

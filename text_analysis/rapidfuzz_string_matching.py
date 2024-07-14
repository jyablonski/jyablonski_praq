import random
import string

import polars as pl
from rapidfuzz import fuzz, utils

# levenshtein distance is a measure of similarity between 2 strings.
# it quantifies the minimum number of single-character edits required
# to change one string into the other

# used in string matching, spell checking etc

# business questions to ask:
# do we want to lowercase everything?
#   will lose caps context - for something like reviews then no.
#   for something like name matching then yes
# do we want to remove non alphanumeric characters (ex !!!)
# pick a threshold to match on (ex everything over 90%), and qa it

# https://github.com/rapidfuzz/RapidFuzz
fuzz.ratio("this is a test", "this is a test!")
fuzz.partial_ratio("this is a test", "this is a test!!!")

fuzz.WRatio(
    "this is a test", "this is a new test!!!", processor=utils.default_process
)  # here "this is a new test!!!" is converted to "this is a new test"

fuzz.WRatio("this is a test", "this is a new test")

# remove non alpha numeric chars
fuzz.QRatio("this is a test", "this is a new test!!!", processor=utils.default_process)
fuzz.QRatio("this is a test", "this is a new test!!!")


df = pl.DataFrame(
    data={
        "id": [1, 2, 3, 4],
        "review_a": [
            "i had a great time",
            "wow this things sucks",
            "i couldnt have done it without you",
            "oh ya baby i love it",
        ],
        "review_b": [
            "i had a great time!!",
            "wow this thing suckss",
            "i couldn't have done it without you",
            "oh ya babyyy i love it",
        ],
    }
)

df = df.with_columns(
    ratio=pl.struct(["review_a", "review_b"]).map_elements(
        lambda x: fuzz.ratio(x["review_a"], x["review_b"])
    ),
    partial_ratio=pl.struct(["review_a", "review_b"]).map_elements(
        lambda x: fuzz.partial_ratio(x["review_a"], x["review_b"])
    ),
    w_ratio=pl.struct(["review_a", "review_b"]).map_elements(
        lambda x: fuzz.WRatio(x["review_a"], x["review_b"])
    ),
    q_ratio=pl.struct(["review_a", "review_b"]).map_elements(
        lambda x: fuzz.QRatio(x["review_a"], x["review_b"])
    ),
)

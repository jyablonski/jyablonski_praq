from thefuzz import fuzz
import polars as pl

# dummy example i built using polars and thefuzz package. should split this out into functions
# so they can be independently tested.

# example data - say we're joining people names + emails on 2 different
# data sources
data = {
    "id": [1, 2, 3, 4, 5, 6],
    "name_1": [
        "Jacob Yablonski",
        "Terry Lewis",
        "Marie Obal",
        "Erin Booster",
        "James Harrison",
        "Erik Lave",
    ],
    "email_1": [
        "jacob.yablonski@example.com",
        "terry.lewis@example.com",
        "marie.obal@example.com",
        "erin.booster@example.com",
        "james.harrison@example.com",
        "erik.lave@example.com",
    ],
    "birthdate_1": [
        "1985-05-15",
        "1990-06-20",
        "1988-03-22",
        "1992-07-10",
        "1983-11-02",
        "1995-01-08",
    ],
    "name_2": [
        "Jacob Yablonksi",
        "Terry Lewsi",
        "Mary Oble",
        "Aaron Booster",
        "James Harrison II",
        "Erik Lave Jr.",
    ],
    "email_2": [
        "jacob.yablonski@example.com",
        "terry.lewis@example.com",
        "mary.oble@example.com",
        "aaron.booster@example.com",
        "james.harrison@example.com",
        "erik.lave@example.com",
    ],
    "birthdate_2": [
        "1985-05-15",
        "1990-06-21",
        "1988-09-23",
        "1992-07-10",
        "1983-11-03",
        "1995-01-09",
    ],
}


match_threshold_pct = 0.75

fuzzy_df = pl.DataFrame(data=data)

# if we get an email match, then use that
email_matches = fuzzy_df.filter(pl.col("email_1") == pl.col("email_2")).with_columns(
    is_match=pl.lit(1)
)

# if we dont get an email match, then let's fuzzy match the name and
# take birthdate into account
# this is slow because we have to use python to map this custom fuzz.ratio function
# to each row in the dataframe, but gotta do what u gotta do
mismatches = (
    fuzzy_df.join(other=email_matches, on=pl.col("id"), how="anti")
    .with_columns(
        pl.struct(["name_1", "name_2"])
        .map_elements(
            lambda x: fuzz.ratio(x["name_1"], x["name_2"]), return_dtype=pl.Int64
        )
        .alias("str_match_score")
    )
    .with_columns(
        is_match=pl.when(
            pl.col("str_match_score") >= match_threshold_pct,
            pl.col("birthdate_1") == pl.col("birthdate_2"),
        )
        .then(1)
        .otherwise(0)
    )
)

# return final df, with the appropriate matches
combined_df = pl.concat(
    [
        email_matches,
        mismatches.drop(
            "str_match_score",
        ),
    ]
)

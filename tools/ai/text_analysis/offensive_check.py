from datetime import datetime, timezone

import polars as pl
from profanity_check import predict, predict_prob

import polars as pl
from text_analysis.data_common import example_reviews

created_now = datetime.now(timezone.utc)
offensive_threshold_pct = 0.25

reviews = pl.DataFrame(data=example_reviews)

# 0.0 means the text is not offensive
# 1.0 means the text is offensive
reviews_scored = reviews.with_columns(
    pl.Series(
        "review_text_score", predict_prob(reviews["review_text"].to_list()).round(3)
    ),
)

# `is_offensive` couldnt be created above for whatever reason, so
# had to create separately
reviews_scored = reviews_scored.with_columns(
    is_offensive=pl.when(pl.col("review_text_score") >= offensive_threshold_pct)
    .then(1)
    .otherwise(0)
)

print(reviews_scored)

# normal useage for the function
text1 = "this product really sucked, was expensive, and fucking broke on me"
res1 = predict([text1])

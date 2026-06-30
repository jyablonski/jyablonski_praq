import pandas as pd
from profanity_check import predict, predict_prob
from better_profanity import profanity

from text_analysis.data_common import example_reviews

profanity.load_censor_words()

df = pd.DataFrame(data=example_reviews)
df["review_length"] = df["review_text"].str.len()

# Convert the column to run profanity filtering on to a list
texts = df["review_text"].tolist()

# use profanity check to classify each review as offensive or not, and provide a score
# you can use these to filter downstream or do whatever you want
df["is_offensive"] = predict(texts)
df["offensive_score"] = predict_prob(texts)


# use better_profanity to censor any bad words
df["filtered_reviews"] = [profanity.censor(review) for review in df["review_text"]]

# add another column to catch potentially offensive content that wasnt censored
df["is_likely_offensive"] = (df["offensive_score"] > 0.3) & (
    df["filtered_reviews"] == df["review_text"]
)

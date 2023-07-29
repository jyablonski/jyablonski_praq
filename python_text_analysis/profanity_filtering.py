from datetime import datetime

from better_profanity import profanity
import pandas as pd

# works as expected.  if doing this in for an actual project you probably want to consider altering the
# profanity wordlist, there's probably things you'd want to change depending on your business / industry
# that full list is here https://github.com/snguyenthanh/better_profanity/blob/master/better_profanity/profanity_wordlist.txt

# the library is outdated and the author recommended to not use version 0.7.0
# pip install better_profanity==0.6.1
profanity.load_censor_words()

text = "You p1ec3 of sHit."
censored_text = profanity.censor(text)

# You p1ec3 of ****.
print(censored_text)

current_timestamp = datetime.now()
reviews = pd.DataFrame(
    data={
        "id": [
            1,
            2,
            3,
            4,
            5,
            6,
        ],
        "raw_review_text": [
            "This product really fucking sucked tbh",
            "Piece of shit broke on me",
            "Screw you dude does this get filtered???",
            "son of a b!tch",  # only this one doesnt get filtered
            "bababayboooybie",
            "she's a bi_tch",
        ],
    }
)
reviews["created_at"] = current_timestamp

reviews["filtered_reviews"] = [profanity.censor(x) for x in reviews["raw_review_text"]]

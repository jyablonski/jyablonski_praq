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

reviews = pd.DataFrame(
    data={
        "id": [
            1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            10,
            11,
            12,
            13,
            14,
            15,
        ],
        "raw_review_text": [
            "This product really fucking sucked tbh",
            "Piece of shit broke on me",
            "Screw you dude does this get filtered???",  # this turns into **** you which kinda looks worse after lol
            "son of a b!tch",  # only this one doesnt get filtered
            "son of a b*tch",
            "bababayboooybie",
            "she's a bi_tch",
            "what about the p0rn",
            "what an ass",
            "he's buttcheeks",
            "sh it ahahaha",
            "sh_it hahahah",
            "shiit hahaha",
            "shiiit hahaha",
            "mothertrucker",
        ],
    }
)
reviews["is_profanity"] = [
    profanity.contains_profanity(review) for review in reviews["raw_review_text"]
]
reviews["filtered_reviews"] = [
    profanity.censor(review) for review in reviews["raw_review_text"]
]
reviews["created_at"] = datetime.now()

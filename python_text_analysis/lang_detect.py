import nltk
import pycountry
from langdetect import detect  # use langdetect for this kind of work.
import pandas as pd

lang_list = [
    "is this written in english",
    "est-ce écrit en anglais",
    "esto esta escrito en ingles",
    "è scritto in inglese?",
]
# lang_list = lang_list[0]

tc = nltk.classify.textcat.TextCat()
guess_one = tc.guess_language(lang_list[0])
guess_two = tc.guess_language(lang_list[1])

guess_one_name = pycountry.languages.get(alpha_3=guess_one).name
guess_two_name = pycountry.languages.get(alpha_3=guess_two).name

for i in lang_list:
    print(f"{i} is labeled to be {detect(i)}")

lang_list_df = pd.DataFrame(lang_list)
lang_list_df = lang_list_df.rename(columns={lang_list_df.columns[0]: "text"})
lang_list_df["detected_lang"] = lang_list_df["text"].apply(
    lambda x: detect(x)
)  # apply the detect function on every row

lang_list_df = lang_list_df.query('detected_lang == "en"')

print(lang_list_df)

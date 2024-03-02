test_string = "hello jacob you shit ass shiit fuck butthole"


class ProfanityFilter:
    def __init__(self, word_list: str = "bad_words.txt"):
        self.vowels = set("aAeEiIoOuU")

        try:
            with open(word_list, "r") as file:
                self.word_set = {line.strip() for line in file}
        except FileNotFoundError:
            raise FileNotFoundError("Word List File was not found or unable to open.")

        if not self.word_set:
            raise ValueError(
                "Input Word Set File is empty.  Please input a valid Word Set File."
            )

    def filter_word(
        self, input_str: str, replace_type: str = "limited", replace_char: str = "*"
    ):
        replace_type = replace_type.lower()
        if replace_type not in ("limited", "full"):
            raise ValueError(
                "Please Select one of `limited` or `full` for replace_type"
            )

        return_string = []
        words = input_str.split(" ")

        for word in words:
            if word.lower() in self.word_set:
                if replace_type == "limited":
                    # Replace vowels with asterisks
                    censored_word = "".join(
                        "*" if c.lower() in "aeiou" else c for c in word
                    )
                else:
                    # Replace the entire word with asterisks
                    censored_word = replace_char * len(word)
                    if len(censored_word) > 4:
                        censored_word = "****"
                return_string.append(censored_word)
            else:
                return_string.append(word)

        return " ".join(return_string)


d = ProfanityFilter()


cleaned_word = d.filter_word(input_str=test_string, replace_type="limited")
cleaned_word = d.filter_word(input_str=test_string, replace_type="full")


import polars as pl


df = pl.DataFrame(
    {
        "id": [1, 2, 3, 4, 5],
        "review": [
            "hello world",
            "shit ass i hate this",
            "fuck this",
            "butthole hello world",
            "yes baby",
        ],
    }
)

df_clean = df.with_columns(pl.col("review").apply(d.filter_word))

for review in df_clean["review"]:
    print(review)

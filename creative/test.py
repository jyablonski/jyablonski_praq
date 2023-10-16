from dataclasses import dataclass, field


def default_profanity_word_list():
    return [
        "ass",
        "bitch",
        "fuck",
        "shit",
    ]


def default_char_mappings_dictionary():
    return {
        "a": ("a", "@", "4"),
        "i": ("i", "1", "x"),
        "o": ("o", 0, "x"),
        "s": ("s", "$", "5"),
        "u": ("u", "v"),
    }


@dataclass
class Profanity:
    profanity_word_list: list[str] = field(default_factory=default_profanity_word_list)
    char_mappings: dict = field(default_factory=default_char_mappings_dictionary)

    def is_profanity(self, words: str):
        if not isinstance(words, str):
            raise TypeError(f"words Input must be a string")

        words_split = words.split()

        for word in words_split:
            if word in self.profanity_word_list:
                return True

        else:
            return False


profanity = Profanity()

yes_list = "hello world does this str contain shit"
no_list = "this is a clean string"

profanity.is_profanity(yes_list)
profanity.is_profanity(no_list)

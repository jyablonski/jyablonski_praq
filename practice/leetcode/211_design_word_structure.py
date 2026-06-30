# Design a data structure that supports adding new words and finding if a string matches any
# previously added string.

# Implement the WordDictionary class:

# WordDictionary() Initializes the object.
# void addWord(word) Adds word to the data structure, it can be matched later.
# bool search(word) Returns true if there is any string in the data structure that matches word or
# false otherwise. word may contain dots '.' where dots can be matched with any letter.

import re


class WordDictionary:
    def __init__(self):
        self.words = set()

    def addWord(self, word: str) -> None:
        if word not in self.words:
            self.words.add(word)

    def search(self, word: str) -> bool:
        # Compile a regular expression pattern from the input word,
        # where '.' matches any single character. Anchoring with ^ and $
        # ensures the entire word must match (not just a substring).
        if "." in word:
            pattern = re.compile(f"^{word}$")
            return any(pattern.fullmatch(w) for w in self.words)
        else:
            return word in self.words

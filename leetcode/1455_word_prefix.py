# Given a sentence that consists of some words separated by a single space,
# and a searchWord, check if searchWord is a prefix of any word in sentence.

# Return the index of the word in sentence (1-indexed) where searchWord is a
# prefix of this word. If searchWord is a prefix of more than one word,
# return the index of the first word (minimum index). If there is no such
# word return -1.

# A prefix of a string s is any leading contiguous substring of s.


def solution(sentence: str, searchWord: str) -> int:
    # str split to get the sentence into a list of words
    word_list = sentence.split(" ")

    # iterate through and use `startswith` teq to find
    # any word that starts with the prefix we're looking for
    for index, word in enumerate(word_list):
        if word.startswith(searchWord):
            return index + 1

    return -1


sentence1 = "i love eating burger"
search1 = "burg"

sentence2 = "this problem is an easy problem"
search2 = "pro"

solution(sentence=sentence1, searchWord=search1)
solution(sentence=sentence2, searchWord=search2)

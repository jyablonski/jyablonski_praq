# In English, we have a concept called root, which can be followed by some other word to form another
# longer word - let's call this word derivative. For example, when the root "help" is followed by the
# word "ful", we can form a derivative "helpful".

# Given a dictionary consisting of many roots and a sentence consisting of words separated by spaces,
# replace all the derivatives in the sentence with the root forming it. If a derivative can be
# replaced by more than one root, replace it with the root that has the shortest length.

# Return the sentence after the replacement.


# time complexity of O(n * m) because we have to check every combination of a word to the list of roots
def solution(dictionary: list[str], sentence: str) -> str:
    sentence_list = sentence.split(" ")
    word_set = set(dictionary)
    result = []

    # iterate through the list of words
    for word in sentence_list:
        # create a new replacement var incase we can truncate the word to a root
        replacement = word

        # then iterate through the roots. if we find a match and the word startswith
        # a root, and the length of the word is < the root of the word, then replace it
        for root in word_set:
            if word.startswith(root):
                if len(root) < len(replacement):
                    replacement = root

        # finally, add it to the result list
        result.append(replacement)

    return " ".join(result)


dictionary1 = ["cat", "bat", "rat"]
sentence1 = "the cattle was rattled by the battery"

dictionary2 = ["a", "b", "c"]
sentence2 = "aadsfasf absbs bbab cadsfafs"

solution(dictionary=dictionary1, sentence=sentence1)
solution(dictionary=dictionary2, sentence=sentence2)

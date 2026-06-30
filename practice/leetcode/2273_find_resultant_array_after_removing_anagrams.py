# You are given a 0-indexed string array words, where words[i] consists of lowercase English letters.

# In one operation, select any index i such that 0 < i < words.length and words[i - 1] and words[i]
# are anagrams, and delete words[i] from words. Keep performing this operation as long as you can
# select an index that satisfies the conditions.

# Return words after performing all operations. It can be shown that selecting the indices for each
# operation in any arbitrary order will lead to the same result.

# An Anagram is a word or phrase formed by rearranging the letters of a different word or phrase
# using all the original letters exactly once. For example, "dacb" is an anagram of "abdc".

# time complexity o(n x m log m) where n is number of words and m is the average word length (for sorting)
def solution(words: list[str]) -> list[str]:
    # build a result list by checking each word against the previous one
    # we start with this because it can never be deleted as it has no previous value
    res = [words[0]]

    # iterate through words starting at the 1st index (2nd value in the list)
    # beacuse we already put words[0] in
    for i in range(1, len(words)):
        # check if the current word (sorted) is an anagram with the last value in the array
        # if it's not an anagram, we add the current word to the array and move on
        if sorted(words[i]) != sorted(res[-1]):
            res.append(words[i])

    return res


words1 = ["abba", "baba", "bbaa", "cd", "cd"]
words2 = ["a", "b", "c", "d", "e"]

solution(words=words1)
solution(words=words2)

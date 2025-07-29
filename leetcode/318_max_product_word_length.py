# Given a string array words, return the maximum value of length(word[i]) *length(word[j])
# where the two words do not share common letters. If no such two words exist, return 0.

# the proper efficient solution involves some bitmask fuckass bullshit. absolutely not.
# 	O(n^2 * k)
from collections import Counter


# you could use sets here instead because we arent using the counter portion of counter,
# but it requires special syntax (set.isdisjoint) etc i havent seen before
def solution(words: list[str]) -> int:
    n = len(words)
    counters = [Counter(word for word in words)]
    lengths = [len(word) for word in words]

    max_product = 0

    for i in range(n):
        for j in range(i + 1, n):
            # only calculate max product if each counter has no shared characters
            # (which are the keys in the dict)
            if not (counters[i].keys() & counters[j].keys()):
                max_product = max(max_product, lengths[i] * lengths[j])

    return max_product


words1 = ["abcw", "baz", "foo", "bar", "xtfn", "abcdef"]
words2 = ["a", "ab", "abc", "d", "cd", "bcd", "abcd"]

solution(words=words1)
solution(words=words2)


# set approach
def maxProduct(words: list[str]) -> int:
    n = len(words)
    sets = [set(word) for word in words]
    lengths = [len(word) for word in words]

    max_product = 0

    for i in range(n):
        for j in range(i + 1, n):
            if sets[i].isdisjoint(sets[j]):
                max_product = max(max_product, lengths[i] * lengths[j])

    return max_product

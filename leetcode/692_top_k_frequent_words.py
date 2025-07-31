# Given an array of strings words and an integer k, return the k most frequent strings.

# Return the answer sorted by the frequency from highest to lowest. Sort the words with
# the same frequency by their lexicographical order.

from collections import Counter


# time complexity O(n + m log m)
def solution(words: list[str], k: int) -> list[str]:
    freq = Counter(words)

    # sort first by count desc, then by character ascending
    sorted_words = sorted(freq.items(), key=lambda x: (-x[1], x[0]))
    print(sorted_words)

    # only pull the first k words
    return [word for word, _ in sorted_words[:k]]


words1 = ["i", "love", "leetcode", "i", "love", "coding"]
words2 = ["the", "day", "is", "sunny", "the", "the", "the", "sunny", "is", "is"]

k1 = 2
k2 = 4

solution(words=words1, k=k1)
solution(words=words2, k=k2)

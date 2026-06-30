# You are given an array of strings words and a string chars.
# A string is good if it can be formed by characters from chars (each character can only be used once).
# Return the sum of lengths of all good strings in words.

# trick is to use counter, it counts the frequency of chars in a string and
# outputs them to a dict basically. then you can do a very simple check to see
# if the counter for that word is less than or equal to the char count you have available,
# and if so then the len of that word can be saved to your result.

from collections import Counter


def solution(words: list[str], chars: str) -> int:
    char_count = Counter(chars)
    result = 0

    # loop through every word
    for word in words:
        word_count = Counter(word)

        # When you compare two Counter objects with >=, it checks if every
        # character in char_count appears at least that many times in word_count.
        print(f"Checking if {word_count} <= {char_count}")
        if char_count >= word_count:
            result += len(word)

    return result


words1 = ["cat", "bt", "hat", "tree"]
chars1 = "atach"

words2 = ["hello", "world", "leetcode"]
chars2 = "welldonehoneyr"

solution(words=words1, chars=chars1)
solution(words=words2, chars=chars2)

# basically doing this under the hood
# chars1 = "atach"
# char_count = {}

# for char in chars1:
#     if char in char_count:
#         char_count[char] += 1
#     else:
#         char_count[char] = 1

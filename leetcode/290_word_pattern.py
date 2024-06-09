# Given a pattern and a string s, find if s follows the same pattern.
# Here follow means a full match, such that there is a bijection between a letter in pattern and a non-empty word in s.

# i can get the list of words into a set


# the trick to this problem is first splitting the string by space to get
# words
# then you can easily check if the # of words != the # of characters in the pattern
# this serves 2 purposes: it immediately checks if we can return false, and it ensures we can
# accurately use zip in the subsequent step.
# then the fun begins
# the trick is to use zip to map 2 iterable objects together to aggregate them from left to right
def solution(pattern: str, s: str) -> bool:
    words = s.split(" ")

    if len(words) != len(pattern):
        return False

    print(set(zip(pattern, words)))
    print(f"{len(set(zip(pattern, words)))} - {len(set(pattern))} - {len(set(words))}")
    return len(set(zip(pattern, words))) == len(set(pattern)) == len(set(words))


pattern1 = "abba"
s1 = "dog cat cat dog"

pattern2 = "abba"
s2 = "dog cat cat fish"

pattern3 = "aaaa"
s3 = "dog cat cat dog"

pattern4 = "aaa"
s4 = "dog cat cat dog"

pattern5 = "abaa"
s5 = "dog cat dog cat"

solution(pattern=pattern1, s=s1)
solution(pattern=pattern2, s=s2)
solution(pattern=pattern3, s=s3)
solution(pattern=pattern4, s=s4)

# {('a', 'cat'), ('a', 'dog'), ('b', 'cat')}
# 3 - 2 - 2
solution(pattern=pattern5, s=s5)

# zip praq
# if an uneven amount of elements exist, the extras get chopped off
# 4 gets chopped tf off because list2 doesnt have an extra one.
list1 = [1, 2, 3, 4]
list2 = ["a", "b", "c"]
zipped = zip(list1, list2)
print(list(zipped))  # Output: [(1, 'a'), (2, 'b'), (3, 'c')]

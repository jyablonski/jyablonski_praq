# Given two strings s and p, return an array of all the start indices of p's anagrams in s.
# You may return the answer in any order.

from collections import Counter


def solution(s: str, p: str) -> list[int]:
    res = []
    p_count = Counter(p)
    window_count = Counter()
    p_len = len(p)

    for i, char in enumerate(s):
        window_count[char] += 1

        if i >= p_len:
            left_char = s[i - p_len]
            print(f"i > p_len at index {i} and left char {left_char}")
            if window_count[left_char] == 1:
                del window_count[left_char]
            else:
                window_count[left_char] -= 1

        if window_count == p_count:
            print(f"{window_count} and {p_count} are equal, we have match")
            res.append(i - p_len + 1)

    return res


s1 = "cbaebabacd"
s2 = "abab"
p1 = "abc"
p2 = "ab"

solution(s=s1, p=p1)
solution(s=s2, p=p2)

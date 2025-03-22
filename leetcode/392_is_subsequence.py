# Given two strings s and t, return true if s is a subsequence of t, or false otherwise.

# A subsequence of a string is a new string that is formed from the original string
# by deleting some (can be none) of the characters without disturbing the relative
# positions of the remaining characters. (i.e., "ace" is a subsequence of "abcde" while "aec" is not).


def solution(s: str, t: str) -> bool:
    # use j to keep track of how many chars in the subsequence we've found
    j = 0
    len_s = len(s)

    # use 2 pointer technique
    # loop through the larger `t` string and if
    # we get a match where the current char
    # is equal to s[j] then add 1 to j
    for char in t:
        if j < len_s and char == s[j]:
            print(f"Found match at {char} and {s[j]}")
            j += 1

    # if j == len_s then we have a subsequence match
    return j == len_s


s1 = "abc"
t1 = "ahbgdc"

# this returns false because of the ordering of aec, we loop over `t` but we're
# still trying to compare against `e` and dont find it until the very end.
# at which we're done w/ the string, so we compare j=2 vs len(s2) or 2 == 3 which is False
s2 = "aec"
t2 = "abcde"

solution(s=s1, t=t1)
solution(s=s2, t=t2)

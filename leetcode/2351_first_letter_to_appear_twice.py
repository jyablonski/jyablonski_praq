# Given a string s consisting of lowercase English letters, return the first letter
# to appear twice.

# Note:

# A letter a appears twice before another letter b if the second occurrence of a is
# before the second occurrence of b.
# s will contain at least one letter that appears twice.

# there are apparently other ways to do this problem with bitwise operators and
# shit but fuck that


# just loop through and use a set to track what characters you've passed
def solution(s: str) -> str:
    chars_passed = set()

    for char in s:
        if char not in chars_passed:
            chars_passed.add(char)
        else:
            return char


s1 = "abccbaacz"
s2 = "abcdd"

solution(s=s1)
solution(s=s2)

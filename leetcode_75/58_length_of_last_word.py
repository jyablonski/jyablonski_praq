# Given a string s consisting of words and spaces, return the length of the last word in the string.

# A word is a maximal
# substring
#  consisting of non-space characters only.


def solution(s: str) -> int:
    s = s.strip().split()

    return s[-1]


str1 = "Hello World"
str2 = "   fly me   to   the moon  "

solution(str1)
solution(str2)

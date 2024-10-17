# Given a string s, find the first non-repeating character in it and return its index. If it does not exist, return -1.


def solution(s: str) -> int:
    # use a dictionary because we're tracking chars and indexes here
    passed_chars = {}

    # loop through entire string, if we find a new char then add it,
    # if we find an existing one then set its value to -1
    for index, char in enumerate(s):
        if char in passed_chars:
            passed_chars[char] = -1
        else:
            passed_chars[char] = index

    # dictionaries maintain the order of insertion since python 3.7, so we'll be able
    # to grab the index of the first char that doesn't have a -1 set
    for char, index in passed_chars.items():
        if index != -1:
            return index

    return -1


#
s1 = "leetcode"
s2 = "loveleetcode"


solution(s=s1)
solution(s=s2)

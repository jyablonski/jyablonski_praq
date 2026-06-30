# Given two strings s and t, determine if they are isomorphic.

# Two strings s and t are isomorphic if the characters in s can be replaced to get t.

# All occurrences of a character must be replaced with another character while preserving
# the order of characters. No two characters may map to the same character, but a character may map to itself.


# use 2 dictionaries and iterate through both of them at once w/ `zip`
# and check if the mapping is consistent throughout both strings
def solution(s: str, t: str) -> bool:
    if len(s) != len(t):
        return False

    s_to_t = {}
    t_to_s = {}

    for char_s, char_t in zip(s, t):
        if char_s in s_to_t:
            if s_to_t[char_s] != char_t:
                return False
        else:
            s_to_t[char_s] = char_t

        if char_t in t_to_s:
            if t_to_s[char_t] != char_s:
                return False
        else:
            t_to_s[char_t] = char_s

    return True


s1 = "egg"
t1 = "add"
s2 = "foo"
t2 = "bar"


solution(s=s1, t=t1)
solution(s=s2, t=t2)


# this just didnt work, strings need to be same len and also this test case
# breaks it

# s3 = "bbbaaaba"
# t3 = "aaabbbba"
# def solution(s: str, t: str) -> bool:
#     unique_s_char_count = len(set(s))
#     unique_t_char_count = len(set(t))

#     return True if unique_s_char_count == unique_t_char_count else False

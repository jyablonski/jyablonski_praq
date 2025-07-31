# Given a string s which consists of lowercase or uppercase letters, return the
# length of the longest palindrome that can be built with those letters.

# Letters are case sensitive, for example, "Aa" is not considered a palindrome.

from collections import Counter


# time complexity o(n) because we just iterate through the entire string
# space is o(1)
def solution(s: str) -> int:
    # solution revolves around getting a count of the characters in s
    freq_map = Counter(s)
    res = 0

    # if a character ever has an odd count (1, 3 etc) then
    # we treat the count differently
    odd_found = False

    for count in freq_map.values():
        print(f"Length starting is {res}")

        # if the count is even, then we can just add the count to res
        # because we can always split the occurrences on both sides evenly
        if count % 2 == 0:
            res += count

        # otherwise if it's odd, we we cant split them evenly, so we can split
        # all but one
        else:
            res += count - 1
            odd_found = True

        print(f"Length is now {res}")

    # if at least 1 character was odd, then we add 1 back into res
    # example: abbcc. we would add 1 - 1 = 0 to the count initially, but
    # then we add it back in before we return the res
    if odd_found:
        res += 1

    return res


s1 = "abccccdd"
s2 = "a"

solution(s=s1)
solution(s=s2)

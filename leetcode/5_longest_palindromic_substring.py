# given a string `s`, find the longest palindromic substring in `s`, assuming
# `s` has a max length of 1000

# time complexity o(n^2) because for each n centers, we have to expand to up to n characters

# for racecar:
#     Center at e (index 3)
#     Expand: "e" → "cec" → "aceca" → "racecar"
#     Longest palindrome = "racecar"


def solution(s: str) -> str:
    # Given a potential center of a palindrome - defined by two indices left and right,
    # this function expands outward while the characters at s[left] and s[right] match.
    def expand_center(left, right):
        # we're allowed to keep expanding as long as left isnt negative, right isnt past the end,
        # and the characters match at the beginning and end of the string, which is what a palindrome is
        # the `left + 1` is necessary to get it back to index 0, because if we exited the loop, left
        # might be -1 now which is invalid
        while left >= 0 and right < len(s) and s[left] == s[right]:
            left -= 1
            right += 1

        return s[left + 1 : right]

    longest = ""
    for i in range(len(s)):
        # p1 handles odd-length palindromes
        # starts with s[i], then tries to expand to s[i-1] and s[i+1], then s[i-2] and s[i+2], etc.
        # Example: "aba" → center is 'b', expands to 'aba'
        p1 = expand_center(i, i)

        # p2 handles even-length palindromes
        # Starts with s[i] and s[i+1], then tries to expand to s[i-1] and s[i+2], etc.
        # Example: "abba" → center is between the two 'b's → expands to 'abba'
        p2 = expand_center(i, i + 1)

        # for every iteration, we recalculate longest len and check if we have a new max
        len_longest = len(longest)

        if len(p1) > len_longest:
            longest = p1
        if len(p2) > len_longest:
            longest = p2

    # after iterating through all characters, return longest
    return longest


str1 = "babadacacad"
str2 = "bddc"
str3 = "racecar"

solution(s=str1)
solution(s=str2)
solution(s=str3)


def solution_old(s: str) -> str:
    result = ""
    result_len = 0

    for i in range(len(s)):
        l = i
        r = i

        # check odd palindrome length `bcb`
        while l >= 0 and r < len(s) and s[l] == s[r]:
            if (r - l + 1) > result_len:
                result = s[l : r + 1]
                result_len = r - l + 1

            l -= 1
            r += 1

        l = i
        r = i + 1

        # check edge case even length `bddc`
        while l >= 0 and r < len(s) and s[l] == s[r]:
            if (r - l + 1) > result_len:
                result = s[l : r + 1]
                result_len = r - l + 1

            l -= 1
            r += 1

    return result


solution(str1)
solution(str2)

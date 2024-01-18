# given a string `s`, find the longest palindromic substring in `s`, assuming
# `s` has a max length of 1000
str1 = "babadacacad"
str2 = "bddc"


def solution(s: str) -> str:
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

# Given two strings text1 and text2, return the length of their longest common
# subsequence. If there is no common subsequence, return 0.

# A subsequence of a string is a new string generated from the original string
# with some characters (can be none) deleted without changing the relative order of the remaining characters.

# For example, "ace" is a subsequence of "abcde".
# A common subsequence of two strings is a subsequence that is common to both strings.


# time complexity (n * m)
def solution(text1: str, text2: str) -> int:
    m, n = len(text1), len(text2)

    # create dp of size (n + 1) * (m + 1), filled with 0s
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    # start outer loop at 1, m + 1
    for i in range(1, m + 1):
        # start inner loop at 1, n + 1
        for j in range(1, n + 1):
            # if the 2 values equal each other, then update dp[i][j]
            # to be what you could get before, plus the current character
            if text1[i - 1] == text2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                # if they're not equal, set current position to be the max
                # of either 1 to the left, or 1 from above
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    return dp[m][n]


text1 = "abcde"
text2 = "ace"

text3 = "abc"
text4 = "abc"


solution(text1=text1, text2=text2)
solution(text1=text3, text2=text4)

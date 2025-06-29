# You are given a string s containing only digits. Write a function to return the number of ways to decode using the following mapping:
# '1' -> "A"
# '2' -> "B"
# '3' -> "C"
# ...
# '26' -> "Z"
# There may be multiple ways to decode a string. For example, "14" can be decoded as "AD" or "N".


# use bottom up approach
def solution(s: str) -> int:
    # If the string is empty or starts with '0', it can't be decoded
    if not s or s[0] == "0":
        return 0

    n = len(s)

    dp = [0] * (n + 1)

    # Base case: there's 1 way to decode an empty string
    dp[0] = 1

    # Base case: if the first character isn't '0', there's one way to decode it
    dp[1] = 1

    for i in range(2, n + 1):
        # Check the last single digit (s[i-1])
        # If it's not '0', it can be decoded on its own, so add dp[i-1]
        one_digit = int(s[i - 1])
        if one_digit != 0:
            dp[i] += dp[i - 1]

        # Check the last two digits (s[i-2:i])
        # If the number is between 10 and 26, it can be decoded as a letter
        # so add dp[i-2]
        two_digits = int(s[i - 2 : i])
        if 10 <= two_digits <= 26:
            dp[i] += dp[i - 2]

    # dp[n] contains the total number of ways to decode the entire string
    return dp[n]


s1 = "12"
s2 = "226"

solution(s=s1)
solution(s=s2)

# You are given an array of binary strings strs and two integers m and n.
# Return the size of the largest subset of strs such that there are at most m 0's and n 1's in the subset.
# A set x is a subset of a set y if all elements of x are also elements of y.

# bottom up dynamic programming solution.
# time complexity len(strs) * m * n
def solution(strs: list[str], m: int, n: int) -> int:
    n = len(strs)
    # need a 2D matrix because we're tracking two different constraints simultaneously: 0s and 1s
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for s in strs:
        # count 0s and 1s in current string
        zeroes = s.count("0")
        ones = s.count("1")

        # traverse backwards to avoid using same string multiple times
        for i in range(m, zeroes - 1, -1):
            for j in range(n, ones - 1, -1):
                # choose to include this string or not by comparing
                # the current max, and the max of the prev + 1
                dp[i][j] = max(dp[i][j], dp[i - zeroes][j - ones] + 1)

    return dp[m][n]


strs1 = ["10", "0001", "111001", "1", "0"]
m1 = 5
n1 = 3

strs2 = ["10", "0", "1"]
m2 = 1
n2 = 1

solution(strs=strs1, m=m1, n=n1)
solution(strs=strs2, m=m2, n=n2)


# if you were only tracking 0's - 1D array is enough
# dp = [0] * (m + 1)
# for s in strs:
#     zeros = s.count('0')
#     for i in range(m, zeros - 1, -1):
#         dp[i] = max(dp[i], dp[i - zeros] + 1)

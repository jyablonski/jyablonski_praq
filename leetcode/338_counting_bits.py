# Given an integer n, return an array ans of length n + 1 such that for each i (0 <= i <= n),
# ans[i] is the number of 1's in the binary representation of i.


# The key to this problem lies in the fact that any binary number can be broken down into two parts:
# the least-significant (rightmost bit), and the rest of the bits.
# 4 in binary -> 100. the right bit is 0, the rest of the bits are 10 (which is 4 // 2 = 2 in binary)
def solution(n: int) -> list[int]:
    dp = [0] * (n + 1)

    for i in range(1, n + 1):
        dp[i] = dp[i // 2] + (i % 2)

    return dp


n1 = 2
n2 = 5

solution(n=n1)
solution(n=n2)

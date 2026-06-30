# Given an integer n, return an array ans of length n + 1 such that for each i (0 <= i <= n),
# ans[i] is the number of 1's in the binary representation of i.


# The key to this problem lies in the fact that any binary number can be broken down into two parts:
# the least-significant (rightmost bit), and the rest of the bits.
# 4 in binary -> 100. the right bit is 0, the rest of the bits are 10 (which is 4 // 2 = 2 in binary)
def solution(n: int) -> list[int]:
    dp = [0] * (n + 1)

    # Every number i in binary can be derived from its half (i // 2), shifted left
    # with possibly a 1 added at the end depending on whether i is odd.
    for i in range(1, n + 1):
        dp[i] = dp[i // 2] + (i % 2)

    return dp


n1 = 2
n2 = 5

solution(n=n1)
solution(n=n2)


# lmfao these fucking chumps, just do this solution
# but ooooooh it's only o(n log n) instead of o(n)
def solution(n: int) -> list[int]:
    dp = [0] * (n + 1)

    for i in range(1, n + 1):
        dp[i] = bin(i).count("1")

    return dp

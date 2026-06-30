# Given an integer n, return the least number of perfect square numbers that sum to n.

# A perfect square is an integer that is the square of an integer; in other words,
# it is the product of some integer with itself. For example, 1, 4, 9, and 16 are perfect squares while 3 and 11 are not.


def solution(n: int) -> int:
    dp = [n] * (n + 1)

    dp[0] = 0

    for i in range(1, n + 1):
        for j in range(1, i + 1):
            # print(dp)
            square = j * j
            if i - square < 0:
                break

            dp[i] = min(dp[i], dp[i - square] + 1)

    return dp[n]


n1 = 12
n2 = 13

solution(n1)
solution(n2)


squares = [i * i for i in range(12)]

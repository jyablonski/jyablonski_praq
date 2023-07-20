# Given an integer n, return an array ans of length n + 1 such that for each i (0 <= i <= n),
# ans[i] is the number of 1's in the binary representation of i.

n_test = 5


def solution(n: int):
    dp = [0]

    for i in range(1, n + 1):
        print(f"i is {i}, i % 2 is {i % 2} zzz")
        if i % 2 == 1:
            dp.append(dp[i - 1] + 1)
        else:
            print(f"i is {i // 2} bby")
            dp.append(dp[i // 2])

    return dp


solution(n=n_test)

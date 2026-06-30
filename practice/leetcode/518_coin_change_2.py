# You are given an integer array coins representing coins of different denominations
# and an integer amount representing a total amount of money.

# Return the number of combinations that make up that amount. If that amount of money
# cannot be made up by any combination of the coins, return 0.

# You may assume that you have an infinite number of each kind of coin.

# The answer is guaranteed to fit into a signed 32-bit integer.

# You are asked to count combinations (not permutations), so:
# [1, 2, 2] is the same as [2, 1, 2] and should only be counted once.


def solution(amount: int, coins: list[int]) -> int:
    dp = [0] * (amount + 1)
    dp[0] = 1

    for coin in coins:
        for i in range(coin, amount + 1):
            print(f"Adding {dp[i - coin]} to {dp[i]} ")
            dp[i] += dp[i - coin]
            print(f"dp list is now {dp}")

    return dp[amount]


amount1 = 5
coins1 = [1, 2, 5]

amount2 = 3
coins2 = [3]

solution(amount=amount1, coins=coins1)
solution(amount=amount2, coins=coins2)

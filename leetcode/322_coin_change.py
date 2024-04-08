# You are given an integer array coins representing coins of different denominations
# and an integer amount representing a total amount of money.

# Return the fewest number of coins that you need to make up that amount. If that amount
# of money cannot be made up by any combination of the coins, return -1.

# You may assume that you have an infinite number of each kind of coin.


# initialize a list dp with length amount + 1, where each element is initialized to amount + 1.
# you do amount + 1 because the base case of dp[0] = 0 is taking up a spot, and we want
# dp[amount]
# set dp[0] = 0, indicating that zero coins are needed to make up an amount of zero.
# then iterate over each amount from 1 to amount, and for each amount, iterate over each coin denomination.
# For each combination of amount and coin, check if subtracting the coin value from the current amount leaves a non-negative remainder.
# If the remainder is non-negative, update dp[amount] to the minimum of its current value and 1 + dp[amount - coin],
# which represents the minimum number of coins needed to make up the remaining amount after subtracting the current coin.
# Finally, return dp[amount] if it's not equal to amount_default (indicating that a valid solution exists), otherwise return -1.
def solution(coins: list[int], target_amount: int) -> int:
    amount_default = target_amount + 1
    dp = [amount_default] * (amount_default)
    dp[0] = 0

    for amount in range(1, amount_default):
        for coin in coins:
            print(dp)
            if amount - coin >= 0:
                dp[amount] = min(dp[amount], 1 + dp[amount - coin])

    return dp[target_amount] if dp[target_amount] != amount_default else -1


coins = [3, 7]
amount1 = 8

solution(coins=coins, target_amount=amount1)

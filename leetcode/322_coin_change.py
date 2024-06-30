# You are given an integer array coins representing coins of different denominations
# and an integer amount representing a total amount of money.

# Return the fewest number of coins that you need to make up that amount. If that amount
# of money cannot be made up by any combination of the coins, return -1.

# You may assume that you have an infinite number of each kind of coin.


# bottom-up dynamic programming - it starts with the smallest subproblems and builds up the target amount.
# it iteratively fills up the dp array from base case to target amount so each subproblem is solved before
# moving onto the next one.
# time complexity O(target_amount * coins) because we have to iterate through every possible combination
def solution(coins: list[int], target_amount: int) -> int:
    # initialize the amount default value as `target_amount + 1`, which acts as an infinity placeholder
    # this value is chosen because it's higher than any possible number of coins needed to make up the target_amount.
    # so if an amount cannot be reached with the given coins, it remains at `amount_default`.
    amount_default = target_amount + 1

    # initialize a list dp with length amount + 1, where each element is initialized to `amount_default`
    dp = [amount_default] * amount_default

    # Base case: 0 amount requires 0 coins
    dp[0] = 0

    # Iterate over each amount from 1 to `target_amount`
    for amount in range(1, amount_default):
        # Iterate over each coin denomination
        for coin in coins:
            # print(dp)

            # If the remainder is a valid non-negative amount, update `dp[amount]` to the minimum of its
            # current value and 1 + dp[amount - coin],
            # dp[amount] represents the minimum number of coins needed to make the amount amount.
            # 1 + dp[amount - coin] represents the minimum number of coins needed to make the amount `amount - coin.`
            if amount - coin >= 0:
                dp[amount] = min(dp[amount], 1 + dp[amount - coin])

    # Return the result: `dp[target_amount]` if it's not equal to amount_default, otherwise -1
    return dp[target_amount] if dp[target_amount] != amount_default else -1


coins1 = [3, 7]
amount1 = 8

coins2 = [25, 5]
amount2 = 45

solution(coins=coins1, target_amount=amount1)
solution(coins=coins2, target_amount=amount2)

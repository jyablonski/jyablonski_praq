def count_combos(target: int, coins: list[int]) -> int:
    # create the table to store results in
    dp = [0] * (target + 1)

    # set base case
    dp[0] = 1

    for coin in coins:
        print(f"checking {coin}")
        for i in range(coin, target + 1):
            print(f"Adding {dp[i - coin]} to {dp[i]} ")
            dp[i] += dp[i - coin]
            print(f"new dp is {dp}")

    print(f"Returning {dp[target]} from {dp}")
    return dp[target]


print(count_combos(5, [1, 2, 3]))  # Output: 4

# Avoids recursion (uses an array instead)
# More efficient (O(n × m) time complexity)
# No path tracking (only counts ways, does not generate paths)

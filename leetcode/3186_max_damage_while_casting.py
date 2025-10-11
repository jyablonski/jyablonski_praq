# A magician has various spells.

# You are given an array power, where each element represents the damage of a spell.
# Multiple spells can have the same damage value.

# It is a known fact that if a magician decides to cast a spell with a damage of power[i],
# they cannot cast any spell with a damage of power[i] - 2, power[i] - 1, power[i] + 1,
# or power[i] + 2.

# Each spell can be cast only once.

# Return the maximum possible total damage that a magician can cast.

from collections import Counter


# time complexity O(n log n), dominant factor is the sorting step and then we just
# iterate through the length of the unique powers


# The solution involves a bottom-up DP approach where we:
# 1. Use Counter to get frequencies of each power level
# 2. Sort the unique power values
# 3. Initialize the first 2 elements of the dp list as base cases
# 4. Use a for loop to fill the rest of the dp array
# 5. For each power level, find the last compatible index (distance > 2)
#    by moving backwards until we find a power that doesn't conflict
# 6. Choose the maximum between:
#    - Skipping current power (take dp[i-1])
#    - Using current power with all its copies plus the best compatible previous state (dp[j] + current_total)
# 7. Return dp[-1] as the final answer


# Key insight: At each step, we decide whether including the current power level
# (with all its occurrences) gives us more total damage than skipping it.
# We can only combine it with previous powers that are more than 2 away.
def solution(power: list[int]) -> int:
    freq = Counter(power)

    unique_powers = sorted(freq.keys())
    print(f"Freq is {freq} and unique powers is {unique_powers}")

    # no limit on the number of times the same spell can be cast,
    # so if there's only 1 unique spell then return spell * count
    if len(unique_powers) == 1:
        return unique_powers[0] * freq[unique_powers[0]]

    # dp[i] = max damage we can get considering powers up to index i
    n = len(unique_powers)
    dp = [0] * n

    # Base case: first power level
    dp[0] = unique_powers[0] * freq[unique_powers[0]]

    # second power level
    if unique_powers[1] - unique_powers[0] <= 2:
        # Can't use both, pick the better one
        dp[1] = max(dp[0], unique_powers[1] * freq[unique_powers[1]])
    else:
        # use both
        dp[1] = dp[0] + unique_powers[1] * freq[unique_powers[1]]

    for i in range(2, n):
        current_power = unique_powers[i]
        current_total = current_power * freq[current_power]

        # Find the last index we can combine with (distance > 2)
        # We need to check which previous values we can include
        j = i - 1
        while j >= 0 and unique_powers[i] - unique_powers[j] <= 2:
            j -= 1

        if j >= 0:
            # We can include power[i] with dp[j]
            dp[i] = max(dp[i - 1], dp[j] + current_total)
        else:
            # Can't combine with any previous, choose between taking current or previous best
            dp[i] = max(dp[i - 1], current_total)

    return dp[-1]


power1 = [1, 1, 3, 4]
power2 = [7, 1, 6, 6]

solution(power=power1)
solution(power=power2)

# You are a professional robber planning to rob houses along a street.
# Each house has a certain amount of money stashed, the only constraint stopping you
# from robbing each of them is that adjacent houses have security systems connected and
# it will automatically contact the police if two adjacent houses were broken into on the same night.

# Given an integer array nums representing the amount of money of each house,
# return the maximum amount of money you can rob tonight without alerting the police.


def robber(nums: list[int]) -> int:
    prev_max = 0  # Previous maximum amount stolen
    current_max = 0  # Current maximum amount stolen

    for n in nums:
        new_max = max(n + prev_max, current_max)
        prev_max = current_max
        current_max = new_max

    return current_max


nums = [1, 2, 3, 1]
robber(nums=nums)

# You are a professional robber planning to rob houses along a street.
# Each house has a certain amount of money stashed, the only constraint stopping you
# from robbing each of them is that adjacent houses have security systems connected and
# it will automatically contact the police if two adjacent houses were broken into on the same night.

# Given an integer array nums representing the amount of money of each house,
# return the maximum amount of money you can rob tonight without alerting the police.

# initialize prev_max and current_max to integer values of 0
# loop through nums and calculate new_max FIRST which is the greater of (current_house_value + prev_max) and (current_max)
# then set prev_max to the current_max to set the previous value
# then set current_max to new_max to set the new current max because it doesnt need to hold the old value anymore


def robber(nums: list[int]) -> int:
    prev_max = 0  # Previous maximum amount stolen
    current_max = 0  # Current maximum amount stolen

    for current_house_value in nums:
        print(
            f"current house value is {current_house_value}, prev_max is {prev_max}, current_max is {current_max}"
        )
        new_max = max(current_house_value + prev_max, current_max)
        prev_max = current_max

        print(f"setting current max to {new_max}")
        current_max = new_max

    return current_max


nums = [1, 2, 3, 1, 5, 7, 10, 3, 5, 1]
robber(nums=nums)


current_max = 0
prev_max = 0

for value in nums:
    new_max = max(value + prev_max, current_max)
    prev_max = current_max
    current_max = new_max

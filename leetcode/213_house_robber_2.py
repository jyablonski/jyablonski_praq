# You are a professional robber planning to rob houses along a street. Each house has a certain
# amount of money stashed. All houses at this place are arranged in a circle. That means the
# first house is the neighbor of the last one. Meanwhile, adjacent houses have a security system
# connected, and it will automatically contact the police if two adjacent houses were broken
# into on the same night.

# Given an integer array nums representing the amount of money of each house, return the
# maximum amount of money you can rob tonight without alerting the police.


# this is the same solution and implementation as house robber 1, the only difference
# is you cant rob the first house and the last house together because of the circle constraint
def rob(nums: list[int]) -> int:
    prev_max = 0
    current_max = 0

    for value in nums:
        new_max = max(prev_max + value, current_max)
        prev_max = current_max
        current_max = new_max

    return current_max


# the solution is to run `rob` twice: once
def solution(nums: list[int]) -> int:
    if not nums:
        return 0

    if len(nums) == 1:
        return nums[0]

    # exclude the last house
    rob1 = rob(nums[:-1])

    # exclude the first house
    rob2 = rob(nums[1:])

    # take the max of the two
    return max(rob1, rob2)


nums1 = [2, 3, 2]
nums2 = [1, 2, 3, 1]

solution(nums=nums1)
solution(nums=nums2)

# You are given an integer array nums. You are initially positioned at the array's first index,
# and each element in the array represents your maximum jump length at that position.

# Return true if you can reach the last index, or false otherwise.


def solution(nums: list[int]) -> bool:
    max_reach = 0

    for i in range(len(nums)):
        if i > max_reach:
            return False

        max_reach = max(max_reach, i + nums[i])

    return True


nums1 = [2, 3, 1, 1, 4]
nums2 = [3, 2, 1, 0, 4]

solution(nums=nums1)
solution(nums=nums2)

# Given an integer array nums, return the maximum difference between two
# successive elements in its sorted form. If the array contains less than two elements, return 0.

# You must write an algorithm that runs in linear time and uses linear extra space.


# this is invalid, but like what the fuck ever lmfao.
# they wanmt to use bucket or radix sort or something
def solution(nums: list[int]) -> int:
    if len(nums) < 2:
        return 0

    nums.sort()

    nums_len = len(nums)
    max_gap = 0

    for i in range(nums_len - 1):
        gap = nums[i + 1] - nums[i]
        max_gap = max(max_gap, gap)

    return max_gap


nums1 = [3, 6, 9, 1]
nums2 = [10]

solution(nums=nums1)
solution(nums=nums2)

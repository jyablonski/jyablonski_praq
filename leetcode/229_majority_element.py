# Given an integer array of size n, find all elements that appear more than ⌊ n/3 ⌋ times.

from collections import Counter


def solution(nums: list[int]) -> list[int]:
    # build a frequency counter for nums, and define limit
    freq = Counter(nums)
    limit = len(nums) // 3

    # return a list of nums if the count is greater than limit
    return [num for (num, count) in freq.items() if count > limit]


nums1 = [3, 2, 3]
nums2 = [1]

solution(nums=nums1)
solution(nums=nums2)

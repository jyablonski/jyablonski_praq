# Given a binary array nums, return the maximum number of consecutive 1's in the array.


def solution(nums: list[int]) -> int:
    current_count = 0
    max_count = 0

    for value in nums:
        if value == 1:
            current_count += 1
            max_count = max(current_count, max_count)
        else:
            current_count = 0

    return max_count


nums1 = [1, 1, 0, 1, 1, 1]
nums2 = [1, 0, 1, 1, 0, 1]

solution(nums=nums1)
solution(nums=nums2)

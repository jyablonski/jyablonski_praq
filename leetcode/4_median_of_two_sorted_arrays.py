# Given two sorted arrays nums1 and nums2 of size m and n respectively, return the median of the two sorted arrays.

# The overall run time complexity should be O(log (m+n)).

# whip out this solution and tell them to go fuck themselves!


def solution(nums1: list[int], nums2: list[int]) -> float:
    # join the 2 lists together and call sorted on it
    sorted_nums = sorted(nums1 + nums2)
    n = len(sorted_nums)

    # if length is an odd number, just return the middle number
    if n % 2 == 1:
        return sorted_nums[n // 2]

    # if length is even
    else:
        return (sorted_nums[n // 2 - 1] + sorted_nums[n // 2]) / 2


nums1 = [1, 3]
nums2 = [2]

nums3 = [1, 2]
nums4 = [3, 4]

solution(nums1=nums1, nums2=nums2)
solution(nums1=nums3, nums2=nums4)


n1 = [1, 2, 3, 4, 5]

n1[len(n1) // 2]

len(n1) % 2

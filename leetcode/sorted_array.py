# problem 88
# given 2 integer arrays nums1 and nums2, sorted in non-decreasing order, and
# 2 integers m and n representing the elements in nums1 and nums2 respectively
# merge nums1 and nums2 into a single array sorted in non-decreasing order
# the final sorted array should not be returned by the function, but should be stored inside
# nums1, where it will have the length of m + n and the first m elements
from typing import List


# first pass - works but not memory efficient because of the all_nums helper
def solution(nums1: List[int], m: int, nums2: List[int], n: int) -> None:
    # nums = (nums1 + nums2).sort() this doesnt work apparently, None is returned
    all_nums = nums1 + nums2
    all_nums.sort()

    nums1 = []
    nums1 = [i for i in all_nums if i > 0]

    print(nums1)


nums1 = [1, 2, 3, 0, 0, 0]
nums2 = [2, 5, 6]
nums_1 = [1, 2, 3, 4, 0, 0, 0]
nums_2 = [2, 5, 6]
x = 3
y = 4

solution(nums1=nums_1, m=x, nums2=nums_2, n=y)


# second pass - most optimal.  merge into nums1 and work backwards bc we're given that the 2 arrays are in non-decreasing order
# no helper array needed
def solution2(nums1: List[int], m: int, nums2: List[int], n: int) -> None:
    # get last index of nums1
    last = m + n - 1

    # merge in reverse order
    while m > 0 and n > 0:
        # nums[n - 1] just means grab the biggest element in the array
        if nums1[m - 1] > nums2[n - 1]:
            nums1[last] = nums1[m - 1]
            print(
                f"setting index {last} as {nums1[m - 1]} because {nums1[m - 1]} > {nums2[n - 1]}"
            )
            m -= 1
        else:
            nums1[last] = nums2[n - 1]
            print(
                f"setting index {last} as {nums2[n - 1]} because {nums1[m - 1]} < {nums2[n - 1]}"
            )
            n -= 1
        last -= 1

    while n > 0:
        nums1[last] = nums2[n - 1]
        n = n - 1
        last = last - 1

    print(nums1)


nums_1 = [1, 2, 3, 0, 0, 0]
nums_2 = [2, 5, 6]
x = 3
y = len(nums_2)

solution2(nums1=nums_1, m=x, nums2=nums_2, n=y)

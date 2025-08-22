# Suppose an array of length n sorted in ascending order is rotated between 1 and n times. For example, the array nums = [0,1,2,4,5,6,7] might become:

# [4,5,6,7,0,1,2] if it was rotated 4 times.
# [0,1,2,4,5,6,7] if it was rotated 7 times.
# Notice that rotating an array [a[0], a[1], a[2], ..., a[n-1]] 1 time results in the array [a[n-1], a[0], a[1], a[2], ..., a[n-2]].

# Given the sorted rotated array nums of unique elements, return the minimum element of this array.

# You must write an algorithm that runs in O(log n) time.


# the key here is the log n hint, because it's a sorted array to begin with
def solution(nums: list[int]) -> int:
    left = 0
    right = len(nums) - 1

    while left < right:
        mid = (left + right) // 2

        # If mid element is greater than the rightmost element,
        # the minimum must be in the right half
        if nums[mid] > nums[right]:
            left = mid + 1

        # The min is in the left half (including mid)
        # we dont know yet if mid is the min or not, so
        # keep it at the right pointer instead of doing right = mid - 1
        else:
            right = mid

    # it doesn't matter whether you do nums[left] or nums[right] here,
    # the loop ends when they're both equal to each other
    return nums[left]


nums1 = [3, 4, 5, 1, 2]
nums2 = [4, 5, 6, 7, 0, 1, 2]

solution(nums=nums1)
solution(nums=nums2)

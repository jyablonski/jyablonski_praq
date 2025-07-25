# There is an integer array nums sorted in ascending order (with distinct values).

# Prior to being passed to your function, nums is possibly rotated at an unknown pivot index k (1 <= k < nums.length)
# such that the resulting array is [nums[k], nums[k+1], ..., nums[n-1], nums[0], nums[1], ..., nums[k-1]] (0-indexed).
# For example, [0,1,2,4,5,6,7] might be rotated at pivot index 3 and become [4,5,6,7,0,1,2].

# Given the array nums after the possible rotation and an integer target, return the index of target if it is in nums,
# or -1 if it is not in nums.

# You must write an algorithm with O(log n) runtime complexity.

# o(log n) is a hint that this involves binary search
# first half of the code is straightforward binary search


# second half of the code involves specific `between` type checks between
# nums[left], nums[mid], and nums[right]
def solution(nums: list[int], target: int) -> int:
    n = len(nums)
    left = 0
    right = n - 1

    while left <= right:
        mid = (left + right) // 2

        if nums[mid] == target:
            return mid

        # the `nums[mid] > target` checks are not equal to because we already checked
        if nums[left] <= nums[mid]:
            if nums[left] <= target < nums[mid]:
                right = mid - 1
            else:
                left = mid + 1

        # if nums[left] > nums[mid]
        else:
            if nums[mid] < target <= nums[right]:
                left = mid + 1
            else:
                right = mid - 1

    return -1


nums1 = [4, 5, 6, 7, 0, 1, 2]
target1 = 0

nums2 = [4, 5, 6, 7, 0, 1, 2]
target2 = 3

solution(nums=nums1, target=target1)
solution(nums=nums2, target=target2)

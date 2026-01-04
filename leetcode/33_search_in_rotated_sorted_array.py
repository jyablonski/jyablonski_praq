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

    # use <= to consider all elements -  we're searching for an exact match
    while left <= right:
        mid = (left + right) // 2

        # if mid is the target, return it
        if nums[mid] == target:
            return mid

        # because it's a rotated sorted array, we have to check which side is properly sorted
        # note the subsequent `nums[mid]` conditionals or < or > and not equal to because we've alrady checked
        # for mid right above this

        # ---- LEFT SIDE -----

        # if nums[left] <= nums[mid], then we check if target is in that left range and adjust accordingly
        if nums[left] <= nums[mid]:
            # note the subsequent `nums[mid]` conditionals or < or > and not equal to because we've alrady checked
            # for mid right above this
            if nums[left] <= target < nums[mid]:
                right = mid - 1
            else:
                left = mid + 1

        # ---- RIGHT SIDE -----
        # if nums[left] > nums[mid], then we check if target is in that right range and adjust accordingly
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

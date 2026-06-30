# Given an array nums, return true if the array was originally sorted in non-decreasing order,
# then rotated some number of positions (including zero). Otherwise, return false.

# There may be duplicates in the original array.

# Note: An array A rotated by x positions results in an array B of the same length such that
# A[i] == B[(i+x) % A.length], where % is the modulo operation.


# O(n) time complexity because we have to loop through every value in nums once
# loop through entire array and look for rotation points where the current value
# is greater than the next value
def solution(nums: list[int]) -> bool:
    num_rotations = sum([nums[i] > nums[i + 1] for i in range(len(nums) - 1)])

    # if more than a single rotation return false
    if num_rotations > 1:
        return False

    # return true if we have 0 rotations (like the input was a sorted array)
    # or if we have < 1 rotation and the last value is <= the first value
    return num_rotations == 0 or nums[-1] <= nums[0]


nums1 = [3, 4, 5, 1, 2]
nums2 = [2, 1, 3, 4]
nums3 = [1, 2, 3]

solution(nums=nums1)
solution(nums=nums2)
solution(nums=nums3)

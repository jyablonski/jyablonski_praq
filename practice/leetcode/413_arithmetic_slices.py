# An integer array is called arithmetic if it consists of at least three elements and if the
# difference between any two consecutive elements is the same.

# For example, [1,3,5,7,9], [7,7,7,7], and [3,-1,-5,-9] are arithmetic sequences.
# Given an integer array nums, return the number of arithmetic subarrays of nums.

# A subarray is a contiguous subsequence of the array.


# When we find a 3rd element that satisfies the condition, we increment length to 3,
# and add `length - 2 = 1` to the result (1 valid subarray).
#
# If the sequence continues, we keep increasing `length`,
# and for each new element, we add `length - 2` to the result
# because each new element extends all previous valid subarrays by 1 element
# and also forms a new one.
def solution(nums: list[int]) -> int:
    n = len(nums)
    if n < 3:
        return 0

    # `length = 2` as a base because we need at least 3 elements to form a valid subarray.
    # we can increment this by 1 and do `res += length - 2`, because that's 1 valid subarray
    # When we find a 3rd element that satisfies the condition, we increment length to 3,
    # and add `length - 2 = 1` to the result (1 valid subarray).
    #
    # If the sequence continues, we keep increasing `length`,
    # and for each new element, we add `length - 2` to the result
    # because each new element extends all previous valid subarrays by 1 element
    # and also forms a new one.
    res = 0
    length = 2  # current length of potential arithmetic subarray

    # start 2 indexes in because to determine if we have a valid subarray,
    # we need at least 3 elements in a row that satisfy the condition
    for i in range(2, n):
        print(i)
        if nums[i] - nums[i - 1] == nums[i - 1] - nums[i - 2]:
            length += 1
            print(f"Adding {length} - 2 to res")
            res += length - 2  # every new element adds (length - 2) new subarrays
        else:
            length = 2  # reset window if we dont meet our equality condition

    return res


nums1 = [1, 2, 3, 4]
nums2 = [1]

solution(nums1)
solution(nums2)


# first try
def solution(nums: list[int]) -> int:
    n = len(nums)
    start = 0
    res = 0
    last_diff = 0

    if n < 3:
        return 0

    for end in range(1, n):
        new_diff = nums[end] - nums[start]

        if new_diff != last_diff:
            last_diff = new_diff

        if end - start + 1 >= 3 and last_diff == new_diff:
            print(f"found a new solution at {end}, {start}")
            res += 1

    return res

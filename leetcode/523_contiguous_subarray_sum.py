# Given an integer array nums and an integer k, return true if nums has a good subarray or false otherwise.

# A good subarray is a subarray where:

# its length is at least two, and
# the sum of the elements of the subarray is a multiple of k.
# Note that:

# A subarray is a contiguous part of the array.
# An integer x is a multiple of k if there exists an integer n such that x = n * k. 0 is always a multiple of k.


def solution(nums: list[int], k: int) -> bool:
    # store indexes of where we first saw this remainder
    # this is initialzied to {0: -1} for an edge case where
    # the valid subarray starts at 0. it's needed for the
    # element count check later to accurately complete.
    remainder_map = {0: -1}
    prefix_sum = 0

    for i, num in enumerate(nums):
        print(f"Remainder before on {num}: {remainder_map}")
        prefix_sum += num
        remainder = prefix_sum % k

        # if we've seen this remainder before, the subarray between
        # that index and the current index has sum divisible by k
        if remainder in remainder_map:
            # make sure subarray has at least 2 elements
            if i - remainder_map[remainder] >= 2:
                return True
        else:
            remainder_map[remainder] = i

        print(f"    -> Remainder after: {remainder_map}")

    return False


nums1 = [23, 2, 4, 6, 7]
k1 = 6

nums2 = [23, 2, 6, 4, 7]
k2 = 13

solution(nums=nums1, k=k1)
solution(nums=nums2, k=k2)


# my first try
# def solution(nums: list[int], k: int) -> bool:
#     good_array = []
#     n = len(nums)

#     for num in nums:
#         good_array.append(num)

#         if len(good_array) >= 2:
#             good_array_sum = sum(good_array)
#             if k % good_array_sum == 0:
#                 return True
#             else:
#                 good_array = []

#     return False

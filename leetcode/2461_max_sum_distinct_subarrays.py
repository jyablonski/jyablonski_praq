# You are given an integer array nums and an integer k. Find the maximum subarray sum of all
# the subarrays of nums that meet the following conditions:

# The length of the subarray is k, and
# All the elements of the subarray are distinct.
# Return the maximum subarray sum of all the subarrays that meet the conditions. If no subarray
# meets the conditions, return 0.

# A subarray is a contiguous non-empty sequence of elements within an array.


def solution(nums: list[int], k: int) -> int:
    max_sum = 0
    current_sum = 0
    state = {}
    start = 0

    for end in range(len(nums)):
        current_sum += nums[end]
        state[nums[end]] = state.get(nums[end], 0) + 1

        # when the window is size `k`, if it contains all distinct elements
        # then we calculate a potential max sum
        if end - start + 1 == k:
            # only recalculate max sum if everything in the current window is distinct
            # if k = 3, then we need to have 3 distinct values in `state` in order to
            # calculate a new max sum
            if len(state) == k:
                max_sum = max(max_sum, current_sum)

            # afterwards, we have to prepare the next iteration by adjusting the window
            # we subtract the value we're on from the current_sum, and remove 1
            # from the index's value in the dictionary
            current_sum -= nums[start]
            state[nums[start]] -= 1

            # if that key now has a count of 0, then remove the key
            # this is necessary because of the len(state) check we do above
            if state[nums[start]] == 0:
                del state[nums[start]]

            # finally, increment start by 1
            start += 1

    return max_sum


nums1 = [1, 5, 4, 2, 9, 9, 9]
nums2 = [4, 4, 4]

k1 = 3
k2 = 3

solution(nums=nums1, k=k1)
solution(nums=nums2, k=k2)

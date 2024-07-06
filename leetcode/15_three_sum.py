# Given an integer array nums, return all the triplets [nums[i], nums[j], nums[k]] such
# that i != j, i != k, and j != k, and nums[i] + nums[j] + nums[k] == 0.

# Notice that the solution set must not contain duplicate triplets.

# initialize an empty result array
# sort in the input array first


def solution(nums: list[int]) -> list[list[int]]:
    result = []
    nums.sort()  # Sort the array to use two-pointer technique

    for key, value in enumerate(nums):
        # Skip duplicates for the current value
        if key > 0 and value == nums[key - 1]:
            continue

        # Two-pointer approach to find the other two numbers
        l = key + 1
        r = len(nums) - 1
        while l < r:
            three_sum = value + nums[l] + nums[r]

            # if the value is > 0 then our three_sum is too large, decrement the right pter
            if three_sum > 0:
                r -= 1

            # if the value is < 0 then our three_sum is too small, increment the left pter
            elif three_sum < 0:
                l += 1

            # else: we found our three_sum.  add the triplet to result and continue on
            else:
                result.append([value, nums[l], nums[r]])
                l += 1
                r -= 1

                # Skip duplicates for the second number
                while l < r and nums[l] == nums[l - 1]:
                    l += 1

                # Skip duplicates for the third number
                while l < r and nums[r] == nums[r + 1]:
                    r -= 1

    return result


nums = [-1, 0, 1, 2, -1, -4]
solution(nums)

# Given an integer array nums, return all the triplets [nums[i], nums[j], nums[k]] such
# that i != j, i != k, and j != k, and nums[i] + nums[j] + nums[k] == 0.

# Notice that the solution set must not contain duplicate triplets.

# initialize an empty result array
# sort in the input array first


# time complexity is o^2 because we are using nested loops in this solution from having to do
# n iterations and each iterations having to take o(n) time to use the 2 pter technique
def solution(nums: list[int]) -> list[list[int]]:
    result = []
    nums.sort()  # Sort the array to use two-pointer technique

    for key, value in enumerate(nums):
        # Skip duplicates for the current value
        if key > 0 and value == nums[key - 1]:
            continue

        # Two-pointer approach to find the other two numbers
        left = key + 1
        right = len(nums) - 1
        while left < right:
            three_sum = value + nums[left] + nums[right]

            # if the value is > 0 then our three_sum is too large, decrement the right pter
            if three_sum > 0:
                right -= 1

            # if the value is < 0 then our three_sum is too small, increment the left pter
            elif three_sum < 0:
                left += 1

            # else: we found our three_sum.  add the triplet to result and continue on
            else:
                result.append([value, nums[left], nums[right]])
                left += 1
                right -= 1

                # Skip duplicates for the second number
                while left < right and nums[left] == nums[left - 1]:
                    left += 1

                # Skip duplicates for the third number
                while left < right and nums[right] == nums[right + 1]:
                    right -= 1

    return result


nums = [-1, 0, 1, 2, -1, -4]
solution(nums)

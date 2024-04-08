# Given an integer array nums, return all the triplets [nums[i], nums[j], nums[k]] such
# that i != j, i != k, and j != k, and nums[i] + nums[j] + nums[k] == 0.

# Notice that the solution set must not contain duplicate triplets.

# initialize an empty result array
# sort in the input array first


def solution(nums: list[int]) -> list[list[int]]:
    result = []
    nums.sort()

    for key, value in enumerate(nums):
        # skip first iteration because we'll never have a dupe yet
        # and bc we sorted we can skip the current iteration
        # if the current value is ever == the previous value
        if key > 0 and value == nums[key - 1]:
            continue

        # create new pointers to iterate through the remaining array
        l = key + 1
        r = len(nums) - 1

        while l < r:
            three_sum = value + nums[l] + nums[r]

            if three_sum > 0:
                r -= 1
            elif three_sum < 0:
                l += 1
            else:
                result.append([key, nums[l], nums[r]])
                l += 1
                while nums[l] == nums[l - 1] and l < r:
                    l += 1

    return result


nums = [-1, 0, 1, 2, -1, -4]
solution(nums)

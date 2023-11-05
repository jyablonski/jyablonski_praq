# given integer list nums, find continuous ubarray which has the largest sum and return it


def maximum_subarray(nums: list[int]) -> int:
    # initialize our max sub with the first value
    # because these values can be < 0, we cant use 0 here.
    max_sub = nums[0]
    current_sum = 0

    # loop through every value in nums
    for value in nums:
        print("----------")
        print(f"iterating through value {value}")
        if current_sum < 0:
            current_sum = 0

        # add current value to current sum
        current_sum += value
        print(f"current sum is {current_sum}")

        # at the end of that,
        max_sub = max(max_sub, current_sum)
        print(f"max sub is {max_sub}")
        print("----------")
    return max_sub


nums = [-2, 1, -3, 4, -1, 2, 1, -5, 4]

solution = maximum_subarray(nums=nums)
print(solution)

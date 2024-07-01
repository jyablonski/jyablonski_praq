# given integer list nums, find continuous ubarray which has the largest sum and return it


# initialize max sub to the first element just to set it to something
# set current sum to 0
# iterate through every item in the array
# if the current sum from previous loop is negative then set it back to 0
# then add the current value to current sum, and then recalculate max sub using that
def maximum_subarray(nums: list[int]) -> int:
    # initialize our max sub with the first value
    # because these values can be < 0, we cant use 0 here.
    max_sub = nums[0]
    current_sum = 0

    # loop through every value in nums
    for value in nums:
        if current_sum < 0:
            current_sum = 0

        # add current value to current sum
        current_sum += value

        # calculate new potential max subarray val
        max_sub = max(max_sub, current_sum)

    return max_sub


nums = [-2, 1, -3, 4, -1, 2, 1, -5, 4]

solution = maximum_subarray(nums=nums)
print(solution)

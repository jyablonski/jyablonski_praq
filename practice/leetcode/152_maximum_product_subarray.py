# given integer array nums, find the contiguous subarray within an array which has the largest product


def solution(nums: list[int]) -> int:
    max_so_far = nums[0]
    min_so_far = nums[0]
    max_product = nums[0]

    # skip the first number because we have to set all of the constants to it
    for num in nums[1:]:
        # when we encounter a negative, flip min and max
        if num < 0:
            max_so_far, min_so_far = min_so_far, max_so_far

        # always re-calculate min and max which is basically cehcking for whether
        # we want to keep re-using the same subarray, or whether we want to start
        # fresh with num
        max_so_far = max(num, num * max_so_far)
        min_so_far = min(num, num * min_so_far)

        # max product is always just a max of our return variable and the current max_so_far
        max_product = max(max_product, max_so_far)

    return max_product


nums = [2, 3, -2, 4, 7, -3, 4, 2]
# solution = 2 * 3 has the largest product 6
solution(nums=nums)

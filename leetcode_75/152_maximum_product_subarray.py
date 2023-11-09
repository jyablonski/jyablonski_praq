# given integer array nums, find the contiguous ubarray within an array which has the largest product


# THIS IS WRONG, DIDNT FINISH
def maximum_subarray(nums: list[int]):
    max_product = nums[0] * nums[1]
    current_product = 0
    l = 0
    r = 1

    for value in range(len(nums) - 1):
        print(f"left {nums[l]} right {nums[r]}")
        current_product = nums[l] * nums[r]

        max_product = max(current_product, max_product)
        l += 1
        r += 1
        # current_product

    return max_product


nums = [2, 3, -2, 4, 7, -3, 4, 2]
# solution = 2 * 3 has the largest product 6
solution = maximum_subarray(nums=nums)

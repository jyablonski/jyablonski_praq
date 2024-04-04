def binary_search(nums: list[int], target: int) -> int:
    l = 0
    r = len(nums) - 1

    while l <= r:
        mid = (l + r) // 2

        if nums[mid] == target:
            return mid

        if nums[mid] > target:
            r = mid - 1
        else:
            l = mid + 1

    return -1


sorted_array = [100, 200, 300, 500, 700, 900, 1100, 1300, 1500]
target_value = 1300

result_index = binary_search(sorted_array, target_value)

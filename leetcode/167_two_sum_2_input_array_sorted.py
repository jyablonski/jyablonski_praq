# Given a 1-indexed array of integers numbers that is already sorted in non-decreasing order,
# find two numbers such that they add up to a specific target number. Let these two numbers be
# numbers[index1] and numbers[index2] where 1 <= index1 < index2 <= numbers.length.

# Return the indices of the two numbers, index1 and index2, added by one as an integer array [index1, index2] of length 2.

# The tests are generated such that there is exactly one solution. You may not use the same element twice.

# Your solution must use only constant extra space.


# not much to it. easy as fuck boi
# time complexity o(n) and space complexity o(1)
def solution(nums: list[int], target: int) -> list[int]:
    len_n = len(nums)
    left = 0
    right = len_n - 1

    while left < right:
        if nums[left] + nums[right] > target:
            right -= 1
        elif nums[left] + nums[right] < target:
            left += 1
        else:
            return [left + 1, right + 1]

    # dont have to return anything, we're guaranteed a solution


nums1 = [2, 7, 11, 15]
target1 = 9

nums2 = [2, 3, 4]
target2 = 6


solution(nums=nums1, target=target1)
solution(nums=nums2, target=target2)


def binary_search(nums: list[int], target: int) -> int:
    # nums.sort()
    n = len(nums)
    left = 0
    right = n - 1

    while left <= right:
        mid = (left + right) // 2

        if nums[mid] == target:
            return mid

        if nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    return -1

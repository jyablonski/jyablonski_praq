# Given an array of integers nums sorted in non-decreasing order, find the starting
# and ending position of a given target value.

# If target is not found in the array, return [-1, -1].

# You must write an algorithm with O(log n) runtime complexity.

# ya fuck this, i really cannot be bothered. solution involves multiple sets
# of binary search or something - grats
def solution(nums: list[int], target: int) -> list[int]:
    n = len(nums)

    # if n == 1:
    #     return [nums[0]]
    left = 0
    right = n - 1

    while left < right:
        mid = (left + right) // 2

        if nums[mid] > target:
            right = mid - 1

        elif nums[mid] < target:
            left = mid + 1

        else:
            if nums[mid - 1] == target:
                return [mid - 1, mid]
            else:
                return [mid, mid + 1]

    return [-1, -1]


nums1 = [5, 7, 7, 8, 8, 10]
target1 = 8

nums2 = [5, 7, 7, 8, 8, 10]
target2 = 6

solution(nums=nums1, target=target1)
solution(nums=nums2, target=target2)

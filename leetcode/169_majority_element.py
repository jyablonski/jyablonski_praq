def solution(nums: list[int]) -> int:
    nums = sorted(nums)

    return nums[len(nums) // 2]


nums = [3, 2, 3]
nums2 = [2, 2, 1, 1, 1, 2, 2]
nums3 = [1, 1, 1, 2, 3, 4, 5, 6, 7]

solution(nums)
solution(nums2)
solution(nums3)

# couple tricks here
def solution(nums: list[int]) -> int:
    l = 1

    for r in range(1, len(nums)):
        if nums[r] != nums[r - 1]:
            nums[l] = nums[r]
            l += 1

    return l


nums1 = [1, 1, 2]
nums2 = [0, 0, 1, 1, 1, 2, 2, 3, 3, 4]

solution(nums1)
solution(nums2)


for i in range(1, 3):
    print(nums1[i])

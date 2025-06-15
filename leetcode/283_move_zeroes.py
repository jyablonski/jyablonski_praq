# Given an integer array nums, move all 0's to the end of it while maintaining the relative order of the non-zero elements.
# Note that you must do this in-place without making a copy of the array.


# o(n) time complexity because we have to iterate through the whole list once
def solution(nums: list[int]) -> None:
    left = 0

    # we iterate through the entire list
    # and if nums[i] > 0 then we set nums[left] = nums[i] and increment left pter
    for i in range(len(nums)):
        if nums[i] != 0:
            nums[left] = nums[i]
            left += 1

    # backfill the rest of the values at and after left with 0
    while left < len(nums):
        nums[left] = 0
        left += 1

    print(f"final nums {nums}")
    return None


nums1 = [0, 1, 0, 3, 12]
nums2 = [0]

print(solution(nums=nums1))
print(solution(nums=nums2))

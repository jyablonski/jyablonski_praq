# Given an integer array nums, return the number of triplets chosen from the array that
# can make triangles if we take them as side lengths of a triangle.


# another o^2 time complexity one to loop through the outer i loop, and then have to do
# 2 pter approach in the while loop runs in o(n) time. o(n) * o(n) = o^2
def solution(nums: list[int]) -> int:
    # nums.sort() runs in O(n log n) time.
    nums.sort()
    nums_len = len(nums)
    num_combos = 0

    # iterate backwards from largest value to the 2nd index, because we set j = k - 1
    for i in range(nums_len - 1, 1, -1):
        left = 0
        right = i - 1

        while left < right:
            if nums[left] + nums[right] > nums[i]:
                print(f"Found combo for {nums[left]} + {nums[right]} > {nums[i]}")

                # If nums[i] + nums[j] > nums[k], then all elements between i and j satisfy
                num_combos += right - left
                print(f"Num combos is now {num_combos}")

                # shift j down 1 to allow us to explore potential new pairs
                right -= 1
            else:
                left += 1

    return num_combos


nums1 = [2, 2, 3, 4]
nums2 = [4, 2, 3, 4]

solution(nums=nums1)

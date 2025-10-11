# Given an integer array nums, return the length of the longest strictly increasing subsequence.

import bisect


# O(n log n) solution using binary search to efficiently break the problem down
def solution(nums: list[int]) -> int:
    sub = []

    for num in nums:
        print(f"Starting Sub is: {sub}")
        # binary search to find where this number would fit in sub to keep it sorted
        idx = bisect.bisect_left(sub, num)

        # The number is larger than all elements in sub, so we can extend the longest
        # subsequence found so far and append the current value
        if idx == len(sub):
            sub.append(num)

        # the number is smaller, so we can replace sub[idx] to create a better
        # subsequence of that length and give more room for future extensions
        else:
            sub[idx] = num

        print(f"    -> Sub is now: {sub}")

    return len(sub)


nums1 = [10, 9, 2, 5, 3, 7, 101, 18]
nums2 = [0, 1, 0, 3, 2, 3]

solution(nums=nums1)
solution(nums=nums2)


l1 = [100, 200, 300, 500, 1000]

for i in range(len(l1)):
    print(f"Index {i}")
    for j in range(i):
        print(f"J value is {l1[j]} and i is {l1[i]}")


# Starting Sub is: []
#     -> Sub is now: [10]
# Starting Sub is: [10]
#     -> Sub is now: [9]
# Starting Sub is: [9]
#     -> Sub is now: [2]
# Starting Sub is: [2]
#     -> Sub is now: [2, 5]
# Starting Sub is: [2, 5]
#     -> Sub is now: [2, 3]
# Starting Sub is: [2, 3]
#     -> Sub is now: [2, 3, 7]
# Starting Sub is: [2, 3, 7]
#     -> Sub is now: [2, 3, 7, 101]
# Starting Sub is: [2, 3, 7, 101]
#     -> Sub is now: [2, 3, 7, 18]

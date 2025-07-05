# Given an integer array nums, return the length of the longest strictly increasing subsequence.

import bisect


# O(n^2) solution
def solution(nums: list[int]) -> int:
    n = len(nums)
    dp = [1] * n

    for i in range(n):
        for j in range(i):
            if nums[j] < nums[i]:
                dp[i] = max(dp[i], dp[j] + 1)

    print(dp)
    return max(dp)


nums1 = [10, 9, 2, 5, 3, 7, 101, 18]
nums2 = [0, 1, 0, 3, 2, 3]

solution(nums=nums1)
solution(nums=nums2)


# O(n log n) solution
class Solution:
    def lengthOfLIS(self, nums: list[int]) -> int:
        sub = []

        for num in nums:
            idx = bisect.bisect_left(sub, num)
            if idx == len(sub):
                sub.append(num)
            else:
                sub[idx] = num

        return len(sub)


l1 = [100, 200, 300, 500, 1000]

for i in range(len(l1)):
    print(f"Index {i}")
    for j in range(i):
        print(f"J Loop {j} because {i}")

# Given an integer array nums and an integer k
# return the k most frequent elements. You may return the answer in any order.

import heapq
from collections import Counter


def solution(nums: list[int], k: int) -> list[int]:
    if not nums:
        return []

    # count frequency of characters w/ Counter and setup heap
    freq_map = Counter(nums)
    heap = []

    # iterate through the counts, and store them to the heap
    # as a tuple of (freq, num)
    for num, freq in freq_map.items():
        heapq.heappush(heap, (freq, num))

        # if our heap is larger than k, we pop from the heap
        # which removes the lowest count
        if len(heap) > k:
            heapq.heappop(heap)

    return [num for (_, num) in heap]


nums1 = [1, 1, 1, 2, 2, 3]
k1 = 2

nums2 = [1]
k2 = 1

solution(nums=nums1, k=k1)
solution(nums=nums2, k=k2)

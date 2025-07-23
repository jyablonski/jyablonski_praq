# Given an integer array nums and an integer k, return the kth largest element in the array.
# Note that it is the kth largest element in the sorted order, not the kth distinct element.
# Can you solve it without sorting?

# sorting would take n log n time, but heaps can do this in n log k time
import heapq


# use a heap to keep track of the largest k elements
# if using a min heap, it will store these elements in sorted order
# and we can just iterate through nums and return heap[0] at the end
# time complexity o(n log k)
def solution(nums: list[int], k: int) -> int:
    if not nums:
        return 0

    # We maintain a min-heap of size k, which always stores
    # the k largest elements seen so far
    heap = []

    # we only insert into `heap` when the array size is less than k,
    # or if we find a new min value to replace
    for num in nums:
        if len(heap) < k:
            heapq.heappush(heap, num)

        # if we find a new value that's greater than the current
        # smallest value in the heap, then we pop that heap value
        # and insert the value we're on. the heap will shuffle things around
        # to maintain order afterwards
        elif num > heap[0]:
            print(f"heap before: {heap}")
            heapq.heappushpop(heap, num)
            print(f"heap after: {heap}")

    print(heap)
    return heap[0]


nums1 = [3, 2, 1, 5, 6, 4]
k1 = 2

nums2 = [3, 2, 3, 1, 2, 4, 5, 5, 6]
k2 = 4

solution(nums=nums1, k=k1)
solution(nums=nums2, k=k2)

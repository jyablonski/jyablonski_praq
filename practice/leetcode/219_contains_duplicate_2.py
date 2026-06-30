# Given an integer array nums and an integer k, return true if there are two distinct
# indices i and j in the array such that nums[i] == nums[j] and abs(i - j) <= k.

# find at least 2 elements in the array that are equal and are at most `k` apart from each other


# trick here is to use a dictionary for o(n) time complexity, as opposed to a
# i and j double for loop
def solution(nums: list[int], k: int) -> bool:
    # use dict to keep track of items you've iterated over
    index_map = {}

    # loop through nums
    for i, num in enumerate(nums):
        # if num already in index_map and the current index is <= that index, then return true
        if num in index_map and i - index_map[num] <= k:
            return True

        # add num as a key to the index_map if it's new or replace it if it already
        # existed
        index_map[num] = i

    return False


nums1 = [1, 2, 3, 1]
k1 = 3

nums2 = [1, 0, 1, 1]
k2 = 1

nums3 = [1, 2, 3, 1, 2, 3]
k3 = 2

solution(nums=nums1, k=k1)
solution(nums=nums2, k=k2)
solution(nums=nums3, k=k3)

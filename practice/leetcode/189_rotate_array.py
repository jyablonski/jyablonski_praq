# Given an integer array nums, rotate the array to the right by k steps, where k is non-negative.

# Input: [1, 2, 3, 4, 5, 6, 7], k = 3
# Output: [5, 6, 7, 1, 2, 3, 4]

# optimal solution in o(n) time is to swap all elements twice
# To rotate the array right by k:
#   Reverse the entire array => [7, 6, 5, 4, 3, 2, 1]
#   Reverse the first k elements => [5, 6, 7, 4, 3, 2, 1]
#   Reverse the remaining n-k elements => [5, 6, 7, 1, 2, 3, 4]


# Rotating right by k means:
#   The last k elements should come to the front
#   The first n-k elements should move to the back
def solution(nums: list[int], k: int) -> None:
    n = len(nums)
    k %= n

    def reverse(start, end):
        while start < end:
            nums[start], nums[end] = nums[end], nums[start]
            start += 1
            end -= 1

    # reverse whole array
    reverse(0, n - 1)

    # reverse the first k elements
    reverse(0, k - 1)

    # reverse the rest
    reverse(k, n - 1)

    print(nums)


nums1 = [1, 2, 3, 4, 5, 6, 7]
k1 = 3

nums2 = [-1, -100, 3, 99]
k2 = 2

solution(nums=nums1, k=k1)
solution(nums=nums2, k=k1)

# Given an array of integers nums and an integer k, return the number of contiguous
# subarrays where the product of all the elements in the subarray is strictly less than k.

# time complexity o(n) because we just iterate through all of nums
# space complexity o(1)
def solution(nums: list[int], k: int) -> int:
    # product has to be < k, so if k is 0 or 1 then
    # we just return false
    if k <= 1:
        return 0

    # setup pointers and product with 1 because we'll be
    # multiplying & dividing
    start = 0
    product = 1
    count = 0

    for end in range(len(nums)):
        product *= nums[end]

        # use while loop becuase we could have to kick out multiple items
        # during an iteration to get product < k again
        # divide by nums[start] and increment start by 1
        while product >= k:
            product //= nums[start]
            start += 1

        # always increment count by the size of hte window, because that window
        # includes a contiguous subarray whose product of all elements is < k
        count += end - start + 1

    return count


nums1 = [10, 5, 2, 6]
nums2 = [1, 2, 3]

k1 = 100
k2 = 0

solution(nums=nums1, k=k1)
solution(nums=nums2, k=k2)

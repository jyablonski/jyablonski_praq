# Given an array of integers nums and an integer k, return the number of contiguous
# subarrays where the product of all the elements in the subarray is strictly less than k.


def solution(nums: list[int], k: int) -> int:
    if k <= 1:
        return 0

    start = 0
    product = 1
    count = 0

    for end in range(len(nums)):
        product *= nums[end]

        while product >= k:
            print(
                f"lowering product {product} by / {nums[start]} and adjusting adding 1 to start"
            )
            product //= nums[start]
            start += 1

        print(f"end is {end}, start is {start}. adding {end - start + 1} to {count}")
        count += end - start + 1

    return count


nums1 = [10, 5, 2, 6]
nums2 = [1, 2, 3]

k1 = 100
k2 = 0

solution(nums=nums1, k=k1)
solution(nums=nums2, k=k2)

# Given a binary array nums and an integer k, return the maximum number of consecutive 1's in
# the array if you can flip at most k 0's.


def solution(nums: list[int], k: int) -> int:
    res = 0
    start = 0
    count_0 = 0
    n = len(nums)

    # iterate through and baiscally just track the 0s
    for end in range(n):
        if nums[end] == 0:
            count_0 += 1

        # if we ever end up with more 0s than k, then we have to adjust the window
        # by moving start pter, and decrementing
        while count_0 > k:
            if nums[start] == 0:
                count_0 -= 1

            start += 1

        res = max(res, end - start + 1)

    return res


nums1 = [1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0]
k1 = 2

nums2 = [0, 0, 1, 1, 0, 0, 1, 1, 1, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1]
k2 = 3

solution(nums=nums1, k=k1)
solution(nums=nums2, k=k2)

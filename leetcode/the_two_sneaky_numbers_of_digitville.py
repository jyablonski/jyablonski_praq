# In the town of Digitville, there was a list of numbers called nums containing integers from 0 to n - 1.
# Each number was supposed to appear exactly once in the list, however, two mischievous numbers sneaked
# in an additional time, making the list longer than usual.

# As the town detective, your task is to find these two sneaky numbers. Return an array of size two
# containing the two numbers (in any order), so peace can return to Digitville.


def solution(nums: list[int]) -> list[int]:
    visited = set()
    res = []

    for num in nums:
        if num not in visited:
            visited.add(num)
        else:
            res.append(num)

    return res


nums1 = [0, 1, 1, 0]
nums2 = [0, 3, 2, 1, 3, 2]

solution(nums=nums1)
solution(nums=nums2)

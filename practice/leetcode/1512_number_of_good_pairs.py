# Given an array of integers nums, return the number of good pairs.

# A pair (i, j) is called good if nums[i] == nums[j] and i < j.


# this is an ok solution but it's o(n^2), we can do better
def solution(nums: list[int]) -> int:
    pairs = []

    for i in range(0, len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] == nums[j]:
                print(f"{nums[i]} == {nums[j]} on loop {i}, {j}")
                pair = (i, j)
                pairs.append(pair)

    print(pairs)
    return len(pairs)


nums = [1, 2, 3, 1, 1, 3]
nums2 = [1, 1, 1, 1]

solution(nums=nums)
solution(nums=nums2)


def solution_v2(nums: list[int]) -> int:
    pairs = {}
    res = 0

    for n in nums:
        if n in pairs:
            res += pairs[n]
            pairs[n] += 1
        else:
            pairs[n] = 1

    print(pairs)
    return res


solution_v2(nums=nums)
solution_v2(nums=nums2)

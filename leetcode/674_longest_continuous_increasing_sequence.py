# Given an unsorted array of integers nums, return the length of the longest continuous increasing
# subsequence (i.e. subarray). The subsequence must be strictly increasing.

# A continuous increasing subsequence is defined by two indices l and r (l < r) such that it is
# [nums[l], nums[l + 1], ..., nums[r - 1], nums[r]] and for each l <= i < r, nums[i] < nums[i + 1].


def solution(nums: list[int]) -> int:
    # handle edge case if there's only 1 value
    if len(nums) == 1:
        return 1

    max_seq = 1

    # set default to 1 because each unique digit counts
    cur_seq = 1

    # loop through and compare current value with next value to see if we can
    # increase the length of the current increasing subsequence
    for index in range(len(nums) - 1):
        if nums[index] < nums[index + 1]:
            cur_seq += 1
        else:
            # if we cant, reset it back to 1
            cur_seq = 1

        # run the comparison to find a potential new max subsequence
        max_seq = max(max_seq, cur_seq)

    return max_seq


nums1 = [1, 3, 5, 4, 7]
nums2 = [2, 2, 2, 2, 2]
nums3 = [1]

solution(nums=nums1)
solution(nums=nums2)
solution(nums=nums3)

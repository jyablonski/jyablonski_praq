# Given an integer array nums of size n, return the number with the
# value closest to 0 in nums. If there are multiple answers, return
# the number with the largest value.


# this solution works but no reason to store a dictionary, you can
# perform the loop and make the comparisons on the fly
def solution(nums: list[int]) -> int:
    res = {}

    # loop through and add the differential for each item to a dictionary
    for value in nums:
        current_res = abs(value)
        res[value] = current_res

    # find the min differential
    min_value = min(res.values())

    # find the largest key for any items whose value is == that min value
    min_key = max(k for k, v in res.items() if v == min_value)
    return min_key


# this is the better solution
def solution_v2(nums: list[int]) -> int:
    # initialize closest to something
    closest = nums[0]

    for x in nums:
        # the first part just checks if the current val we're on is closer than
        # what we currently have

        # the second part checks that if we first came across -1, and then
        # are on 1, then we replace closest with 1 because it's the larger
        # value, even though both differentials are 1.
        if abs(x) < abs(closest) or (abs(x) == abs(closest) and x > closest):
            closest = x

    return closest


nums1 = [-4, -2, 1, 4, 8]
nums2 = [2, -1, 1]
nums3 = [-10000, -10000]

solution(nums=nums1)
solution(nums=nums2)
solution(nums=nums3)

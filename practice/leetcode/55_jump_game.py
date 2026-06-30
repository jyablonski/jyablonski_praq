# You are given an integer array nums. You are initially positioned at the array's first index
# and each element in the array represents your maximum jump length at that position.

# Return true if you can reach the last index, or false otherwise.


# use greedy algorithm, no need for backtracking. just iterate through the loop
# and keep track of your max reach which is i + nums[i] and if that max reach
# is ever < the current index, you return false
def solution(nums: list[int]) -> bool:
    max_reach = 0

    for i in range(len(nums)):
        # if the current index is ever > than our max reach,
        # we return False because we cant get here
        if i > max_reach:
            return False

        # max reach is the max we can jump to
        # current index + the value at that current index
        max_reach = max(max_reach, i + nums[i])

    # if you can iterate through the entire loop then youre good
    return True


nums1 = [2, 3, 1, 1, 4]
nums2 = [3, 2, 1, 0, 4]


solution(nums=nums1)
solution(nums=nums2)

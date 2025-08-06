# You are given a 0-indexed array of integers nums of length n.
# you are initially positioned at nums[0].

# Each element nums[i] represents the maximum length of a forward jump from index i.
# In other words, if you are at nums[i], you can jump to any nums[i + j] where:

# 0 <= j <= nums[i] and
# i + j < n
# Return the minimum number of jumps to reach nums[n - 1]. The test cases are
# generated such that you can reach nums[n - 1].

# time complexity o(n) greedy solution with o(1) space complexity
# we just iterate through nums and always calculate the furthest we can reach,
# and we can keep track of how many jumps we've made with an `end` variable
# that gets updated whenever our current index == `end`
def solution(nums: list[int]) -> int:
    n = len(nums)

    if n <= 1:
        return 0

    jumps = 0
    end = 0
    farthest = 0

    # no need to process the last index
    for i in range(n - 1):
        farthest = max(farthest, i + nums[i])

        # if we've reached the end of the current jump's range, make a jump
        if i == end:
            jumps += 1
            end = farthest

            # once end is >= the end of the list, we have our answer
            if end >= n - 1:
                return jumps


nums1 = [2, 3, 1, 1, 4]
nums2 = [2, 3, 0, 1, 4]

solution(nums=nums1)
solution(nums=nums2)


def solution(nums: list[int]) -> int:
    n = len(nums)
    end = n - 1

    for i in range(n):
        num_range = nums[i : nums[i + nums[i]]]
        max_num_reach = max(num_range)

        if i + max_num_reach >= end:
            return i + 1

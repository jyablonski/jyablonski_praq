# Given an array nums of distinct integers, return all the possible
# permutations. You can return the answer in any order

from itertools import permutations


# this is the easy way, this function does it for you
def solution(nums: list[int]) -> list[list[int]]:
    return [list(p) for p in permutations(nums)]


nums1 = [1, 2, 3]
nums2 = [0, 1]
nums3 = [1]

solution1 = solution(nums=nums1)
solution2 = solution(nums=nums2)
solution3 = solution(nums=nums3)


# need a way to systematically generate different orderings of the numbers.
def solution(nums: list[int]):

    # define a helper function to construct permutations step by step.
    def backtrack(path, remaining):
        print(f"starting new loop for path {path}")

        # base case
        if not remaining:
            print(f"adding {path} to result {result}")
            result.append(path)
            return

        # recursive case
        # for each number in remmaining, pick 1 and add it to path
        # then remove the picked number from remaining
        # and recursively call backtrack on it with the updated values
        for i in range(len(remaining)):
            print(f"running backtrack on {remaining}, {path}")
            backtrack(path + [remaining[i]], remaining[:i] + remaining[i + 1 :])
            # print(f"now {remaining}, {path}")

    result = []
    backtrack([], nums)
    return result

# Given an integer array nums of unique elements, return all possible subsets (the power set).

# The solution set must not contain duplicate subsets. Return the solution in any order.


def solution(nums: list[int]) -> list[list[int]]:
    def dfs(index, path):
        # When index reaches the end of the list, we've made a complete decision for each element:
        # include it or not.
        if index == len(nums):
            result.append(path[:])

        # core idea: at each index, make 2 choices to explore all possible combos:
        # include nums[index]
        path.append(nums[index])
        dfs(index + 1, path)

        # and dont include nums[index]
        path.pop()
        dfs(index + 1, path)

    result = []
    dfs(0, [])
    return result


nums = [1, 2, 3]

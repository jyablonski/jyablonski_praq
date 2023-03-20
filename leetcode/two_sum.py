# 2 sum - return the indicies of the 2 values in the list that add up to the target integer.
nums_list = [14, 21, 34, 44]
target_int = 55


# 2 sum trick is to iterate through the nums list and append values that you've traversed in a dictionary
def solution(nums, target):
    dict1 = {}

    for k, v in enumerate(nums):
        diff = target - v
        # differential = number we want - the value we're currently on.
        # if the missing number is already in the numbers we've iterated through, we have a solution.

        if diff in dict1:
            return [dict1[diff], k]

        # else add the value we just traversed to the dictionary as a key, with the index as the value.
        dict1[v] = k


solution(nums_list, target_int)

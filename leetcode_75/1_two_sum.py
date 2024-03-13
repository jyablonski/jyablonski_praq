# Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.
# You may assume that each input would have exactly one solution, and you may not use the same element twice.
# You can return the answer in any order.

# initialize an empty dictionary to store key value pairs of the items we've iterated through
# store the VALUE of the item as the dictionary key, and the index of the item as the dictionary value.
# the trick here is as we iterate through nums, we can caluclate a `diff` by subtracting the current
# value from the target value we want to find, and then check if that diff exists as a key in the
# passed_items dictionary we made.  if it does, then we found our match and can return it immediately.
# if it doesnt exist, then we add that current pair to the `passed_items`


def solution(nums: list[int], target: int):
    passed_items = {}

    for key, value in enumerate(nums):
        diff = target - value

        if diff in passed_items:
            return [passed_items[diff], key]

        # after we visit it, and didnt find a solution, then add it to
        # the dictionary for our passed items
        else:
            passed_items[value] = key

    return None


nums = [2, 2, 1, 5, 3]
target = 6

value = solution(nums=nums, target=target)


passed_values = {}

for key, value in enumerate(nums):
    diff = target - value

    if diff in passed_values:
        return [passed_values[diff], key]

    else:
        passed_values[value] = value

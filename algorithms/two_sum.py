from typing import List

nums = [102, 365, 454, 819]
target = 819

# PROBLEM STATEMENT
# given array of `nums`` and integer `target`, return the indicies of the 2 numbers
# in `nums` that add up to `target`

# the trick is to identify you're dealing with indicies and values, and use a dictionary.
# then you can keep track of which pairs you've iterated through.

# we're guaranteed to have a pair


def two_sum(nums: List[int], target: int) -> List[int]:
    passed_items = {}

    for i, v in enumerate(nums):
        diff = target - v

        if diff in passed_items:
            return [passed_items[diff], i]
        else:
            passed_items[v] = i


# returns [1, 2]
print(two_sum(nums, target))

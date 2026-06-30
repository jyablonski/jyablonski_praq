# Given a non-empty array of integers nums, every element appears twice except for one. Find that single one.

# You must implement a solution with a linear runtime complexity and use only constant extra space.


# utilizes the XOR bitwise operator to find the number that appears only once in the list
#  where every other number appears exactly twice.
def singleNumber(nums: list[int]) -> int:
    # initialize variable to store our result
    result = 0

    # loop through the list and if the same value pops up twice,
    # use the XOR operator `^`w to cancel it out
    for value in nums:
        result ^= value

    return result


nums = [4, 1, 2, 1, 2]

singleNumber(nums=nums)


# the solution with the set data structure ;-)
def singleNumber(nums: list[int]) -> int:
    passed_items = set()

    for value in nums:
        if value not in passed_items:
            passed_items.add(value)
        else:
            passed_items.remove(value)

    # There should be exactly one element left in the set
    return next(iter(passed_items))


result = 0
nums = [3, 2, 4, 2]

# this makes result return 7 here, because both 2s got cancelled out
# and it sums the rest of the values together apparently.
for value in nums:
    result ^= value

# Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.
# You may assume that each input would have exactly one solution, and you may not use the same element twice.
# You can return the answer in any order.

# initialize an empty dictionary to store key value pairs of the items we've iterated through
# store the VALUE of the item as the dictionary key, and the index of the item as the dictionary value.
# the trick here is as we iterate through nums, we can caluclate a `diff` by subtracting the current
# value from the target value we want to find, and then check if that diff exists as a key in the
# passed_items dictionary we made.  if it does, then we found our match and can return it immediately.
# if it doesnt exist, then we add that current pair to the `passed_items`


# time complexity is o(n); we have to iterate through the list 1 by 1 til we find a solution
# the dictionary operations are o(1) (checking, insewrting, and retrieving values)
# my_dict[value] will return the key for the value
def solution(nums: list[int], target: int):
    passed_items = {}

    for key, value in enumerate(nums):
        diff = target - value

        if diff in passed_items:
            # if it's in there then we have a match
            # return a list of that index, and the key we're on which is the current index
            print(passed_items)
            return [passed_items[diff], key]

        # after we visit it, and didnt find a solution, then store the key pair to
        # the dictionary where the key is the value, and the value is the index we're on
        else:
            passed_items[value] = key

    return None


nums = [2, 2, 1, 5, 3]
target = 6

value = solution(nums=nums, target=target)


# if the input array is sorted


def solution(nums: list[int], target: int) -> bool:
    left = 0
    right = len(nums) - 1

    while left < right:
        current_sum = nums[left] + nums[right]
        print(f"Checking {left} ({nums[left]}) and {right} ({nums[right]})")
        if current_sum == target:
            return True

        if current_sum < target:
            left += 1
        else:
            right -= 1

    return None


nums = [1, 2, 3, 6, 7, 8]
target = 5

b = solution(nums=nums, target=target)

# Consider using the two-pointer technique for questions that involve searching for a pair (or more) of items in an array that meet a certain criteria.
# Examples:

#     Finding a pair of items that sum to a given target in an array.
#     Finding a triplet of items that sum to 0 in a given array.
#     Finding the maximum amount of water that can be held between two array items representing wall heights.

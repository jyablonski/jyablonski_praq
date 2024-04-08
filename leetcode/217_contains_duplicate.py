# given array of nums:
#    return true if any value appears at least twice
#    return false if every item is distinct


def contains_duplicate(nums: list[int]) -> bool:
    passed_values = set()
    # passed_values = {} <--- this is actually a dict
    # same o(n) time complexity but using more memory

    for value in nums:
        if value not in passed_values:
            passed_values.add(value)
        else:
            return True

    return False


nums_true = [1, 2, 3, 1]
nums_false = [1, 2, 3, 4]

# should fail out immediately on the 2nd item
nums = [1, 1, 1, 3, 3, 4, 3, 2, 4, 2]

solution_true = contains_duplicate(nums_true)
print(solution_true)

solution_false = contains_duplicate(nums_false)
print(solution_false)

solution = contains_duplicate(nums)
print(solution_false)

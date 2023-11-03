def solution(nums: list[int], target: int):
    passed_items = {}

    for key, value in enumerate(nums):
        diff = target - value

        if diff in passed_items:
            print(f"Found Solution")
            return [passed_items[diff], key]

        # after we visit it, and didnt find a solution, then add it to
        # the dictionary for our passed items
        else:
            passed_items[value] = key

    print(f"Target {target} not computable by a pair of values in nums")
    return None


nums = [2, 1, 5, 3]
target = 6

value = solution(nums=nums, target=target)

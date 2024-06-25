# two sum
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


# fizzbuzz
def fizz_buzz(n: int) -> list[str]:
    result_list = []

    for i in range(1, n + 1):
        output = ""
        if i % 3 == 0:
            output += "Fizz"

        if i % 5 == 0:
            output += "Buzz"

        if not output:
            output = str(i)

        result_list.append(output)

    return result_list


# house robber
def robber(nums: list[int]) -> int:
    prev_max = 0  # Previous maximum amount stolen
    current_max = 0  # Current maximum amount stolen

    for current_house_value in nums:
        print(
            f"current house value is {current_house_value}, prev_max is {prev_max}, current_max is {current_max}"
        )
        new_max = max(current_house_value + prev_max, current_max)
        prev_max = current_max

        print(f"setting current max to {new_max}")
        current_max = new_max

    return current_max


# climbing stairs
def solution(n: int) -> int:
    if n in (0, 1):
        return 1

    # initialize a list to store the number of ways to reach each step
    dp = [0] * (n + 1)

    # set base cases
    dp[0] = 1  # 1 way to stay at the start (0 steps)
    dp[1] = 1  # 1 way to climb 1 step

    # calculate the number of ways for each step up to n using the recursive relation
    # this is like a fibonacci sequence adding the previous to values to get the next one
    for i in range(2, n + 1):
        print(f"dp[{i}] = {dp[i - 1]} + {dp[i - 2]}")
        dp[i] = dp[i - 1] + dp[i - 2]

    # return the number of ways to reach the top of the staircase
    return dp[n]


# binary search
def solution(nums: list[int], target: int) -> int:
    l = 0
    r = len(nums) - 1

    while l <= r:
        mid = (l + r) // 2

        if target == nums[mid]:
            return mid

        if target > nums[mid]:
            l = mid + 1
        else:
            r = mid - 1

    return l


# merge sort
def merge_sort(arr):
    if len(arr) <= 1:
        return arr

    # Divide the array into two halves
    mid = len(arr) // 2
    left_half = arr[:mid]  # up to but not including mid
    right_half = arr[mid:]  # mid and everything after mid

    # Recursively sort both halves
    left_half = merge_sort(left_half)
    right_half = merge_sort(right_half)

    # print(f"mid is {mid}, left is {left_half}, right is {right_half}")
    # Merge the sorted halves
    return merge(left_half, right_half)


def merge(left, right):
    result = []
    i = 0
    j = 0
    print(f"left is {left}")
    print(f"right is {right}")

    # Merge the two halves into a sorted array
    while i < len(left) and j < len(right):
        # print(f"left is {left[i]} and right is {right[j]}")
        if left[i] < right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    # Add remaining elements from left and right halves
    # this is in the event we iterate through all of the left side, but still have
    # elements on the right
    # in that case, we already know that the left and right side were
    result.extend(left[i:])
    result.extend(right[j:])
    return result


# roman integer
def solution(s: str) -> int:
    mapping = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    int_sum = 0
    str_len = len(s)

    for i in range(str_len):
        if (
            i + 1 < str_len  # this is the check to make sure we dont go out of bounds
            and mapping[s[i]] < mapping[s[i + 1]]
        ):
            print(f"subtracting {mapping[s[i]]} from {int_sum}")
            int_sum -= mapping[s[i]]
        else:
            print(f"adding {mapping[s[i]]} to {int_sum}")
            int_sum += mapping[s[i]]

    return int_sum


#

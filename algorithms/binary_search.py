# commonly used algorithm for finding a specific element in a sorted array
def binary_search(arr: list[int], target: int):
    left = 0
    right = len(arr) - 1

    while left <= right:
        mid = left + (right - left) // 2  # find the midpoint
        print(f"mid index is {mid}")

        # if the value at index mid is our target then we're done
        if arr[mid] == target:
            return mid

        # if the value at index mid is > than our target then it's is in the left half
        # and the new upper bound of our binary search should be the element below that
        elif arr[mid] > target:
            right = mid - 1

        # if the value at index mid is < than our target then it's is in the right half
        # and the new lower bound of our binary search should be the element above that
        else:
            left = mid + 1

    return -1


# Example usage
sorted_array = [100, 200, 300, 500, 700, 900, 1100, 1300, 1500]
target_value = 1300

result_index = binary_search(sorted_array, target_value)


def binary_search(arr, target):
    left = 0
    right = len(arr) - 1

    while left <= right:
        print(f"left is at index {left} and right is at index {right}")
        mid = left + (right - left) // 2
        print(f"mid is {mid} w/ value {arr[mid]}")

        if arr[mid] == target:
            print(f"result is index {mid}")
            return mid
        elif arr[mid] > target:
            print(f"arr mid {arr[mid]} is > {target}")
            right = mid - 1
        else:
            print(f"arr mid {arr[mid]}  is < {target}")
            left = mid + 1

    return -1


def binary_search(arr, target):
    left = 0
    right = len(arr) - 1

    while left <= right:
        mid = left + (right - left) // 2

        if arr[mid] == target:
            return mid
        elif arr[mid] > target:
            right = mid - 1
        else:
            left = mid + 1

    return -1

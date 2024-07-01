# merge sort is a divide and conquer sorting algorithm that works to repeatedly
# divide an unsorted array into smaller subarrays, sorting them, and then merging
# them back into a sorted array
# n log n complexity for worst, average, and best case scenarios


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


# Example usage
arr = [38, 27, 43, 6, 9, 82, 10]
sorted_arr = merge_sort(arr)

print("Original array:", arr)
print("Sorted array:", sorted_arr)


test_case = [100, 200, 300, 400, 500]

first_half = test_case[:2]
second_Half = test_case[2:]


### re-typing it out
def merge_sort(arr):
    length = len(arr)
    if length <= 1:
        return arr

    mid = length // 2
    left_half = arr[:mid]
    right_half = arr[mid:]

    left_half = merge_sort(left_half)
    right_half = merge_sort(right_half)

    return merge(left_half, right_half)


def merge(left, right):
    result = []
    i = 0
    j = 0

    while i < len(left) and j < len(right):
        if left[i] < right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    # append the remaining elements of the left and right arrays (or lists) to
    # the result list after the main merge process is complete.
    result.extend(left[i:])
    result.extend(right[j:])

    return result


arr = [38, 27, 43, 6, 9, 82, 10]
sorted_arr = merge_sort(arr)

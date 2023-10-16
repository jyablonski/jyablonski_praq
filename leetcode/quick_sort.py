# quick sort is a recursive element that picks a pivot point to split an input array in half,
# and divides all elements of that array into upper and lower groups
# it then recursively applies the same algorithm onto those upper and lower groups again and again
# until all elements are sorted


# best case time complexity is n log n if partitioning is balanced (you picked a good pivot)
# worst case is n ^ 2 in the event the partitioning is highly unbalanced (you picked a bad pivot)
def quick_sort(arr: list[int]) -> list[int]:
    length = len(arr)
    # nothing to sort
    if length <= 1:
        return arr

    # Choose pivot (middle element in this case)
    # could also be the last element (arr.pop())
    # you have no idea what the best "pivot" could possibly be
    pivot = arr[length // 2]

    lower = [x for x in arr if x < pivot]
    upper = [x for x in arr if x > pivot]

    # pivot is only a list so that we can combine all 3 lists together
    return quick_sort(lower) + [pivot] + quick_sort(upper)


# Example usage
arr = [3, 6, 8, 10, 7, 2, 1]
sorted_arr = quick_sort(arr)

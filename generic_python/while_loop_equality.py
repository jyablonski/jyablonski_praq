# <= “I want to check every index for an exact match”
# <  “I want to narrow down until I have one candidate left”

# while left <= right
# Common in “classic” binary search (finding a target value in a sorted array) when searching for unknown values
# The search space is inclusive on both ends: [left, right].
# you must always check evrey value (left <= right) to ensure you dont miss the one you're looking for.
# Loop stops when left > right.

nums1 = [10, 20, 30, 40, 50]
left = 0
right = len(nums1) - 1
target = 40

while left <= right:
    mid = (left + right) // 2
    print(f"Checking {nums1[mid]}")

    if nums1[mid] == target:
        print(f"Found Index {mid}")
        break
    elif nums1[mid] < target:
        left = mid + 1
    else:
        right = mid - 1

# while left < right
# Often used when you’re searching for a guaranteed value (min, max, first/last occurrence)
# The search space is half-open, in a sense: [left, right] but you always keep at least one element in the loop.
# Loop stops when left == right, meaning you’ve narrowed down to one candidate.
# you're eliminating half the elements every time without actually checking all of them

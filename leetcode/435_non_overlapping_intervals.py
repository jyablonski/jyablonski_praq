# Given an array of intervals intervals where intervals[i] = [starti, endi]
# return the minimum number of intervals you need to remove to make the rest of the intervals non-overlapping.

# Note that intervals which only touch at a point are non-overlapping. For example, [1, 2] and [2, 3] are non-overlapping.


# This question reduces to finding the maximum number of non-overlapping intervals.Once we know that value,
# then we can subtract it from the total number of intervals to get the minimum number of intervals that need to be removed.

# Time Complexity: O(n * logn) where n is the number of intervals due to the sorting step.
# Space Complexity: O(1) since we only initialize two extra variables.


def solution(intervals: list[list[int]]) -> int:
    if not intervals:
        return 0

    # sort all intervals by end time and find max end_time
    # Sorting by the end time allows us to choose the intervals that end the
    # earliest first, which frees up more time for intervals to be included later.
    # this could look like `[[1, 2], [2, 3], [1, 3], [3, 4]]` after
    intervals.sort(key=lambda x: x[1])
    max_end_time = intervals[0][1]

    # count keeps track of how many non-overlapping intervals we have
    count = 1
    n = len(intervals)

    print(f"intervals {intervals} and max end {max_end_time}")
    # then iterate over each one and if current start time is > the last known end time,
    # then they dont overlap and we increment count by 1
    # we skip the first 1 because that's our starting `end`, and the count is already = 1
    for i in range(1, n):
        if intervals[i][0] >= max_end_time:
            # set the new end time
            max_end_time = intervals[i][1]
            count += 1

    # at the end, n - count is the total number of intervals we have minus the # of non-overlapping ones
    # this gives us the total to remove which we return
    print(f"Count is {count}")
    return n - count


intervals1 = [[1, 2], [2, 3], [3, 4], [1, 3]]
intervals2 = [[1, 2], [1, 2], [1, 2]]
intervals3 = [[1, 2], [2, 3]]

solution(intervals=intervals1)
solution(intervals=intervals2)
solution(intervals=intervals3)

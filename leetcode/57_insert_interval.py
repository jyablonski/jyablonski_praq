# You are given an array of non-overlapping intervals intervals where intervals[i] = [starti, endi]
# represent the start and the end of the ith interval and intervals is sorted in ascending order
# by starti. You are also given an interval newInterval = [start, end] that represents the start
# and end of another interval.

# Insert newInterval into intervals such that intervals is still sorted in ascending order by starti
# and intervals still does not have any overlapping intervals (merge overlapping intervals if necessary).

# Return intervals after the insertion.

# Note that you don't need to modify intervals in-place. You can make a new array and return it.

# Time Complexity: O(n) where n is the number of intervals.
# Space Complexity: O(n) for the merged output array.


def solution(intervals: list[list[int]], newInterval: list[int]) -> list[list[int]]:
    merged = []
    i = 0
    n = len(intervals)

    # This solution operates in 3 phases:
    # Add all the intervals starting before newInterval to merged.
    while i < n and intervals[i][1] < newInterval[0]:
        merged.append(intervals[i])
        i += 1

    print(f"merged phase 1 {merged}")
    # Merge all overlapping intervals into newInterval inplace and add it to merged after
    while i < n and intervals[i][0] <= newInterval[1]:
        # find min start time
        newInterval[0] = min(intervals[i][0], newInterval[0])

        # find max end time
        newInterval[1] = max(intervals[i][1], newInterval[1])
        i += 1

    merged.append(newInterval)
    print(f"merged phase 2 {merged}")

    # Add all the intervals starting after newInterval to merged.
    for j in range(i, n):
        merged.append(intervals[j])

    print(f"merged phase 3 (final) {merged}")
    return merged


intervals1 = [[1, 3], [6, 9]]
newInterval1 = [2, 5]

intervals2 = [[1, 2], [3, 5], [6, 7], [8, 10], [12, 16]]
newInterval2 = [4, 8]


solution(intervals=intervals1, newInterval=newInterval1)
solution(intervals=intervals2, newInterval=newInterval2)

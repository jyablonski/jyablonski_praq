# Given an array of intervals where intervals[i] = [starti, endi], merge
# all overlapping intervals, and return an array of the non-overlapping
# intervals that cover all the intervals in the input.

# Since this question involves merging intervals that overlap, we want to first sort the intervals by their start time.


def solution(intervals: list[list[int]]) -> list[list[int]]:
    sortedIntervals = sorted(intervals, key=lambda x: x[0])
    merged = []

    for interval in sortedIntervals:
        # if it's the first iteration, or if the current interval start time
        # is > the end time of the last interval, then lets create a new interval
        # and add this one to `merged`
        if not merged or interval[0] > merged[-1][1]:
            merged.append(interval)

        # otherwise, attempt to update the last interval's end time in `merged` w/
        # the max of its current end time, or the current interval's end time
        else:
            merged[-1][1] = max(interval[1], merged[-1][1])

    return merged


intervals1 = [[1, 3], [2, 6], [8, 10], [15, 18]]
intervals2 = [[1, 4], [4, 5]]

solution(intervals=intervals1)
solution(intervals=intervals2)

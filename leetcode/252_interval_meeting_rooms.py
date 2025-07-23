# Write a function to check if a person can attend all the meetings scheduled without any time conflicts.
# Given an array intervals, where each element [s1, e1] represents a meeting starting at time s1 and
# ending at time e1, determine if there are any overlapping meetings. If there is no overlap between
# any meetings, return true; otherwise, return false.

# Time Complexity: O(n * logn) where n is the number of intervals due to the sorting step.
# Space Complexity: O(1) since we are not using any extra space.

# By sorting by start time, we ensure that all meetings are arranged chronologically,
# which makes it easy to compare each meeting to the one that comes before it.

# If you don’t sort, the meetings could be in any order, and you might miss overlaps unless
# you compare every pair, which would be O(n²) — much slower.


def solution(intervals: list[list[int]]) -> bool:
    intervals.sort(key=lambda x: x[0])
    print(f"Sorted Intervals: {intervals}")

    for i in range(1, len(intervals)):
        # if the start time of the current meeting is `intervals[i][0] < the end time
        # of the last meeting `intervals[i - 1][1]`, then there's an overlap. return false
        if intervals[i][0] < intervals[i - 1][1]:
            return False

    return True


intervals1 = [(1, 5), (3, 9), (6, 8)]  # overlap
intervals2 = [(10, 12), (6, 9), (13, 15)]  # no overlap

solution(intervals=intervals1)
solution(intervals=intervals2)

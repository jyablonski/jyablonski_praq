# You are given an array of CPU tasks, each labeled with a letter from A to Z, and a number n.
# Each CPU interval can be idle or allow the completion of one task. Tasks can be completed in
# any order, but there's a constraint: there has to be a gap of at least n intervals between
# two tasks with the same label.

# Return the minimum number of CPU intervals required to complete all tasks.

from collections import Counter


# (minimum time) = (max_freq - 1) * (n + 1) + max_count
def solution(tasks: list[str], n: int) -> int:
    freq = Counter(tasks)

    # the task that appears the most times
    max_freq = max(freq.values())

    # number of tasks tied for most frequent
    max_count = sum(1 for t in freq.values() if t == max_freq)

    # calulate the # of min slots needed
    part_count = max_freq - 1
    part_length = n + 1
    min_intervals = part_count * part_length + max_count

    # final res is either the actual task count, or the # of min intervals
    # we take the higher amount because min_intervals will never be less than
    # the # of tasks
    return max(len(tasks), min_intervals)


tasks1 = ["A", "A", "A", "B", "B", "B"]
n1 = 2

tasks2 = ["A", "C", "A", "B", "D", "B"]
n2 = 1

solution(tasks=tasks1, n=n1)
solution(tasks=tasks2, n=n2)

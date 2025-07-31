# Given a list of 24-hour clock time points in "HH:MM" format, return the
# minimum minutes difference between any two time-points in the list.

# terribly written question, skip
def solution(timePoints: list[str]) -> int:
    def to_minutes(t: str) -> int:
        hours, minutes = map(int, t.split(":"))
        return hours * 60 + minutes

    minutes_list = sorted(to_minutes(t) for t in timePoints)

    # Compute min difference between adjacent times
    min_diff = float("inf")
    for i in range(1, len(minutes_list)):
        diff = minutes_list[i] - minutes_list[i - 1]
        min_diff = min(min_diff, diff)

    # Compare last and first across midnight
    first = minutes_list[0]
    last = minutes_list[-1]
    wrap_around_diff = (24 * 60 + first - last) % (24 * 60)
    min_diff = min(min_diff, wrap_around_diff)

    return min_diff


timePoints1 = ["23:59", "00:00"]
timePoints2 = ["00:00", "23:59", "00:00"]

solution(timePoints=timePoints1)
solution(timePoints=timePoints2)


def solution(timePoints: list[str]) -> int:
    def to_minutes(t: str) -> int:
        hours, minutes = map(int, t.split(":"))
        return hours * 60 + minutes

    minutes_list = sorted(to_minutes(t) for t in timePoints)

    # Compute min difference between adjacent times
    min_diff = float("inf")
    for i in range(1, len(minutes_list)):
        diff = minutes_list[i] - minutes_list[i - 1]
        min_diff = min(min_diff, diff)

    # Compare last and first across midnight
    first = minutes_list[0]
    last = minutes_list[-1]
    wrap_around_diff = (24 * 60 + first - last) % (24 * 60)
    min_diff = min(min_diff, wrap_around_diff)

    return min_diff

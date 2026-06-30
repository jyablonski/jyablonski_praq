def solution():
    safe_reports = 0

    with open("advent_of_code/2024/day_2_input.txt", "r") as file:
        for report in file:
            levels = report.strip().split(" ")
            levels = list(map(int, levels))

            # determine if levels are strictly increasing or decreasing
            is_increasing = all(
                levels[i] < levels[i + 1] and 1 <= levels[i + 1] - levels[i] <= 3
                for i in range(len(levels) - 1)
            )
            is_decreasing = all(
                levels[i] > levels[i + 1] and 1 <= levels[i] - levels[i + 1] <= 3
                for i in range(len(levels) - 1)
            )

            # if either them are increasing or decreasing entirely, then that is a safe report
            if is_increasing or is_decreasing:
                safe_reports += 1

    return safe_reports


solution()

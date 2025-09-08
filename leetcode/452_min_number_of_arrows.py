# There are some spherical balloons taped onto a flat wall that represents the XY-plane. The balloons are
# represented as a 2D integer array points where points[i] = [xstart, xend] denotes a balloon whose
# horizontal diameter stretches between xstart and xend. You do not know the exact y-coordinates of the balloons.

# Arrows can be shot up directly vertically (in the positive y-direction) from different points along
# the x-axis. A balloon with xstart and xend is burst by an arrow shot at x if xstart <= x <= xend.
# There is no limit to the number of arrows that can be shot. A shot arrow keeps traveling up
# infinitely, bursting any balloons in its path.

# Given the array points, return the minimum number of arrows that must be shot to burst all balloons.


def solution(points: list[list[int]]) -> int:
    if not points:
        return 0

    points = sorted(points, key=lambda x: x[1])
    print(f"Points is {points}")
    arrows = 1
    current_arrow_pos = points[0][1]

    for i in range(1, len(points)):
        start = points[i][0]
        end = points[i][1]

        # also works?
        # start, end = points[i]
        print(start, end)

        if start > current_arrow_pos:
            print(
                f"{start} > {current_arrow_pos}, adding 1 to arrows and setting arrow pos to {end}"
            )
            arrows += 1
            current_arrow_pos = end

    return arrows


points1 = [[10, 16], [2, 8], [1, 6], [7, 12]]
points2 = [[1, 2], [3, 4], [5, 6], [7, 8]]

solution(points=points1)
solution(points=points2)

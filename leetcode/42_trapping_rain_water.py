# Given n non-negative integers representing an elevation map where
# the width of each bar is 1, compute how much water it can trap after raining.


def solution(height: list[int]) -> int:
    left_wall = 0
    right_wall = 0
    n = len(height)
    max_left = [0] * n
    max_right = [0] * n
    water_sum = 0

    # iterate backwards
    for i in range(n):
        j = -i - 1
        max_left[i] = left_wall
        max_right[j] = right_wall
        left_wall = max(left_wall, height[i])
        right_wall = max(right_wall, height[j])

    for i in range(n):

        # use the minimum value
        potential_water = min(max_left[i], max_right[i])

        # only add to water_sum if potential_water - height[i]
        # is actually > 0
        water_sum += max(0, potential_water - height[i])

    return water_sum


height1 = [0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]

solution(height=height1)

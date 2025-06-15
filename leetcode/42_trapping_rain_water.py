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


def hello_inteview_solution(heights: list[int]):
    left = 0
    right = len(heights) - 1
    left_max = heights[left]
    right_max = heights[right]
    count = 0

    # adding +1 to ensure there's always 1 element between left and right
    # Always move the pointer on the side with the smaller max (because that's the limiting factor)
    # If the current bar is lower than the side’s max then count += side_max - heights[side]
    # Otherwise → update the max and continue to the next iteration
    # Every iteration either updates a max for a side, or adds to count by trapping water
    while left + 1 < right:
        if right_max > left_max:
            left += 1

            if heights[left] > left_max:
                left_max = heights[left]
            else:
                count += left_max - heights[left]

        else:
            right -= 1

            if heights[right] > right_max:
                right_max = heights[right]
            else:
                count += right_max - heights[right]

    return count

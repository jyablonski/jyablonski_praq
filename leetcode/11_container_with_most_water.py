# You are given an integer array height of length n. There are n vertical lines
# drawn such that the two endpoints of the ith line are (i, 0) and (i, height[i]).

# Find two lines that together with the x-axis form a container, such that the
# container contains the most water.

# Return the maximum amount of water a container can store.

# Notice that you may not slant the container.


# use 2 pointers, left starting at left and right starting at right
# to maximize our width and hopefully allow us to get the best solution
def solution(height: list[int]) -> int:
    n = len(height)
    l = 0
    r = n - 1
    max_area = 0

    while l < r:
        # we already know the width is the difference between the 2 pointers
        width = r - l

        # pick the smaller of the 2 height values to correctly calculate area
        current_max_height = min(height[l], height[r])
        area = width * current_max_height
        max_area = max(max_area, area)

        # increase left if its height is lower than right
        # decrement right if its height is lower than left
        if height[l] < height[r]:
            l += 1
        else:
            r -= 1

    return max_area


height1 = [1, 8, 6, 2, 5, 4, 8, 3, 7]
height2 = [1, 1]

solution(height=height1)
solution(height=height2)

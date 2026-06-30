# Given an array of integers heights representing the histogram's bar height
# where the width of each bar is 1, return the area of the largest rectangle in the histogram.


# use a monotonically increasing stack for o(n) time complexity
def solution(heights: list[int]) -> int:
    stack = []
    max_area = 0
    i = 0

    while i < len(heights):
        if not stack or heights[i] >= heights[stack[-1]]:
            stack.append(i)
            i += 1

        else:
            top = stack.pop()
            right = i - 1
            left = stack[-1] if stack else -1
            area = heights[top] * (right - left)
            max_area = max(max_area, area)

    while stack:
        top = stack.pop()
        width = i - stack[-1] - 1 if stack else i
        area = heights[top] * width
        max_area = max(max_area, area)

    return max_area


heights1 = [2, 1, 5, 6, 2, 3]
heights2 = [2, 4]

solution(heights=heights1)
solution(heights=heights2)

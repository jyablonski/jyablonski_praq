# A web developer needs to know how to design a web page's size. So, given a specific
# rectangular web page’s area, your job by now is to design a rectangular web page
# whose length L and width W satisfy the following requirements:

# The area of the rectangular web page you designed must equal to the given target area.
# The width W should not be larger than the length L, which means L >= W.
# The difference between length L and width W should be as small as possible.
# Return an array [L, W] where L and W are the length and width of the web page you designed in sequence.

import math


def solution(area: int) -> list[int]:
    # math.isqrt(48) returns the largest square root of the base number
    # (6 in this case. isqrt(49) would return 7)
    # start checking from the largest possible width
    for width in range(int(math.isqrt(area)), 0, -1):
        # check if the current w divides evenly into area
        # if it does, we can calculate a matching l and return it
        if area % width == 0:
            length = area // width
            return [length, width]


area1 = 4
area2 = 37

solution(area=area1)
solution(area=area2)

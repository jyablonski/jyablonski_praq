# You are given two positive integer arrays spells and potions, of length n and m respectively,
# where spells[i] represents the strength of the ith spell and potions[j] represents the strength of the jth potion.

# You are also given an integer success. A spell and potion pair is considered successful if the
# product of their strengths is at least success.

# Return an integer array pairs of length n where pairs[i] is the number of potions that will form
# a successful pair with the ith spell.
from bisect import bisect_left
import math


# trick here is to use binary search. we find the minimum potion needed for each spell
# in order to be successful, and then we KNOW that all subsequent potions will also be
# successful as well. this is more efficient than the brute force solution.


# time complexity O(m log m + n log m) - much better!
def solution(spells: list[int], potions: list[int], success: int) -> list[int]:
    potions.sort()
    res = []

    for spell in spells:
        # find minimum potion strength needed for this spell
        min_potion = math.ceil(success / spell)
        print(f"min potion is {min_potion}")

        # standard binary search stuff afterwards
        left = 0
        right = len(potions)

        # perform binary search for the first potion >= min portion
        while left < right:
            mid = (left + right) // 2

            if potions[mid] < min_potion:
                left = mid + 1
            else:
                right = mid

        # all potions from index 'left' to end are successful
        res.append(len(potions) - left)

    return res


spells1 = [5, 1, 3]
potions1 = [1, 2, 3, 4, 5]
success1 = 7

spells2 = [3, 1, 2]
potions2 = [8, 5, 8]
success2 = 16

solution(spells=spells1, potions=potions1, success=success1)
solution(spells=spells2, potions=potions2, success=success2)


# other approach which is even simpler
def solution_v2(spells: list[int], potions: list[int], success: int) -> list[int]:
    potions.sort()
    res = []

    for spell in spells:
        min_potion = math.ceil(success / spell)
        index = bisect_left(potions, min_potion)
        res.append(len(potions) - index)

    return res


# original solution but it's inefficient using a double nested loop
def solution_old(spells: list[int], potions: list[int], success: int) -> list[int]:
    res = []

    for spell in spells:
        count = 0
        for potion in potions:
            if spell * potion >= success:
                count += 1

        res.append(count)

    return res

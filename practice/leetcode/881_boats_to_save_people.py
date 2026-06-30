# You are given an array people where people[i] is the weight of the ith person, and an infinite
# number of boats where each boat can carry a maximum weight of limit. Each boat carries at most
# two people at the same time, provided the sum of the weight of those people is at most limit.

# Return the minimum number of boats to carry every given person.

# sort the input list and 2 use 2 pters to track the lighest and heaviest passengers
# we either have a valid pair, or the heaviest person has to go alone

# o(n log n) complexity because of the sorting. the while loop considers easch person once,
# so that's o(n) and it just gets cancelled out. o(1) space
def solution(people: list[int], limit: int) -> int:
    people.sort()
    n = len(people)
    left = 0
    right = n - 1
    res = 0

    while left <= right:
        # increment left only when we successfully pair the lighest person w/ the heaviest
        if people[left] + people[right] <= limit:
            left += 1

        # heaviest person will always go in a boat
        right -= 1
        res += 1

    return res


people1 = [1, 2]
limit1 = 3

people2 = [3, 5, 3, 4]
limit2 = 5

# i, 3, 4, 7, 8
people3 = [3, 8, 7, 1, 4]
limit3 = 9

solution(people=people1, limit=limit1)
solution(people=people2, limit=limit2)
solution(people=people3, limit=limit3)

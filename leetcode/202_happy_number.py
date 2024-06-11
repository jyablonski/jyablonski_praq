# Write an algorithm to determine if a number n is happy.

# A happy number is a number defined by the following process:

# Starting with any positive integer, replace the number by the sum of the squares of its digits.
# Repeat the process until the number equals 1 (where it will stay), or it loops endlessly in a cycle which does not include 1.
# Those numbers for which this process ends in 1 are happy.
# Return true if n is a happy number, and false if not.


# this was fairly straight forward except figuring out how to terminate
# the trick is to use a set to keep track of the numbers you've iterated over
# if you ever hit the same number twice and you havent gotten a solution yet then you know you'll just end in an endless loop
# so terminate.
# we either get an n == 1 and we return n == 1 which returns true, or
def solution(n: int) -> bool:
    seen = set()

    while n != 1 and n not in seen:
        seen.add(n)
        n = sum(int(digit) ** 2 for digit in str(n))

    return n == 1


n1 = 19
n2 = 2

solution(n=n1)
solution(n=n2)


def solution(n: int) -> bool:
    seen = set()

    while n != 1 and n not in seen:
        seen.add(n)
        n = sum(int(digit) ** 2 for digit in str(n))

    return n == 1


def old_solution(n: int) -> bool:
    seen = set()

    while n != 1:
        if n in seen:
            return False

        seen.add(n)
        n = [int(digit) ** 2 for digit in str(n)]

    if n == 1:
        return True

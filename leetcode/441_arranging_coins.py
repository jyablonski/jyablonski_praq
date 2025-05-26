# You have n coins and you want to build a staircase with these coins.
# The staircase consists of k rows where the ith row has exactly i coins.
# The last row of the staircase may be incomplete.

# Given the integer n, return the number of complete rows of the staircase
# you will build.


def solution(n: int) -> int:
    left = 0
    right = n

    while left <= right:
        mid = (left + right) // 2
        coins_used = mid * (mid + 1) // 2

        if coins_used == n:
            return mid
        elif coins_used < n:
            left = mid + 1
        else:
            right = mid - 1

    return right


n1 = 5
n2 = 8

solution(n=n1)
solution(n=n2)

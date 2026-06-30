# Given a positive integer num, return true if num is a perfect square or false otherwise.
# A perfect square is an integer that is the square of an integer. In other words, it is the product of some integer with itself.
# You must not use any built-in library function, such as sqrt.


def solution(n: int) -> bool:
    l = 1
    r = n

    while l < r:
        mid = (l + r) // 2

        if mid * mid > n:
            r = mid - 1
        elif mid * mid < n:
            l = mid + 1
        else:
            return True
    return False


n1 = 16
n2 = 14

solution(n=n1)
solution(n=n2)

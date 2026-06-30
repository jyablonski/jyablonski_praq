# An ugly number is a positive integer whose prime factors are limited to 2, 3, and 5.

# Given an integer n, return true if n is an ugly number.


def solution(n: int) -> bool:
    if n <= 0:
        return False

    for prime in [2, 3, 5]:
        print(f"Starting loop with n {n} and prime {prime}")
        while n % prime == 0:
            print(f"old n was {n}")
            n = n // prime
            print(f"n is now {n // prime}")

    print(f"Returning n {n} == 1")
    return n == 1


n1 = 6
n2 = 1
n3 = 14
n4 = 23

solution(n=n1)
solution(n=n2)
solution(n=n3)
solution(n=n4)

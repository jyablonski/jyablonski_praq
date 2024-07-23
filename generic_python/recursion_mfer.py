import random
import string


def factorial(n: int) -> int:
    # Base case: if n is 0 or 1, return 1
    if n == 0 or n == 1:
        print(f"1 boob")
        return 1
    # Recursive case: n * factorial(n-1)
    else:
        print(f"{n} boobs")
        return n * factorial(n - 1)


number = factorial(8)


def add_1_until_n(n: int) -> int:
    int_sum = 1
    int_count = 1

    while int_count <= n:
        int_sum += int_count
        int_count += 1

    return int_sum


add_1_until_n(n=120)


def fact(x: int) -> int:
    # base case
    if x == 1:
        return 1
    else:
        return x * fact(x - 1)


fact(4)


def add_1(x: int) -> int:
    if x == 1:
        return 1
    else:
        return x + add_1(x - 1)


add_1(5)

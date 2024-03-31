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

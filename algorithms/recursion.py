from sys import getrecursionlimit

getrecursionlimit()


def jacobs_recursion(num: int, limit: int = 2000):
    if num >= limit:
        return  # Base case: Stop the recursion when num is greater than or equal to 1000

    print(num)
    jacobs_recursion(num + 1)


jacobs_recursion(num=1)  # this runs fine
jacobs_recursion(num=1, limit=3001)  # this will hit the recursion limit


def factorial(n: int) -> int:
    return_value = 1
    for i in range(2, n + 1):
        print(i)
        return_value *= i
    return return_value


factorial(4)

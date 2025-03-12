# Given a signed 32-bit integer x, return x with its digits reversed.
# If reversing x causes the value to go outside the signed 32-bit
# integer range [-2**31, 2**31 - 1], then return 0.

# Assume the environment does not allow you to store 64-bit integers (signed or unsigned).


def solution(x: int) -> int:
    int_max = 2**31 - 1
    result = 0
    sign = -1 if x < 0 else 1
    x = abs(x)

    while x != 0:
        print(f"starting x is {x}")
        digit = x % 10

        # remove last digit
        x //= 10
        print(f"digit is {digit}, x is {x}")

        # check for overflow before modifying result. If adding another digit would exceed int_max, return 0.
        if result > (int_max - digit) // 10:
            return 0

        result = result * 10 + digit
        print(f"new result is {result}")

    return sign * result


x1 = 123
x2 = -123
x3 = 120
x4 = 1204
x5 = 10001
x6 = 2147483649
x7 = 0

solution(x=x1)
solution(x=x2)
solution(x=x3)
solution(x=x4)
solution(x=x5)
solution(x=x6)
solution(x=x7)

# Given an integer num, repeatedly add all its digits until the result has only one digit, and return it.

# Example 1:

# Input: num = 38
# Output: 2
# Explanation: The process is
# 38 --> 3 + 8 --> 11
# 11 --> 1 + 1 --> 2
# Since 2 has only one digit, return it.


# this converts the number into a string, splitting the str into digits,
# summing them, and repeating until a single digit is reached
def solution(num: int) -> int:
    while len(str(num)) > 1:
        num = sum([int(char) for char in str(num)])

    return num


# this calculates the result in constant time using the digital root formula
# which is below
def solution(num: int) -> int:
    if num > 9:
        return (num - 1) % 9 + 1
    else:
        return num


num1 = 0
num2 = 15
num3 = 157

solution(num=num1)
solution(num=num2)
solution(num=num3)

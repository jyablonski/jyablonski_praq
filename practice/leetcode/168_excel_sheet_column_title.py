# Given an integer columnNumber, return its corresponding column title as it appears in an Excel sheet.

# For example:

# A -> 1
# B -> 2
# C -> 3
# ...
# Z -> 26
# AA -> 27
# AB -> 28
# ...

# idea is to take the initial number and process each character


def solution(column_number: int) -> str:
    result = []

    while column_number > 0:
        # decrement by 1 to make it 0-indexed so we're picking characters properly
        # without this, chr(26 % 26 + ord("A")) would return A instead of Z
        column_number -= 1

        # chr turns ints into characters. adding ord("A") gives us a baseline to add
        # the remainder of our current value % 26 which is the num of chars in alphabet
        # so we get an accurate value back afterwards
        result.append(chr(column_number % 26 + ord("A")))

        # this is the same as column_number = column_number // 26
        column_number //= 26
        print(f"result is now {result} and col num is {column_number}")

    # because we build it backwards to forward, return the reversed results
    return "".join(reversed(result))


col_num1 = 1
col_num2 = 28
col_num3 = 701
col_num4 = 1313
col_num5 = 26

solution(column_number=col_num1)
solution(column_number=col_num2)
solution(column_number=col_num3)
solution(column_number=col_num4)
solution(column_number=col_num5)


chr(1 + ord("A") - 1)

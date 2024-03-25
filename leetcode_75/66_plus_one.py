# You are given a large integer represented as an integer array digits, where
# each digits[i] is the ith digit of the integer. The digits are ordered from
# most significant to least significant in left-to-right order. The large integer
# does not contain any leading 0's.

# Increment the large integer by one and return the resulting array of digits.

# intialize a new empty list
# then turn the digits into a number by joining them together with 0 separated space
# and add 1.  then turn it back into a string to iterate through those numbers
# to append them into that new_list and turn them back into ints in that process


def solution(digits: list[int]) -> list[int]:
    new_list = [
        int(digit) for digit in (str(int("".join(str(digit) for digit in digits)) + 1))
    ]

    return new_list


digits = [1, 2, 3]
digits2 = [9]
digits3 = [0, 0]
solution(digits=digits)
solution(digits=digits2)
solution(digits=digits3)

# pytest leetcode_75/66_plus_one.py
import pytest


@pytest.mark.parametrize(
    "input_digits, expected_output",
    [([1, 2, 3], [1, 2, 4]), ([0, 0], [1]), ([9], [1, 0])],
)
def test_plus_one(input_digits, expected_output):
    answer = solution(digits=input_digits)

    assert answer == expected_output

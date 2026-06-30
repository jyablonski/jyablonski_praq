# Seven different symbols represent Roman numerals with the following values:

# I	1
# V	5
# X	10
# L	50
# C	100
# D	500
# M	1000


# Given an integer, convert it to a Roman numeral.

# these are special subtraction use cases, we include them to automatically
# handle their edge cases easily
# (900, 'CM'),
# (400, 'CD'),
# (90, 'XC'),
# (40, 'XL'),
# (9, 'IX'),
# (4, 'IV')


def solution(num: int) -> str:
    # create a mapping
    roman_mapping = [
        (1000, "M"),
        (900, "CM"),
        (500, "D"),
        (400, "CD"),
        (100, "C"),
        (90, "XC"),
        (50, "L"),
        (40, "XL"),
        (10, "X"),
        (9, "IX"),
        (5, "V"),
        (4, "IV"),
        (1, "I"),
    ]

    roman = ""

    # iterate through the mapping from top to bottom
    # and try to find combos that are >= the num we're running for
    for val, symbol in roman_mapping:
        # use while loop because we might have to use the same symbol
        # multiple times in a row before num < val
        while num >= val:
            # when we find a match, add the symbol to `roman` and subtract the
            # symbol's `val` from `num`
            roman += symbol
            num -= val

    return roman


num1 = 58
num2 = 1994

solution(num=num1)
solution(num=num2)

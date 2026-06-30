# A phrase is a palindrome if, after converting all uppercase letters into lowercase letters
# and removing all non-alphanumeric characters, it reads the same forward and backward.
# Alphanumeric characters include letters and numbers.

# Given a string s, return true if it is a palindrome, or false otherwise.


def is_valid_palindrome(s: str) -> bool:
    s = s.lower()
    clean_string = ""

    for char in s:
        if char.isalnum():
            clean_string += char

    return clean_string == clean_string[::-1]


str1 = "hello!!as132"
str2 = "racecaR"
str3 = "racecar."

is_valid_palindrome(s=str1)
is_valid_palindrome(s=str2)
is_valid_palindrome(s=str3)

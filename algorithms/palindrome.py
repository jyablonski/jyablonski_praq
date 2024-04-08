# Given an integer x, return true if x is a palindrome, and false otherwise.
# a palindrome is a number like 121 or 323


def solution(s: int):
    s = str(s)
    new_str = ""

    for char in s:
        if char.isalnum():
            new_str += char.lower()

    print(new_str)

    if new_str == new_str[::-1]:
        return True
    else:
        return False


x = 123
y = 323

# problem 57 palindromes.
pas = "r&a@@C!!ec..ar"
pas2 = "racecar3"


solution(x)
solution(y)
solution(pas)
solution(pas2)

my_list = ["hello", "my", "you", "world"]
my_list_reversed = my_list[::-1]  # this reverses the entire list
my_list_test1 = my_list[:-1]  # this removes the last value
my_list_test2 = my_list[-1]  # this returns the last value
my_list_test3 = my_list[:1]  # this returns the first value
my_list_test4 = my_list[1:]  # this removes the first value

print(my_list)
print(my_list_reversed)

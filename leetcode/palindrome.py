# Given an integer x, return true if x is a palindrome, and false otherwise.
# a palindrome is a number like 121 or 323

x = 123
y = 323

# problem 57 palindromes.
pas = 'r&a@@C!!ec..ar'
pas2 = 'racecar3'

def solution(s: str):
    s = str(s)
    new_str = ""

    for c in s: # for every character in the input string
        if c.isalnum(): # if its alphanumerical, removing any non letters or numbers.
            new_str += c.lower() # lowercase it and add it to new_str which is the clean variable we created.

    print(f"new str is {new_str}")
    return new_str == new_str[::-1] # this completely reverses the string in python
    
solution(x)
solution(y)
solution(pas)
solution(pas2)

my_list = ["hello", "my", "you", "world"]
my_list_reversed = my_list[::-1] # this reverses the entire list
my_list_test1 = my_list[:-1]     # this removes the last value
my_list_test2 = my_list[-1]      # this returns the last value
my_list_test3 = my_list[:1]      # this returns the first value
my_list_test4 = my_list[1:]      # this removes the first value

print(my_list)
print(my_list_reversed)
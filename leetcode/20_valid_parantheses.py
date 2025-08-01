# Given a string s containing just the characters '(', ')', '{', '}', '[' and ']', determine if the input string is valid.

# An input string is valid if:

# Open brackets must be closed by the same type of brackets.
# Open brackets must be closed in the correct order.
# Every close bracket has a corresponding open bracket of the same type.

# put a quick condition at start to check if the len of the input string
# is a multiple of 2.  if not, then input will be invalid and we dont have to check


# then initialize combos dictionary and an empty list for the stack
def solution(s: str) -> bool:
    if len(s) % 2 != 0:
        return False

    combos = {"(": ")", "{": "}", "[": "]"}
    stack = []

    for char in s:
        # if it's an open bracket, then add it to stack
        if char in combos:
            stack.append(char)
        else:
            # if it's a closing bracket and:
            # 1. we don't have anything in stack
            # 2. or the last character in the stack does not match with this one
            # then return false
            if not stack or combos[stack[-1]] != char:
                return False

            # otherwise, it's a match and we just pop the last value on the stack
            else:
                stack.pop()

    # return true only if stack is empty after iterating through the string
    return True if not stack else False


s = "()[]{}"  # true
s2 = "([])"  # true
s3 = "(([])}"  # false
s4 = "(("
s5 = "){"
solution(s)
solution(s2)
solution(s3)
solution(s4)
solution(s5)

t = [1, 2, 3]


def solution(s: str) -> bool:
    stack = []
    mapping = {")": "(", "}": "{", "]": "["}

    # iterate through the entire string
    for char in s:
        # Does this closing bracket correctly match the last opening bracket we saw?
        if char in mapping:
            if not stack or stack[-1] != mapping[char]:
                return False

            # otherwsie we can pop
            stack.pop()
        else:
            stack.append(char)

    # if there are any leftover values, return false
    return len(stack) == 0

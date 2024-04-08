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
        if char in combos:
            stack.append(char)
        else:
            if len(stack) == 0 or combos[stack[-1]] != char:
                return False
            else:
                stack.pop()

    return True if not stack else False


s = "()[]{}"  # true
s2 = "([])"  # false
s3 = "(([])}"  # false
s4 = "(("
s5 = "){"
solution(s)
solution(s2)
solution(s3)
solution(s4)
solution(s5)

t = [1, 2, 3]

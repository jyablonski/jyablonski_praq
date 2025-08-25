# Given a string s containing only three types of characters: '(', ')' and '*', return true if s is valid.

# The following rules define a valid string:

# Any left parenthesis '(' must have a corresponding right parenthesis ')'.
# Any right parenthesis ')' must have a corresponding left parenthesis '('.
# Left parenthesis '(' must go before the corresponding right parenthesis ')'.
# '*' could be treated as a single right parenthesis ')' or a single left parenthesis '(' or an empty string "".


def solution(s: str) -> bool:
    min_open = 0  # min possible unmatched left parantheses
    max_open = 0  # max possible unmatched left parantheses

    for char in s:
        if char == "(":
            min_open += 1
            max_open += 1
        elif char == ")":
            min_open -= 1
            max_open -= 1

        # else if char is *, treat is as both an end char
        # for min_open, and a beginning char for max open
        else:
            min_open -= 1  # treat as ')' to minimize
            max_open += 1  # treat as '(' to maximize

        # If max_open < 0, we have too many ')' - impossible to balance
        if max_open < 0:
            return False

        # to handle edge case of * chars causing min open to become negative,
        # always check to see if we can reset it back to 0 at the end
        min_open = max(min_open, 0)

    print(f"min open is {min_open}, max_open is {max_open}")

    # return true as long as we have 0 unmatched parantheses
    # this catches cases like s = "((("
    return min_open <= 0 <= max_open


s1 = "()"
s2 = "(*)"
s3 = "(*))"

solution(s=s1)
solution(s=s2)
solution(s=s3)


# too many edge cases with the * character
def old_solution(s: str) -> bool:
    if len(s) == 1:
        return False

    stack = []
    begin_chars = ("(", "*")

    for char in s:
        print(f"Checking {char}")
        if char in begin_chars:
            stack.append(char)
        else:
            if not stack or stack[-1] not in begin_chars:
                print(f"Stack is {stack}, ")
                return False
            else:
                stack.pop()

    print(stack)
    return True if not stack else False

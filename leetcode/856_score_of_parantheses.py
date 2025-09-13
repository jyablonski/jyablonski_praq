# Given a balanced parentheses string s, return the score of the string.

# The score of a balanced parentheses string is based on the following rule:

# "()" has score 1.
# AB has score A + B, where A and B are balanced parentheses strings.
# (A) has score 2 * A, where A is a balanced parentheses string.

# Use a stack to track scores at each nesting level - start with [0] as the base level
# Opening parenthesis ( - push a new level with score 0 to the stack
# Closing parenthesis ) - pop the current level's accumulated score, then apply scoring rules: () gets score 1, (A) gets score 2×A
# Add the calculated score to the parent level - this handles the "AB = A + B" rule where adjacent balanced strings sum their scores
# stack level accumulates scores from adjacent balanced substrings, and closing parentheses "wrap" those accumulated scores by doubling them

# time complexity o(n) because we just iterate through the string
# space complexity
def solution(s: str) -> int:
    stack = [0]  # start with 0 score as base

    for char in s:
        if char == "(":
            stack.append(0)  # new level starts with 0 score

        # if char == ")"
        else:
            print(f"Found end parantheses, stack is {stack}")
            current_score = stack.pop()

            # If current level has no score, it's "()" = 1
            # Otherwise, it's "(A)" = 2 * A
            score = max(2 * current_score, 1)
            stack[-1] += score

    return stack[0]


s1 = "()"
s2 = "(())"
s3 = "(()(()))"

solution(s=s1)
solution(s=s2)
solution(s=s3)

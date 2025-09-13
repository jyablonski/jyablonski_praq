# A parentheses string is valid if and only if:

# It is the empty string,
# It can be written as AB (A concatenated with B), where A and B are valid strings, or
# It can be written as (A), where A is a valid string.
# You are given a parentheses string s. In one move, you can insert a parenthesis at any position of the string.

# For example, if s = "()))", you can insert an opening parenthesis to be "(()))" or a closing parenthesis to be "())))".
# Return the minimum number of moves required to make s valid.

# o(n) time complexity
# simple solution. just iterate through the string and use a stack to keep track of
# pairs of parantheses that can be open or closed
def solution(s: str) -> int:
    stack = []

    for char in s:
        # always append open parantheses
        if char == "(":
            stack.append(char)
        else:
            # if we get a close parantheses and stack is empty or
            # the last char in stack is not `(` to create a valid pair,
            # then append the char
            if not stack or stack[-1] != "(":
                stack.append(char)

            # else we have a valid pair, and we can just pop the last char
            # off stack
            else:
                stack.pop()

    return len(stack)


s1 = "())"
s2 = "((("

solution(s=s1)
solution(s=s2)

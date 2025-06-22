# Given a string containing just the characters '(' and ')', return the length of the longest valid (well-formed) parentheses substring.

# key assumption that the input string can only be `(` or `)`


# strategy involves using a stack that will always contain the index of hte last unmatched opening parantheses,
# which is the start of the current valid substring
def solution(s: str) -> int:
    max_len = 0
    stack = [-1]
    # this has to be -1 to handle edge cases like s = `()`

    for i, char in enumerate(s):
        # always put opening parantheses onto the stack
        if char == "(":
            stack.append(i)

        else:
            # first pop the top element
            stack.pop()

            # then check if the stack is empty or not
            if not stack:
                # stack is empty. addt he current index so any future substring
                # can only start after this
                stack.append(i)
            else:
                # stack is not empty.
                # we can calculate the length of the valid substring
                max_len = max(max_len, i - stack[-1])

    return max_len


s1 = "()"
s2 = ")()())"

solution(s=s1)
solution(s=s2)

# this loops through in reverse order
len_s = 5
for i in range(len_s - 1, -1, -1):
    print(i)

# Given a string s which represents an expression, evaluate this expression and return its value.
# The integer division should truncate toward zero.
# You may assume that the given expression is always valid. All intermediate results will be in the range of [-2^31, 2^31 - 1].
# Note: You are not allowed to use any built-in function which evaluates strings as mathematical expressions, such as eval().


def solution(s: str) -> int:
    stack = []
    current_num = 0
    last_op = "+"
    s = s.replace(" ", "")

    for i, char in enumerate(s):
        # ensure we track numbers like `123+45` as 123 + 45,
        # and not 1 + 2 + 3 + 4 + 5 etc
        if char.isdigit():
            current_num = current_num * 10 + int(char)
            print(f"updated current_num: {current_num}")

        # if we run into an op code, or we're at the last index
        # of the string, then we have to append the results of the
        # math operation to stack
        if char in "+-*/" or i == len(s) - 1:
            if last_op == "+":
                stack.append(current_num)
            elif last_op == "-":
                stack.append(-current_num)
            elif last_op == "*":
                stack[-1] *= current_num
            elif last_op == "/":
                stack[-1] = int(stack[-1] / current_num)

            # after we adjust stack, always reset last op and current num
            last_op = char
            current_num = 0

    print(stack)
    # stack is a list of ints to account for all the ops we made
    return sum(stack)


s1 = "3+2*2"
s2 = " 3/2 "

solution(s=s1)
solution(s=s2)

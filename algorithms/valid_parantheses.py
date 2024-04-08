# given a string `s` containing (){}[] determine if the string is valid
# all brackets, parantheses, and [] must be properly closed

s = "fds()sd{}sdfsd[]"


def solution(s: str) -> bool:
    stack = []
    print(stack)

    for char in s:
        print(char)
        if char == "(" or char == "{" or char == "[":
            stack.append(char)
            print(stack)
        else:
            if char == ")" and stack[-1] == "(":
                stack.pop()
            elif char == "}" and stack[-1] == "{":
                stack.pop()
            elif char == "]" and stack[-1] == "[":
                stack.pop()


solution(s)

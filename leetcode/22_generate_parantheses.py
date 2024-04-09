# https://leetcode.com/problems/generate-parentheses/description/
# Given n pairs of parentheses, write a function to generate all combinations of well-formed parentheses.


def solution(n: int) -> list[str]:
    res = []

    def backtrack(open_n, closed_n, path):
        if open_n == closed_n == n:
            res.append(path)
            return

        if open_n < n:
            backtrack(open_n + 1, closed_n, path + "(")

        if closed_n < open_n:
            backtrack(open_n, closed_n + 1, path + ")")

    backtrack(0, 0, "")
    return res


n1 = 3
n2 = 1

solution(n1)
solution(n2)


def solution(n: int) -> list[str]:
    res = []
    stack = [(0, 0, "")]

    while stack:
        open_n, closed_n, path = stack.pop()
        print(open_n)
        print(closed_n)

        if open_n == closed_n == n:
            res.append(path)
        if open_n < n:
            stack.append((open_n + 1, closed_n, path + "("))
        if closed_n < open_n:
            stack.append((open_n, closed_n + 1, path + ")"))

    return res


# Example usage:
print(solution(3))

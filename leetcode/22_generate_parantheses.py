# https://leetcode.com/problems/generate-parentheses/description/
# Given n pairs of parentheses, write a function to generate all combinations of well-formed parentheses.

# Use backtracking to build combinations and keep track of how many ( and ) are used
# only add ) when it will still be valid
# stop when len recahes 2 * n

# Time complexity: O(2^n)
# Space complexity: O(n)
def solution(n: int) -> list[str]:
    res = []

    def backtrack(current, open_count, close_count):
        # Base case: if the current string is complete
        # then add it to res
        # it's also guaranteed to be valid thx to our conditions below
        # ex: if n = 3, then current will have 6 characters
        if len(current) == 2 * n:
            res.append(current)
            return

        # these backtracking conditions help ensure we dont make invalid
        # parantheses combinations

        # can we add a "(" until we hit n number of open parantheses?
        if open_count < n:
            backtrack(current + "(", open_count + 1, close_count)

        # can we add a ")" to account for every open parantheses
        if close_count < open_count:
            backtrack(current + ")", open_count, close_count + 1)

    backtrack("", 0, 0)
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

# Given two integers n and k, return all possible combinations of k numbers chosen from the range [1, n].

# You may return the answer in any order.
# backtracking solution to build up the current combination, try all valid numbers, and stop when we get
# a valid result

# Time complexity: O(C(n, k))
# Because there are n choose k combinations total.

# Space complexity: O(k) for the recursion stack, plus output size.


import itertools


def solution(n: int, k: int) -> list[list[int]]:
    res = []

    def backtrack(start, path):
        # if the len of our current path is equal to
        # k, then we have a valid combination
        if len(path) == k:
            res.append(path[:])
            return

        # loop through start, n + 1 to ensure:
        # We don’t pick the same number twice.
        # We generate combinations in ascending order, so [1, 2] and [2, 1] won’t both appear.
        for i in range(start, n + 1):
            path.append(i)  # Choose
            backtrack(i + 1, path)  # explore
            path.pop()  # backtrack

    # backtrack starting from 1
    backtrack(1, [])
    return res


n1 = 4
k1 = 2

n2 = 1
k2 = 1

solution(n=n1, k=k1)
solution(n=n2, k=k2)


# cheap solution?
def combine(n: int, k: int) -> list[list[int]]:
    return list(itertools.combinations(range(1, n + 1), k))

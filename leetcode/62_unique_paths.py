# There is a robot on an m x n grid. The robot is initially located at the top-left corner
# (i.e., grid[0][0]). The robot tries to move to the bottom-right corner (i.e., grid[m - 1][n - 1]).
# The robot can only move either down or right at any point in time.

# Given the two integers m and n, return the number of possible unique paths that the robot
# can take to reach the bottom-right corner.

# The test cases are generated so that the answer will be less than or equal to 2 * 109.

# bottom up approach (tabulation)
# we start from the smallest base case and build up to the final solution


def solution(m: int, n: int) -> int:
    dp = []

    # 2d list with m rows and n columns filled with 0s
    for _ in range(m):
        dp.append([0] * n)

    # set base case: only 1 way of reaching starting cell (0, 0)
    dp[0][0] = 1

    # start with rows first, then columns
    for i in range(m):
        for j in range(n):
            # skip if they're at 0, 0 so we dont override the base case
            if i == j == 0:
                continue

            # Number of ways to reach cell (i, j) is the sum of:
            # - the ways to reach the cell above (i-1, j)
            # - the ways to reach the cell to the left (i, j-1)
            dp[i][j] = dp[i - 1][j] + dp[i][j - 1]

    # again, return in order of rows first, then columns
    # return the bottom right cell where the value is all the distinct ways to get there
    return dp[m - 1][n - 1]


# top down approach - we start at the goal (bottom right cell) and recursively break it down
# into smaller subproblems
# this will keep recalculating the same results every time
def solution_v2(m: int, n: int) -> int:
    memo = {(0, 0): 1}

    def paths(i, j):
        if (i, j) in memo:
            return memo[(i, j)]
        else:
            if i == j == 0:
                return 1

            # out of bounds mfer
            elif i < 0 or j < 0 or i == m or j == n:
                return 0

            else:
                val = paths(i, j - 1) + paths(i - 1, j)
                memo[(i, j)] = val
                return val

    return paths(m - 1, n - 1)


m1 = 3
n1 = 7

m2 = 3
n2 = 3

solution(m=m1, n=n1)
solution(m=m2, n=n2)

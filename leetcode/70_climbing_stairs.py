# you are climbing a staircase.  it takes n steps to reach the top
# each time you can either climb 1 or 2 steps.  how many distinct ways can you climb to the top.


def solution(n: int) -> int:
    if n in (0, 1):
        return 1

    # initialize a list to store the number of ways to reach each step
    dp = [0] * (n + 1)

    # set base cases
    dp[0] = 1  # 1 way to stay at the start (0 steps)
    dp[1] = 1  # 1 way to climb 1 step

    # calculate the number of ways for each step up to n using the recursive relation
    # this is like a fibonacci sequence adding the previous to values to get the next one
    for i in range(2, n + 1):
        print(f"dp[{i}] = {dp[i - 1]} + {dp[i - 2]}")
        dp[i] = dp[i - 1] + dp[i - 2]

    # return the number of ways to reach the top of the staircase
    return dp[n]


test1 = 1
test2 = 14
test3 = 30

solution1 = solution(n=test1)
solution2 = solution(n=test2)
solution3 = solution(n=test3)

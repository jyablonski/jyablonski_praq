# Naive recursive implementation of Fibonacci (inefficient for large n)
def fibo_raw(n: int) -> int:
    if n <= 1:
        return n
    return fibo_raw(n - 1) + fibo_raw(n - 2)


# Recursive implementation with memoization (top-down DP)
# Start from the original problem (fibo(n)) and recursively break it down
# into smaller subproblems (fibo(n-1), fibo(n-2), etc.) until reaching the base cases.
def fibo_memo(n: int, memo: dict = None) -> int:
    if memo is None:
        memo = {}  # Initialize memo dictionary if not provided

    # Check if the result is already computed
    if n in memo:
        return memo[n]

    # Base case: fibo(0) = 0, fibo(1) = 1
    # This is the stopping condition for the recursion
    if n <= 1:
        return n

    # Store result in memo to avoid redundant computations
    memo[n] = fibo_memo(n - 1, memo) + fibo_memo(n - 2, memo)
    return memo[n]


# Iterative dynamic programming implementation (bottom-up approach)
# starting from the base cases (fibo(0) and fibo(1)) and building up to fibo(n).
def fibo_dp(n: int) -> int:
    if n <= 1:
        return n

    # build up a list of Fibonacci numbers from 0 to n
    dp = [0] * (n + 1)

    # set base cases
    dp[1] = 1

    # Build the sequence from the bottom up
    for i in range(2, n + 1):
        dp[i] = dp[i - 1] + dp[i - 2]

    return dp[n]


# Optimized DP using constant space (only keeps track of the last two values)
def fibo_dp_optimized(n: int) -> int:
    if n <= 1:
        return n

    prev1 = 0  # Represents F(n-2)
    prev2 = 1  # Represents F(n-1)

    # Only keep the last two Fibonacci numbers at each step
    for _ in range(2, n + 1):
        current = prev1 + prev2
        prev1 = prev2
        prev2 = current

    return current


fibo_raw(10)
fibo_memo(10, {})
fibo_dp(10)
fibo_dp_optimized(10)

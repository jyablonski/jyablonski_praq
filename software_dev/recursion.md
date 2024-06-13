# Recursion

[Article](https://martinlwx.github.io/en/solving-dynamic-programming-problems-using-srtbot/)

Solve algorithmic problems of arbitrary size n with a fixed amount of code. Recursion is a technique where a function calls itself in order to solve a problem.

Solving these problems involves breaking it down into several overlapping subproblems.  The solution can be calculated by combining optimal solutions of smaller subproblems.

Memoization is an optimization technique that basically says we can remember and re-use our solutions to subproblems to solve the larger problem itself.

The 2 main concepts of Recursion are a base csae and a recursive case

- Base Case - Condition in which the recursive function stops calling itself.  It's the simplest instance that can be solved without further recursion
- Recursive Case - Part of the function that calls itself with a modified argument that gradually progresses towards the base case.

Recursive Problems follow the 3 steps:

1. Check if the current problem can be solved directly via the base case
2. If base case is met, return the result directly
3. If base case is not met, modify the problem slightly and call itself with a new, smaller problem (recursive case)

## SRTBOT

1. Subproblem definition
2. Relate subproblem solutions recursively
3. Topological order on subproblems to guarantee acyclic - DAGs
4. Base Case of relation
   1. Acts as a termination condition to prevent infinite recursion
5. Orginal Problem: solve via subproblems
6. Time Analysis

## Fibonacci Example

Fn = Fn - 1 + Fn - 2

1. Subproblems: F(i) = fi - <= i <= n
2. Relate: F(i) = F(i - 1) + F(i - 2)
3. Topological Order: increasing i, for i = 1, 2 ... n
4. Base Case: F(1) = F(2) = 1
5. Original Problem: F(n)
6. Time: T(n) = T(n - 1) + T(n - 2) + 1 (addition time) > Fn (grows exponentially, bad news bears)

``` py
def fibonacci(n: int) -> int:
    # Base cases: fibonacci(0) = 0, fibonacci(1) = 1
    if n == 0:
        return 0

    elif n == 1:
        return 1

    else:
        return fibonacci(n-1) + fibonacci(n-2)

# Example usage:
for i in range(10):
    print(fibonacci(i))
```

## Factorial Example

``` py
def factorial(n: int) -> int:
    # Base case: factorial of 0 or 1 is 1
    if n == 0 or n == 1:
        return 1
    # Recursive case: n! = n * (n-1)!
    else:
        return n * factorial(n - 1)

# Example usage:
print(factorial(5))  # Output: 120 (5! = 5 * 4 * 3 * 2 * 1 = 120)
```
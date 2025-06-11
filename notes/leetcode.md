# Leetcode

## 2 Pointers

The 2 pointer technique involves using 2 different pointers to iterate through a list. There are various ways these can be utilized:

- Starting at index 0 and at index 1, and then iterating the right pointer by one and comparing the values at these 2 indexes
    - These solutions are often (`n^2`) because you're iterating over every item in the list twice
- Starting with the left pointer at index 0 and the right pointer at `len(list) - 1` which is at the last value of the list
    - If the list is sorted, this is particularly effective in a problem like two sum where you can increment the left pointer by 1, or decrement the right pointer by 1 until you find some target value you're looking for

## Backtracking

Backtracking is an algorithmic technique used for solving problems incrementally by trying out possible solutions and abandoning ("backtracking") as soon as you realize the current path doesn’t lead to a valid or optimal solution.

1. Start at the root of the decision tree (an empty path or starting point).
2. Recursively build a potential solution by choosing one option at a time.
3. If a partial solution violates the problem constraints, backtrack (undo the last choice).
4. If you reach a complete and valid solution, record it.
5. Repeat this process until all possible paths have been explored or a solution is found.

Backtracking is particularly useful for problems involving permutations, combinations, subsets, and other scenarios where you need to explore all possible configurations.

Example: Generate all binary strings of length 2 using backtracking.

``` python
def generate_binary_strings(n):

    # create an empty list where we can store the results we're looking for
    result = []

    # this child function has access to all variables in the parent function
    def backtrack(path):
        # Base case: if the string is of desired length, record it
        if len(path) == n:
            result.append("".join(path))
            return

        # Recursive case: try adding '0' and '1'
        # basically keep trying all combinations
        # until you reach the base case, at which point you
        # record the result, or you hit a dead end and backtrack
        # by removing the last element from the path and trying the next option
        for bit in ['0', '1']:
            path.append(bit)            # Choose
            backtrack(path)            # Explore
            path.pop()                 # Un-choose (backtrack)

    # Start the backtracking with an empty path
    backtrack([])
    return result

print(generate_binary_strings(2))

```


When the problem involves finding unique combinations (like subsets, permutations, or groupings where order doesn’t matter or duplicates must be avoided), you need to add extra logic to avoid generating the same group multiple times.

``` python
def unique_combinations(nums):

    # Step 1: sort nums to enable skipping duplicates w/ the start logic
    nums.sort()
    result = []

    # The start index ensures that Each recursive call only considers elements
    # at or after the current index, preventing reuse of the same elements
    # earlier in the array. it ensures you don’t reuse previous elements
    # so combinations remain ordered (canonical).
    def backtrack(start, path):

        # store path[:] to store an immutable copy of the current path to result
        result.append(path[:])

        for i in range(start, len(nums)):

            # `nums[i] == nums[i - 1]` skips duplicates
            # When i == start, we always want to consider the element at nums[i]
            # because it's the first candidate at this level.
            if i > start and nums[i] == nums[i - 1]:
                continue

            path.append(nums[i])
            backtrack(i + 1, path)  # move forward
            path.pop()

    backtrack(0, [])
    return result

print(unique_combinations([1, 2, 2]))
```

combinations sum2

``` python
def combinationSum2(candidates, target):
    candidates.sort()
    result = []

    def backtrack(start, path, total):
        if total == target:
            result.append(path[:])
            return
        if total > target:
            return

        for i in range(start, len(candidates)):
            # Skip duplicates at this recursion level
            if i > start and candidates[i] == candidates[i-1]:
                continue

            path.append(candidates[i])
            backtrack(i + 1, path, total + candidates[i])  # move forward, no reuse
            path.pop()

    backtrack(0, [], 0)
    return result
```
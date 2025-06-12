# Leetcode

## Sorting

Sorting is a fundamental technique in computer science that involves arranging the elements of a list or array in a specific order, typically in ascending or descending order. Sorting is often a prerequisite for many algorithms and data structures, as it can significantly improve efficiency and performance.

### 1. Bubble Sort

Idea: Repeatedly swap adjacent elements if they are in the wrong order. Largest elements "bubble" to the end.

```python
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(n - 1 - i):  # last i elements are already sorted
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
```

* Time: O(n²) worst/avg, O(n) best (already sorted)
* Space: O(1)
* Simple but inefficient

---

### 2. Selection Sort

Idea: Repeatedly select the minimum element and move it to the beginning.

```python
def selection_sort(arr):
    n = len(arr)
    for i in range(n):
        min_idx = i
        for j in range(i+1, n):
            if arr[j] < arr[min_idx]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
```

* Time: O(n²) always
* Space: O(1)
* Better than bubble, still bad for large lists

---

### 3. Insertion Sort

Idea: Build the sorted array one element at a time by inserting each item into its correct position.

```python
def insertion_sort(arr):
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >=0 and arr[j] > key:
            arr[j+1] = arr[j]
            j -= 1
        arr[j+1] = key
```

* Time: O(n²) worst/avg, O(n) best (nearly sorted)
* Space: O(1)
* Good for small or nearly sorted data

---

## 🔥 Efficient Sorting Algorithms

### 4. Merge Sort (Divide & Conquer)

Idea: Recursively split the array in half, sort each half, and merge them.

```python
def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return merge(left, right)

def merge(left, right):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        result.append(left[i] if left[i] < right[j] else right[j])
        if left[i] < right[j]:
            i += 1
        else:
            j += 1
    result.extend(left[i:] or right[j:])
    return result
```

* Time: O(n log n) all cases
* Space: O(n)
* Very stable and consistent

---

### 5. Quick Sort (Divide & Conquer)

Idea: Pick a pivot, partition array into elements < and > pivot, and recursively sort both sides.

```python
def quick_sort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[0]
    less = [x for x in arr[1:] if x < pivot]
    greater = [x for x in arr[1:] if x >= pivot]
    return quick_sort(less) + [pivot] + quick_sort(greater)
```

* Time: O(n log n) avg, O(n²) worst (bad pivot)
* Space: O(log n) average (call stack)
* Very fast in practice, but unstable

---

### 7. Counting Sort

Idea: Count how many times each value appears. Only works with non-negative integers in a known range.

```python
def counting_sort(arr):
    count = [0] * (max(arr) + 1)
    for num in arr:
        count[num] += 1
    sorted_arr = []
    for i, c in enumerate(count):
        sorted_arr.extend([i] * c)
    return sorted_arr
```

* Time: O(n + k) where `k` is the range of input
* Space: O(k)
* Very fast if range is small; not a comparison sort


### Summary Table

| Algorithm      | Time (Best) | Time (Worst) | Space    | Stable | Notes                     |
| -------------- | ----------- | ------------ | -------- | ------ | ------------------------- |
| Bubble Sort    | O(n)        | O(n²)        | O(1)     | Yes    | Educational only          |
| Selection Sort | O(n²)       | O(n²)        | O(1)     | No     | Rarely used               |
| Insertion Sort | O(n)        | O(n²)        | O(1)     | Yes    | Great for small inputs    |
| Merge Sort     | O(n log n)  | O(n log n)   | O(n)     | Yes    | Always safe choice        |
| Quick Sort     | O(n log n)  | O(n²)        | O(log n) | No     | Fastest in practice       |
| Heap Sort      | O(n log n)  | O(n log n)   | O(1)     | No     | Good worst-case guarantee |
| Counting Sort  | O(n + k)    | O(n + k)     | O(k)     | Yes    | Non-comparison based      |


## 2 Pointers

The 2 pointer technique involves using 2 different pointers to iterate through a list. There are various ways these can be utilized:

- Starting at index 0 and at index 1, and then iterating the right pointer by one and comparing the values at these 2 indexes
    - These solutions are often (`n^2`) because you're iterating over every item in the list twice
- Starting with the left pointer at index 0 and the right pointer at `len(list) - 1` which is at the last value of the list
    - If the list is sorted, this is particularly effective in a problem like two sum where you can increment the left pointer by 1, or decrement the right pointer by 1 until you find some target value you're looking for

## Dynamic Programming

Dynamic Programming (DP) is a powerful technique used in computer science to solve optimization problems and combinatorial problems by breaking them down into smaller overlapping subproblems, solving each subproblem just once, and storing the result for future reuse.

1. Dynamic programming = recursion + memoization
2. Dynamic programming = building up solutions bottom-up using a table (tabulation

To apply DP, your problem must have:

- Overlapping Subproblems: The problem can be broken down into smaller subproblems which are reused multiple times.
- Optimal Substructure: The optimal solution to the problem can be built from optimal solutions to its subproblems.

Examples:

1. Fibonacci Sequence
   - Recursive solution is inefficient due to repeated calculations.
   - DP stores results of previous calculations to avoid redundant work.

``` python
# top down memoization
# You use recursion, but cache (memoize) the results of each subproblem.

def fib(n, memo={}):
    if n in memo:
        return memo[n]

    if n <= 1:
        return n

    memo[n] = fib(n-1, memo) + fib(n-2, memo)
    return memo[n]

# bottom up tabulation
# You build up solutions from the smallest subproblem iteratively.
def fib(n):
    if n <= 1:
        return n

    dp = [0, 1]

    for i in range(2, n + 1):
        dp.append(dp[i - 1] + dp[i - 2])

    return dp[n]
```

2. Knapsack Problem
   - Given weights and values of items, find the maximum value that can be carried in a knapsack of a given capacity.
   - DP builds a table where each entry represents the maximum value for a given weight limit.

``` python



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
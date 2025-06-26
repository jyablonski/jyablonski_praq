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

## Sliding Window

The sliding window technique is a powerful method for solving problems that involve contiguous subarrays or substrings. It allows you to maintain a subset of elements in a data structure while iterating through the array, which can lead to more efficient solutions than brute force methods.

There are two main types of sliding window techniques:
1. **Fixed-size Sliding Window**: The window size is constant, and you slide the window across the array.
2. **Variable-size Sliding Window**: The window size can change based on certain conditions, expanding or contracting as needed.

It's useful for problems involving:
- Finding the maximum or minimum sum of a subarray of a fixed size.
- Finding the longest substring with unique characters.

If you know the length of the subsequence you are looking for, use a fixed-length sliding window. Otherwise, use a variable-length sliding window.


``` python
def variable_length_sliding_window(nums):
  state = # choose appropriate data structure
  start = 0
  max_ = 0

  for end in range(len(nums)):
    # this syntax will keep track of the count of the current element in the state
    state[s[end]] = state.get(s[end], 0) + 1
    # extend window
    # add nums[end] to state in O(1) in time

    while state is not valid:
      # repeatedly contract window until it is valid again
      # remove nums[start] from state in O(1) in time
      start += 1

    # INVARIANT: state of current window is valid here.
    max_ = max(max_, end - start + 1)

  return max_
```

## Stack

Stacks are a data structure of elements that follow the LIFO principle, which means the last element added to the stack is the first to be removed

- New elements are pushed onto the stack
- Old elements that are removed are popped from the stack
- Both operations take O(1) time
- In Python, Arrays `[]` can be used as a stack

A monotonic stack is a special type of stack in which all elements on the stack are sorted in either descending or ascending order. It is used to solve problems that require finding the next greater or next smaller element in an array.

## Greedy Algorithms

Greedy algorithms are a category of algorithms in data structures and algorithms (DS&A) where decisions are made step by step, choosing the locally optimal solution at each step with the hope that this leads to a globally optimal solution.

A globally optimal solution can be arrived at by making a locally optimal (greedy) choice at each step.

- You don't need to consider all possibilities (like in dynamic programming or backtracking).
- Once you make a choice, you never reconsider it

A problem has an optimal substructure if an optimal solution to the problem contains optimal solutions to its subproblems.

- Greedy and dynamic programming both require this property.
- But greedy doesn't require overlapping subproblems (unlike DP).

Greedy problems often involve sorting elements by some criteria, and are generally faster than dynamic programming because they're not considering all possible solutions

``` py
def solution(prices: list[int]) -> int:
    min_price = prices[0]
    max_profit = 0

    for price in prices:
        min_price = min(min_price, price)
        max_profit = max(max_profit, price - min_price)

    return max_profit
```

## Depth First Search

DFS is a traversal algorithm to visit all nodes in a tree or graph data structure. It starts at the root node and tries to go down as far as possible until reaching a leaf node, when it reaches a leaf node, it backtracks to the closest parent node to explore the next path.

- It's typically implemented as a recursive function, and visits new nodes by making recursive calls
- As we make recursive calls to traverse down the tree, we keep pushing call frames onto the call stack until we reach our first base case, where node is None.
- Backtracking occurs whenever a recursive call returns. The call frame is popped off the call stack, and execution returns to the next call frame on the call stack.
- Time complexity is o(n) beacuse we have to visit each node exactly once

Binary trees are typically used in these algorithms and they have key attributes & characteristics:

- The top node of a binary tree is called the root
- Each node in a binary tree can have at most 2 children, a left child and right child
- A node that does not have any children is called a leaf node
- The height (or depth) of a binary tree is the number of edges on the longest path between the root node and a leaf node
- A balanced binary tree is one where the height of the left or right subtrees of every node differs by at most 1
- A binary tree is "complete" if every level, except possibly the last, is completely filled, and all nodes are as far left as possible
    - A complete binary tree has a height of O(log(n)), where n is the number of nodes in the tree.


A binary search tree (BST) is a binary tree where:

- All nodes in the left subtree have a value less than the root
- All nodes in the right subtree have a value greater than the root


``` py
# template to act as a starting point to solve binary tree problems with DFS
def dfs(node):
    # base case
    if node is None:
        return some value
    
    ...
    
    left = dfs(node.left)
    right = dfs(node.right)
    return value based on left and right

```

- This is a template for solving DFS Problems

To determine what the return value should be for a different problem, imagine you're at a node in the tree and ask yourself: "What information do I need from my left and right subtrees to solve the problem for my subtree?"

- If the problem is to find the max value in a binary tree, then your return would be something like:

``` py
def maxValue(node):
    if node is None:
        return float('-inf')
    
    if node.left is None and node.right is None:
        return node.val

    left = maxValue(node.left)
    right = maxValue(node.right)
    return max(left, right, node.val)
```

In some cases, questions require us to pass information "down" from parents to child nodes, which we do via the parameters of our recursive function. If we need more parameters than the original function signature allows, then we need to introduce a helper function to help us recurse.

- Questions involving root-to-leaf paths are common examples of where using helper functions are necessary, as we can use the helper function to introduce extra parameters that store the state of our current path.
- Sometimes we may also want to use a global variable defined in the main function that we append to or modify in the helper function. In this case, define it and then run `nonlocal var_name` in the helper function to access it.

``` py
def goodNodes(root):
    # nodes is a "global" var in the context of this function and its child functions
    # this is best practice and good to mention that you know the knowledge of variable scoping
    nodes = []
    def dfs(root, max_):

        # use this syntax if youi want to access nodes or append to it from the helper function
        nonlocal nodes

        return ...

    dfs(root, float("inf"))

    return nodes
```

Return Values - If I'm at a node in the tree, what values do I need from my left and right children to calculate xyz of the subtree rooted at the current node?


## Examples

1. Given a binary tree, use Depth-First Search to find the sum of all nodes in the tree.

``` py

# Given a binary tree, use Depth-First Search to find the sum of all nodes in the tree.
def dfs(node):
    # base case: empty subtree
    if node is None:
        return 0
    
    # base case: leaf node
    if node.left is None and node.right is None:
        return node.val
    
    left = dfs(node.left)
    right = dfs(node.right)
    return left + right + node.val
```

- Formula is basically root node + sum(left subtree) + sum(right subtree)
- The base cases are the subproblems we can solve directly (without making any recursive calls):

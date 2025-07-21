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

3. The climbing stairs problem can be solved with recursion, but it would take o(n^2) time and a lot of repeat work has to be done. A better solution is DP.

- DP makes sense when the problem has optimal substructure, which is to say if an optimal solution to the problem contains optimal solutions to subproblems.
- If we know the number of ways to climb 3 steps and 4 steps, then we can add those together to get the number of ways we can get to 5 steps
- So, if a problem has optimal substructure (it can be solved using recursion), and there are overlapping subproblems (the same recursive call is made multiple times), then we can use dynamic programming to handle the overlapping subproblems more efficiently.
- The two ways of doing that are only solve each subproblem once

Memoization is a strategy where we save the results of every subproblem that we've solved to eliminate any subsequent recursive calls that might go try to solve the same problem again.

- This reduces the time complexity from O(2^n) to O(n)
- This is known as a top down approach
- But, keep in mind we still might be making unnecessary recursive calls, even if their answer is cached

``` py
# the recursive way 
def climbStairs(n):
    # base cases
    if n <= 1:
        return 1
    
    return climbStairs(n - 1) + climbStairs(n - 2)

# the memo way
def climbStairs(n: int) -> int:
    memo = {}
    
    def climb_helper(i: int) -> int:
        if i <= 1:
            return 1
        
        # check if value is already in cache
        # before making recursive calls
        # corresponds to the green nodes in the diagram
        if i in memo:
            return memo[i]
        
        # store result in cache before returning
        memo[i] = climb_helper(i - 1) + climb_helper(i - 2)
        return memo[i]
    
    return climb_helper(n)

# bottom up approach
def stairs(n):
    if n <= 1:
        return 1
    dp = [0] * (n + 1)

    dp[0] = 1
    dp[1] = 1
    for i in range(2, n + 1):
        dp[i] = dp[i - 1] + dp[i - 2]
    return dp[n]
```

The other solution is to use a bottom up approach by using the previous 2 series of steps to calculate the number of ways to climb the next step

- Here, we start from climbstairs(0) -> 1 and go up to `n`

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

- It's typically implemented as a recursive function w/ a stack, and visits new nodes by making recursive calls
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

``` py
# check if you're trying to call past a leaf node - this is necessary so you dont try running node.val or node.left
# on a node that doesn't exist
if not node:
    return

# check if you're at a leaf node
if not node.left and not node.right:
    print(f"were at a leaf node")
```

DFS Types

1. Preorder - Process each node as you come across it (root -> left -> right)
2. Inorder - Go down to leaf nodes before you start processing nodes, and then backtrack and process nodes as you come across them (left -> root -> right)
3. Postorder - Go left, then right, and then current node

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

## Breadth First Search

BFS is a level by level traversal algorithm that starts at a node in a tree or graph like data structure and processes all nodes at the current level before moving to the nodes at the next level.

It uses a queue to keep track of nodes it needs to visit, and follows these steps:

- Starts at the root node and adds it to the queue
- While the queue is not empty, remove the node at the front and visit it
- Add the children of the node to the back of the queue
- Repeats step 2 and 3 until the queue is empty

Compared to depth-first search, BFS makes it much easier to tell when we have finished processing all nodes at a particular level.

- This makes it a natural candidate for questions that ask something about the nodes at each level

``` py
from collections import deque

def bfs(root):
  if not root:
    return []

  result = []
  queue = deque([root])

  while queue:
    curr_node = queue.popleft()
    result.append(curr_node.val)
    
    if curr_node.left:
      queue.append(curr_node.left)
    if curr_node.right:
      queue.append(curr_node.right)

  return result
```

## Graphs

Depth-First Search is also used to solve interview questions involving graphs. Graphs are typically represented in two ways: an adjacency list or as a matrix, and each has a different method of implementing DFS.

Graphs consist of:

- Nodes which are also known as verticies
- Edges which connect the nodes together
- Nodes that are connected to each other via an edge are known as neighbors of that node

Graphs can contain cycles, which is a path that starts and ends on the same node. Graphs can also have connected and disconnected components. A connected graph is a graph where there is a path between every pair of nodes. (A tree is a connected graph with no cycles.)

A disconnected graph is a graph where there are at least two nodes that are not connected to each other by a path. This is basically like 2 distinct graphs.

Graphs can be either directed or undirected. In a directed graph, edges between nodes only go in one direction. In an undirected graph, edges between nodes go in both directions. For the most part, the graphs that you will encounter during the coding interview will be undirected.

An adjacency list is a common way to represent a graph. In an adjacency list, we are given a list of nodes, where each node is mapped to a list of its neighbors. These can be created in Python using a dictionray where the keys are nodes and the values are the list of nodes each node is connected to:

``` py
adjList = {    
    1: [2],    
    2: [1, 3, 4],    
    3: [2, 4],    
    4: [2, 3, 5],    
    5: [4]    
}    
```

- Adjacency lists allow you to look up the neighbors of any node in O(1) time, which is a necessary step for depth-first search.

Given an integer n which represents the number of nodes in a graph, and a list of edges edges, where edges[i] = [ui, vi] represents a bidirectional edge between nodes ui and vi, write a function to return the adjacency list representation of the graph as a dictionary. The keys of the dictionary should be the nodes, and the values should be a list of the nodes each node is connected to.

``` py
# edges = [[0, 1]] means node 0 is connected to node 1
n = 4
edges = [[0, 1], [1, 2], [2, 3], [3, 0], [0, 2]]

def build_adj_list(n, edges):
    # build the dictionary with all the keys we need and with empty lists as the value
    adj_list = {i: [] for i in range(n)}


    for u, v in edges:
        adj_list[u].append(v)
        adj_list[v].append(u)

    return adj_list

# we had 5 pairs, so we have 10 total values in the sum of all lists here
{
    0: [1, 3, 2],
    1: [0, 2],
    2: [1, 3, 0],
    3: [2, 0]
}
```

DFS for a graph is conceptually similar to DFS on a binary tree. The algorithm tries to go as deep as possible along a path before backtracking to explore other paths. The main differences are:

- Each node can have any amount of neighbors, so we need a `for loop` to iterate over each neighbor
- Because graphs can contain cycles, we have to keep track of nodes we have already visited. If we encounter one, we need to return immediately without making any further recursive calls to avoid getting into an infinite loop
- No need for explicit base case, we just need to iterate through all nodes in the graph and the recursion will stop on its own

``` py
# basic DFS implementation on adjacency list
def dfs(adjList):
  if not adjList:
    return

  visited = set()

  def dfs_helper(node):
    if node in visited:
      return

    visited.add(node)

    for neighbor in adjList[node]:
      dfs_helper(neighbor)

    return

  # Handle disconnected components
  for node in adjList:
    if node not in visited:
      dfs_helper(node)
```

- Use a set to keep track of visited nodes
- If you encounter a node you've already visited, return immediately
- Use a for loop to iterate ovewr each neighbor of the current node, and recursively call `dfs` on each neighbor


## Intervals

Interval problems typically involve sorting given interval lists, and then processing each interval in order.

- They're given as a list of `[start, end]` times

Sorting intervals by their start times makes it easy to merge 2 intervals that are overlapping

- After sorting by start time, an interval overlaps with the previous interval if it starts before the end time of the previous interval
- Detecting overlapping intervals is the basis for many leetcode questions
- Solutions involve sorting by start times and then iterating over each one. If the current one overlaps with the previous one, then you found your answer

When an interval overlaps with the previous interval in a list of intervals sorted by start times, they can be merged into a single interval.

- To merge an interval into a previous interval, we set the end time of the previous interval to be the max of either end time.
- `prev_interval[1] = max(prev_interval[1], interval[1])`

Sometimes you'll want to sort by end time instead of start time

- Example: finding the max number of non-overlapping intervals in a given list of intervals
- If we sort by start time, we risk adding an interval that starts early but ends late, which will block us from adding other intervals until that interval ends.
- If instead we sort by end time, we can start by adding the intervals that end the earliest. Intuitively, this frees time for us to add more intervals as early as possible, and yields the correct answer.
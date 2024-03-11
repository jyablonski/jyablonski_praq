# Algorithms
Algorithms are a series of step-by-step instructions to solve a particular problem.  We use algorithms to solve problems consistently, correctly, and efficiently.

A problem is a specific task or question that requires a solution or an answer.

Interfaces are like a specification for an algorithm, and a data structure is a way to implement an interface.

## Asymtopic Analysis
Asymptotic analysis is a technique in computer science and mathematics used to analyze the behavior and performance of algorithms as the size of the input approaches infinity or becomes very large. It helps in understanding how the algorithm's time and space complexity scales with increasing input sizes.

The goal of asymptotic analysis is to describe the algorithm's efficiency in a way that is independent of hardware, operating system, programming language, and other implementation-specific details. It provides a high-level view of the algorithm's behavior and helps compare algorithms in terms of their efficiency and scalability.

Asymptotic analysis uses mathematical notation to describe the upper and lower bounds on the algorithm's performance. The most common notations used in asymptotic analysis are:

1. **Big O (O)** Notation: Represents the upper bound or worst-case time complexity of an algorithm. It gives an upper limit on the growth rate of the algorithm's running time as the input size increases. For example, O(n) represents linear time complexity.

2. **Omega (Ω)** Notation: Represents the lower bound or best-case time complexity of an algorithm. It gives a lower limit on the growth rate of the algorithm's running time. For example, Ω(n) represents linear time complexity.

3. **Theta (θ)** Notation: Represents both the upper and lower bounds, providing a tight bound on the algorithm's time complexity. For example, θ(n) represents that the algorithm has a linear time complexity, and its running time grows linearly with the input size.

Asymptotic analysis helps in classifying algorithms into broad categories based on their efficiency and scalability. It allows developers and researchers to make informed decisions about which algorithm to use based on the problem's requirements and the size of the input.

For example, an algorithm with O(n^2) time complexity may be efficient for small input sizes but inefficient for large input sizes, making it necessary to explore more efficient alternatives for scalability.

## Algorithmic Performance
![image](https://github.com/jyablonski/jyablonski_praq/assets/16946556/5b791fab-57fa-45e2-9f51-daeea71514a7)

1. O(1) Constant Time
   1. Accessing an element from an Array by Index
   2. Appending an Item to an Array
   3. Accessing a value in a Dictionary by Key
2. O(log(n)) Logarithmic Time
   1. Binary Search
3. O(n) Linear Time
   1. Traversing through every element in an Array
4. O(n log(n)) Linearithmic Time
   1. Merge Sort
5. O(n^2) Quadratic Time
   1. Bubble Sort
   2. Selection Sort
   3. Insertion Sort

## Data Structures

### Arrays
An array is a fundamental data structure used in computer programming to store a collection of elements, each identified by an index or a key. The elements in an array are stored sequentially in memory, making it easy to access and manipulate them based on their position.

Here are some key characteristics and features of array data structures:

1. **Ordered Collection**: Arrays are ordered collections of elements, meaning that the elements are stored in a specific order based on their index.

2. **Fixed Size**: In many programming languages, arrays have a fixed size, meaning the number of elements they can hold is determined when they are created and cannot be changed dynamically.

3. **Index-Based Access**: Elements in an array are accessed using their index, which is typically an integer value. The index allows for efficient and direct access to specific elements.

4. **Zero-Based Indexing**: In most programming languages, array indexing starts at 0. The first element is accessed using index 0, the second with index 1, and so on.

5. **Homogeneous Data Type**: In most cases, arrays store elements of the same data type, such as integers, floating-point numbers, characters, or custom objects.

6. **Efficient Access**: Accessing elements in an array is efficient because you can access any element directly using its index.

7. **Contiguous Memory Allocation**: Array elements are stored in contiguous memory locations, which allows for efficient memory access and faster iteration through the elements.

8. **Static or Dynamic Allocation**: Some programming languages allow for dynamic arrays, where the size can be changed dynamically during runtime, while others have static arrays with a fixed size.


### Set
Sets are a collection of distinct unique elements in no specific order
- Build - Given an iterable A, build sequence from items in A
- len - return number of stored items
- find - return stored item with key k
- insert - add x to set (and replace item with key x.key if one already exists)
- delete - remove and return stored item with key k
- iter order
- find min - return item with smallest key
- find max - return item with highest key
- find next - return item with smallest key larger than k
- find prev - return item with largest key smaller than k

Building an unsorted array is much faster than building a sorted array.  But, once a sorted list of numbers is built, operations such as finding k or finding prev or next k become much faster (log n time).

### Sequences
Sequences are a type of data structure that allow ordered arrangement of items of any type such as number, character, or even other data structures.  this allows for get_at, set_at, insert_at etc type of operations
- inserting or deleting at beginning of sequence is 0(1) time, so super fast + efficient.  but every other insert or delete kinda blows.
- Store n elements together in Memory.  Each item in the linked list 
- [x, y] -> [z, a]

## Hashing
[Article](https://adamgold.github.io/posts/python-hash-tables-under-the-hood/)

Python dictionaries are implemented as hash tables, which are a common data structure used for efficient lookups and insertions. The specific implementation details can vary between different versions of Python and across different implementations (CPython, PyPy, Jython, etc.), but the core concept remains the same.

Here's a high-level overview of how Python dictionaries are typically implemented using a hash table:

1. **Hash Function:**
   Python uses a hash function to convert keys (e.g., strings, integers) into hash values, which are numerical representations of the keys. The hash function should distribute keys evenly to minimize collisions (different keys mapping to the same hash value).

2. **Hash Table Structure:**
   The hash table is an array (or a collection of arrays) with a fixed number of slots or buckets. Each slot can hold a key-value pair or a reference to a linked list or other data structure containing key-value pairs.

3. **Hash Value to Index:**
   The hash value obtained from the hash function is used to determine the index (position) in the hash table where the key-value pair will be stored. Typically, the hash value is transformed into a valid index within the array using a modulo operation with the size of the hash table.

4. **Collision Handling:**
   Collisions occur when two or more keys hash to the same index. To handle collisions, Python uses techniques like chaining or open addressing.
   - **Chaining:** Each bucket in the hash table contains a linked list or other data structure that stores all key-value pairs hashing to the same index. This allows multiple key-value pairs to coexist at the same index.
   - **Open Addressing:** When a collision occurs, the algorithm looks for the next available (unoccupied) slot in the hash table to store the key-value pair.

5. **Insertion and Lookup:**
   To insert a key-value pair, the hash value is computed for the key, the appropriate index in the hash table is determined, and the key-value pair is stored in that location (either by adding to the linked list or occupying the slot).
   For lookups, the hash value of the key is computed again to find the index and retrieve the value associated with the key.

Python's dictionaries are designed to provide fast average-case performance for inserting, retrieving, and deleting key-value pairs, with a time complexity of O(1) for these operations, assuming a good hash function and a relatively uniform distribution of keys. However, in the worst case (e.g., with many collisions), the time complexity can degrade to O(n), where n is the number of key-value pairs in the dictionary.

## Breadth First Search
Breadth-First Search (BFS) is an algorithm used for traversing or searching tree or graph data structures. It starts at a specific node (often called the "source" node) and explores its neighbors before moving on to the next level of neighbors. In other words, it explores all the neighbors at the present depth prior to moving on to nodes at the next depth level.

Here's a step-by-step description of the Breadth-First Search algorithm:

1. **Start at a Source Node:**
   Begin with a designated source node (or starting point) in the graph or tree.

2. **Explore Neighbors:**
   Explore all the neighbors (adjacent nodes) of the source node first. These are the nodes directly connected to the source node.

3. **Visit in Order of Discovery:**
   Visit the neighbors in the order in which they were discovered. This is typically achieved using a queue data structure to manage the order of exploration.

4. **Queue the Neighbors:**
   Enqueue (add to the end of the queue) all the neighbors of the source node.

5. **Process the Next Node:**
   Dequeue (remove from the front of the queue) the next node to be processed. This node becomes the new source node for further exploration.

6. **Repeat the Process:**
   Repeat steps 2-5 for the newly selected source node (now at the front of the queue), exploring its neighbors and enqueueing any unvisited neighbors.

7. **Terminate When Complete:**
   Continue this process until all nodes have been visited, or until a specific condition or node is reached.

BFS is typically implemented using a queue data structure, which ensures that nodes are processed in the order they were discovered. This property of BFS ensures that it explores nodes level by level, making it particularly useful for tasks like finding the shortest path in an unweighted graph, or traversing a tree or graph in a systematic way.

BFS has a time complexity of O(V + E), where V is the number of vertices (nodes) and E is the number of edges in the graph or tree.

## Depth-first Search
Depth-First Search (DFS) is an algorithm used for traversing or searching tree or graph data structures. Unlike Breadth-First Search (BFS), which explores all neighbors at a given level before moving on to the next level, DFS explores as far as possible along each branch before backtracking.

Here's a step-by-step description of the Depth-First Search algorithm:

1. **Start at a Source Node:**
   Begin with a designated source node (or starting point) in the graph or tree.

2. **Explore a Neighbor:**
   Choose a neighbor of the source node and explore it as deeply as possible.

3. **Backtrack When Necessary:**
   If you reach a node with no unvisited neighbors, backtrack to the previous node and explore any remaining unvisited neighbors from there.

4. **Repeat the Process:**
   Continue this process, choosing the deepest unexplored node, until all nodes have been visited.

DFS can be implemented using recursion or by using a stack (either explicitly or through the call stack). The algorithm effectively goes as deep as possible along each branch before backtracking, which is why it's called "depth-first."

DFS has different variants, such as Inorder, Preorder, and Postorder traversal, based on the order in which nodes are visited.

- **Inorder DFS:**
  Visit the left subtree, visit the root, visit the right subtree.
  
- **Preorder DFS:**
  Visit the root, visit the left subtree, visit the right subtree.
  
- **Postorder DFS:**
  Visit the left subtree, visit the right subtree, visit the root.

DFS is versatile and can be applied to solve a variety of problems, including cycle detection, topological sorting, pathfinding, and more. However, it's important to note that DFS does not necessarily find the shortest path, and it may get stuck in an infinite loop if the graph contains cycles (in the case of graphs).

DFS has a time complexity of O(V + E), where V is the number of vertices (nodes) and E is the number of edges in the graph or tree.
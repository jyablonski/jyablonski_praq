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
1. O(1)
2. O(log(n))
3. O(n)
4. O(n log(n))
5. n^2
6. n^3


## Sorting Algorithms
n^2 Sorting
1. Selection Sort
2. Bubble Sort
3. Insertion Sort
   
n log(n) Sorting 
1. Merge Sort
2. 

# Data Structures

## Set
Interface - Functions for Set.
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

## Linked List
Linked Lists
- Store n elements together in Memory.  Each item in the linked list 
- [x, y] -> [z, a]
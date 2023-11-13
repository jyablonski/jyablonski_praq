# Python Vectorization
[Article](https://pythonspeed.com/articles/pandas-vectorization/)
Vectorization is the idea of parallelizing operations.  You can do this in Python by building C++ or Rust bindings for particular operations, which is what Numpy does.

In the context of Python, vectorization means to apply an operation across an entire Series or DataFrame at once.

## Arithmetic
```py
# ... Vectorized operation:
df["ratio"] = 100 * (df["x"] / df["y"])

# ... Non-vectorized operation:
def calc_ratio(row):
    return 100 * (row["x"] / row["y"])
```

Vectorized:     0.0043 secs
Non-vectorized: 5.6435 secs

It's able to do this because Python knows the data is in a Pandas Series which are built off of Numpy Arrays, and it can pass the operation onto the entire underlying array at once.


## Strings

```py
# ... Vectorized operation:
df["sentence_length"] = df["sentences"].str.split().apply(
    len
)

# ... Non-vectorized operation:
def sentence_length(s):
    return len(s.split())

df["sentence_length2"] = df["sentences"].apply(
    sentence_length
)
```

Vectorized:     1.492 secs
Non-vectorized: 0.280 secs

It's actually much slower!  The vectorized solution uses much more memory and strings are trickier to work with than raw numbers + floats.

## Numpy
Vectorization is a powerful concept in computer programming, and in the context of Python, the NumPy library is a popular choice for performing vectorized operations efficiently. Vectorization allows you to apply operations to entire arrays or vectors of data rather than iterating over each element one by one, making your code more concise and often significantly faster.

Here's a walk-through of Python vectorization using the NumPy package and an explanation of how it works:

1. **Import NumPy:**
   First, you need to import the NumPy library. You typically do this at the beginning of your Python script or in a Jupyter Notebook:

   ```python
   import numpy as np
   ```

   This imports NumPy and provides the alias "np" for convenience.

2. **Creating NumPy Arrays:**
   NumPy primarily deals with `numpy.ndarray` objects, which are multi-dimensional arrays. You can create these arrays in various ways, such as from Python lists or using NumPy functions.

   ```python
   # Create a NumPy array from a Python list
   my_list = [1, 2, 3, 4, 5]
   my_array = np.array(my_list)

   # Create a NumPy array with a range of values
   my_range = np.arange(1, 6)  # Creates an array [1, 2, 3, 4, 5]
   ```

3. **Performing Vectorized Operations:**
   The real power of NumPy comes into play when you perform operations on these arrays. You can apply arithmetic operations, functions, and more to entire arrays at once. NumPy will internally handle element-wise operations efficiently without the need for explicit loops.

   ```python
   # Element-wise addition
   result = my_array + 10  # Adds 10 to each element in the array

   # Element-wise multiplication
   result = my_array * 2   # Multiplies each element by 2
   ```

4. **Universal Functions (ufuncs):**
   NumPy includes a vast library of universal functions (ufuncs) that are optimized for performance. These functions can be applied element-wise to arrays.

   ```python
   # Example of a NumPy ufunc: square root
   result = np.sqrt(my_array)  # Computes the square root of each element
   ```

5. **Broadcasting:**
   NumPy allows you to operate on arrays of different shapes, as long as they are broadcastable. Broadcasting means that NumPy can automatically adjust the shapes of the input arrays to make the operation possible.

   ```python
   a = np.array([1, 2, 3])
   b = 2
   result = a + b  # The scalar 'b' is broadcasted to [2, 2, 2] for the addition
   ```

6. **Aggregation and Reduction:**
   NumPy provides functions for aggregating and reducing data in arrays, such as `sum()`, `mean()`, `min()`, `max()`, and many others. These functions operate over the entire array or along specified axes.

   ```python
   # Compute the sum of all elements in the array
   total = np.sum(my_array)

   # Calculate the mean value of the elements
   mean = np.mean(my_array)
   ```

7. **Indexing and Slicing:**
   You can use NumPy's indexing and slicing capabilities to extract and manipulate elements or sub-arrays efficiently.

   ```python
   sub_array = my_array[1:4]  # Get a sub-array containing elements 2, 3, and 4
   ```

NumPy's underlying C implementation and use of contiguous memory make it highly efficient for vectorized operations. This is particularly beneficial when working with large datasets, numerical computations, and scientific computing tasks. It's an essential library for data scientists, machine learning practitioners, and anyone dealing with numerical data in Python.

### Numpy's Design
Numpy is implemented in C and Python and has several design features and optimizations that enable its superior performance for numerical and array operations. Here are some key internals and techniques that make Numpy efficient:

1. **Homogeneous Data Types:**
   NumPy arrays are homogeneous, which means that all elements in an array have the same data type. This allows for efficient memory storage and optimized operations because the data layout is predictable and can be aligned in memory.

2. **Contiguous Memory Layout:**
   NumPy stores data in a contiguous block of memory. This layout is memory-efficient and allows for efficient data access and vectorized operations. This is in contrast to Python lists, which can store elements scattered across memory.

3. **Vectorization with ufuncs:**
   NumPy uses universal functions (ufuncs) to perform element-wise operations. Ufuncs are implemented in C and are highly optimized. When you apply a ufunc to a NumPy array, it performs the operation efficiently across all elements without the need for Python-level iteration.

4. **Broadcasting:**
   NumPy implements broadcasting, which allows operations on arrays with different shapes. Broadcasting enables NumPy to extend smaller arrays to match the shape of larger arrays, making element-wise operations more flexible and efficient.

5. **Data Buffer and Metadata:**
   NumPy separates data from metadata. The data buffer contains the actual array elements, while metadata contains information about the array, such as shape, data type, and strides. This separation allows efficient sharing of data and slicing without copying.

6. **Strides:**
   Strides are a critical concept in NumPy that defines how data is accessed in memory. The stride for each dimension of an array determines the number of bytes to move in memory to reach the next element along that dimension. NumPy uses strides to efficiently traverse arrays and perform operations.

7. **Cython and Cython-Wrappers:**
   NumPy leverages Cython, a programming language that makes it easy to write C extensions for Python. Some parts of NumPy, especially extensions, are implemented in Cython for better performance.

8. **Memory Management:**
   NumPy provides efficient memory management, including reference counting and garbage collection. It ensures that memory is allocated and deallocated efficiently, preventing memory leaks.

9. **C-Level APIs:**
   NumPy provides C-level APIs that enable other libraries and tools to interface with NumPy arrays directly. This allows for seamless integration with other numeric and scientific computing libraries like SciPy.

10. **Efficient Algorithms and Data Structures:**
    NumPy uses efficient algorithms and data structures for common operations such as sorting, searching, and reshaping arrays. These algorithms are often implemented in C for performance.

11. **Multithreading and Parallelism:**
    NumPy can take advantage of multiple CPU cores and parallel processing in some operations. It uses libraries like OpenMP to optimize performance when available.

12. **Memory Views:**
    NumPy supports memory views that allow you to view data in one array with a different shape, data type, or strides without copying the data. This is particularly useful for efficiently working with sub-arrays.

NumPy's careful design and efficient implementation in C make it one of the most fundamental and high-performance libraries for numerical and array computations in the Python ecosystem. Its focus on array operations, data layout, and efficient memory management plays a crucial role in achieving its impressive performance.
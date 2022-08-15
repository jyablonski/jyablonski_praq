# importing the modules
import numpy as np
import timeit

# numpy arrays only hold 1 data type for the whole array; normal python lists can allow any data type and thus are less efficient during math operations.
# pandas series are built off of numpy arrays.

# use numpy vectorized operations where possible

# it's called vectorization when an operation is called to many similar elements of the same type.  cpu can process multiples of these in parallel
# rather than 1 by 1 at a time.

# vectorized sum
print(np.sum(np.arange(15000)))

print("Time taken by vectorized sum : ", end="")
# timeit(np.sum(np.arange(15000)))

# iterative sum
total = 0
for item in range(0, 15000):
    total += item
a = total
print("\n" + str(a))

print("Time taken by iterative sum : ", end="")
# timeit(a)

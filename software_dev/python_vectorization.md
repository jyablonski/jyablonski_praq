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
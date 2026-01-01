# Advanced Python

## Context Managers

Context Managers are a way to manage resources efficiently and ensure they're properly acquired and released. They are defined using the `with` statement.

A Context Manager is an object that defines the runtime context when a `with` statement is used. It sets up a context, runs some code, and cleans up the context afterwards. It does this with:

- `__enter__(self)` - Method called when execution flow enters the context of the `with` statement.
- `__exit__(self, exc_type, exc_value, traceback)` - Method called when the execution flow leaves the context of the `with` statement. It handles the cleanup of the resource.

```py
with open('example.txt', 'w') as file:
    file.write('Hello, World!')
```

Custom Context Manager Example

```py
class CustomContextManager:
    def __enter__(self):
        print("Entering the context")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        print("Exiting the context")

with CustomContextManager() as manager:
    print("Inside the context")
```

An easier way to do this is to use the `contextmanager` Decorator.

```py
from contextlib import contextmanager

@contextmanager
def custom_context():
    print("Entering the context")
    try:
        yield
    finally:
        print("Exiting the context")

with custom_context():
    print("Inside the context")
```

SQLAlchemy uses this with its context managers to handle Database connections as well as for transactions + rollbacks.

```py
    with engine.begin() as connection:
        write_to_sql_upsert(
            conn=connection,
            table_name="boxscores",
            df=boxscores,
            pd_index=["player", "date"],
        )
        write_to_sql_upsert(
            conn=connection, table_name="odds", df=odds, pd_index=["team", "date"]
        )
        write_to_sql_upsert(
            conn=connection,
            table_name="pbp_data",
            df=pbp_data,
            pd_index=[
                "hometeam",
                "awayteam",
                "date",
                "timequarter",
                "numberperiod",
                "descriptionplayvisitor",
                "descriptionplayhome",
            ],
        )
        write_to_sql_upsert(
            conn=connection, table_name="opp_stats", df=opp_stats, pd_index=["team"]
        )

```

- In this example, if the first 3 `write_to_sql_upsert` Succeed but the last one fails and returns any Error, then the entire transaction will be rolled back and none of the data will be inserted into the Database.
- I've coded `write_to_sql_upsert` up to just `pass` any Errors and log the failures to Slack. Because I'm using `pass`, if I have 9/10 upserts complete and 1 fail those 9 successful upserts will still get committed to the Database which is fine.

`engine.begin()` will automatically commit any changes to the database if it doesn't encounter an error within the context manager. With `engine.connect()` your transactions have to be explicitly committed or else it'll automatically roll things back at the end, even if every database statement was successful.

## Generators

Generators are a type of iterable, like lists or tuples, but unlike lists, they do not store their contents in memory. They generate the values on the fly and are more memory efficient, specifically when dealing with large datasets.

How does this compare to `return` ? The key difference between yield and return is that `return` ends the function entirely, while `yield` pauses the function, saving its state for the next call.

```py
def simple_generator():
    print("First Value")
    yield 1

    print("Second Value")
    yield 2

    print("Third Value")
    yield 3

gen = simple_generator()

# gen object
print(gen)

# `generator` class
print(type(gen))

# executes the print statements and the value in the gen
for value in gen:
    print(value)
```

Generators are particularly useful for generating infinite sequences where you don't want to store all values in memory.

```py
def infinite_sequence():
    num = 0
    while True:
        yield num
        num += 1

gen = infinite_sequence()

# dont need to process infinity, just specify the amount we want
# this prints 0-4
for i in range(5):
    print(next(gen))

# this prints 5-9
for i in range(5):
print(next(gen))
```

- `next()` retrieves the next value of the generator based on where the last yield statement ended up

Fibonacci Example w/ a generator

```py
def fibonacci_sequence():
    a = 0
    b = 1
    while True:
        yield a
        a, b = b, a + b

fib = fibonacci_sequence()

for _ in range(10):
    print(next(fib))
```

## Dictionary

Dictionaries in Python store key value pairs using a hash table under the hood

- When you insert a key value pair into a dictionary, Python computes a hash value for the key using the built in `hash()` function
- This hash value determines where the key value pair will be stored in an internal array
- This hash-based lookup makes dictionary operations very fast on average, achieving O(1) time complexity for inserts, deletes, and lookups.

The backing array stores the hash value of the key, the actual key, and the value.

- The actual key must also be stored in the event we run into a hash collision
- Without it, we wouldn't effectively be able to deal with collisions

Multiple keys can actually end up having the same hash index, so Python solves this via open addressing w/ probing

- If a collision occurs, Python searches for the next available slot using probing
- This means Python tries index i + 1, i + 4, i + 9 etc instead of just i

Python dictionaries automatically resize when the number of entries exceed a certain threshold (typically when the dictionary is 2/3 full)

- Resizing involves creating a new larger backing array (typically double the size), and re-hashing all existing key value pairs
- This is done to ensure the operations remain O(1) on average

The `hash()` Function in Python computes a unique integer hash value for a given object.

- Integers, Strings, Floats etc can all be hashed
- A hash of an integer actually just returns an integer - this is on purpose as integers are already unique and efficiently distributable
- Mutable Objects like Dictionaries or Lists cannot be hashed
- Python randomizes string hashes at runtime for security reasons.
- This means hash("hello") changes every time you restart Python.
- However, integer hashes are consistent.

Below is what it looks like in code

```python
d = {}
d["name"] = "Alice"

hash("name") → 123456789
index = hash("name") % table_size
index = 123456789 % 8 = 5
# so at index 5, Python stores: (123456789, "name", "Alice")

d["age"] = 30

# lets assume both name and age hash to index 5, causing a collision
hash("name") % table_size = 5
hash("age") % table_size = 5

# python performs open addressing with quadratic probing, and basically just stores
# age at index 6 instead

# now if we go to get the value for the key `age` out of the dictionary, it'll hash it
# and go to index 5, but it sees `name` instead of `age`. python will continue probing for the
# index which actually has `age` until it finds it
print(d["age"])
```

## Named Tuples

A named tuple is a subclass of a regular tuple that allows you to assign meaningful names to each element. This makes your code more readable and self-documenting while keeping the efficiency of a tuple.

Other bits about named tuples:

- They're immutable, unlike regular tuples
- Can be more memory efficient than dictionaries

```python
from collections import namedtuple

# Define a named tuple called 'Point' with fields 'x' and 'y'
Point = namedtuple("Point", ["x", "y"])

# Create an instance
p = Point(3, 4)

# Access values using dot notation
print(p.x)  # Output: 3
print(p.y)  # Output: 4

# Named tuples are still tuples, so indexing works too
print(p[0])  # Output: 3
print(p[1])  # Output: 4
```

## contextlib.contextmanager

`contextlib.contextmanager` is a decorator that allows you to create context managers using a generator function instead of defining a class with **enter** and **exit** methods

- Typically used for mangaging temporary resources like files, network connections, or database sessions where you want to ensure cleanup happens automatically.

The standard flow for using the decorator looks like below:

1. Set up before yielding anything
1. Yield a resource of some kind inside a `try` block in the function, so it can be used in a `with` block outside of the function
1. Cleanup the yield in a finally block to ensure cleanup happens no matter what (even if you run into an exception)

```python
from contextlib import contextmanager

@contextmanager
def my_context():
    print("🔹 Setup before yield")
    try:
        yield "Some Resource"  # Provide a resource
    finally:
        print("🧹 Cleanup after yield")

# Usage
with my_context() as resource:
    print(f"Using: {resource}")
    # If an exception happens here, cleanup still runs

@contextmanager
def open_file(file_name, mode):
    f = open(file_name, mode)
    try:
        yield f  # Provide the file object to the caller
    finally:
        f.close()  # Ensure file is closed

with open_file("example.txt", "w") as f:
    f.write("Hello, World!")

# File is automatically closed after exiting the 'with' block

@contextmanager
def database_session():
    session = create_db_session()
    try:
        yield session  # Provide the session
        session.commit()  # Commit changes if no error
    finally:
        session.close()  # Ensure session closes

with database_session() as session:
    session.query(User).all()

# the equivalent class based way of doing it
class OpenFile:
    def __init__(self, file_name, mode):
        self.file = open(file_name, mode)

    def __enter__(self):
        return self.file

    def __exit__(self, exc_type, exc_value, traceback):
        self.file.close()

# Usage
with OpenFile("example.txt", "w") as f:
    f.write("Hello, World!")
```

## super.init()

- `super()` is used in OOP to give access to methods in a parent class without explicitly naming it
- `super().__init__(...)` calls the parent class’s constructor, allowing the child class to inherit and initialize properties from the parent.

```python
class Product:
    def __init__(self, product_name, price):
        self.product_name = product_name
        self.price = price

# you need to pass in Product, AND call super init as well
class Book(Product):
    def __init__(self, product_name, price, author):
        # Call parent class's __init__ method
        super().__init__(product_name, price)
        self.author = author

# Creating an instance of Book
book = Book("Python Crash Course", 29.99, "Eric Matthes")

# Check attributes
print(book.product_name)  # Output: Python Crash Course
print(book.price)         # Output: 29.99
print(book.author)        # Output: Eric Matthes

# if you just did this, it wouldnt be enough for product name and price
# to be inherited
class Book(Product):
    def __init__(self, product_name, price, author):
        # Call parent class's __init__ method
        # super().__init__(product_name, price)
        self.author = author
```

## Function Overloading

Function Overloading involves using the `overload` decorator from typing. It helps mypy understand different return types based on input types.

We're basically saying if we DO pass in a string, then we expect to return a string. If we pass in an int, we expect to return an int.

Without overload, the best we can do is `def process(value: int | str) -> int | str:` where we're using an OR operator for both the inputs + output types. In this case, we cant force mypy to error out if we pass in a string and actually return an integer or something.

The implementation of the actual function should _not_ have an `overload` decorator on it.

```python
from typing import overload

# The ... (ellipsis) means this function has no implementation—it's just a type hint for mypy.

@overload
def process(value: int) -> int: ...

# example 1 without overload
def process(value: int | str) -> int | str:
    if isinstance(value, int):
        return value ** 2
    return value[::-1]

reveal_type(process(4))      # mypy: Revealed type is "int | str"
reveal_type(process("abc"))  # mypy: Revealed type is "int | str"

# example 2 w/ overload
@overload
def process(value: int) -> int: ...

@overload
def process(value: str) -> str: ...

def process(value: int | str) -> int | str:
    if isinstance(value, int):
        return value ** 2
    return value[::-1]

reveal_type(process(4))      # mypy: Revealed type is "int"
reveal_type(process("abc"))  # mypy: Revealed type is "str"


# this is basically shorthand for `process = overload(process)`
# don't need to call it w/ `overload()`
# You only use () if the decorator takes arguments.

@overload
def process(value: int) -> int: ...
```

## Decorators

```python
# decorator that doesnt take arguments
def my_decorator(func):
    def wrapper(*args, **kwargs):
        print("Before function call")
        result = func(*args, **kwargs)
        print("After function call")
        return result
    return wrapper

@my_decorator
def say_hello():
    print("Hello!")

say_hello()
# essentially equivalent to `say_hello = my_decorator(say_hello)`
# decorator -> wrapper
# @my_decorator

# decorator that does take arguments
def repeat(n):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for _ in range(n):
                func(*args, **kwargs)
        return wrapper
    return decorator

@repeat(3)
def greet():
    print("Hello!")

greet()

# outer -> decorator -> wrapper
# @my_decorator(arg)

```

## Classmethod

`@classmethod` is a decorator that defines a method as a class method, meaning it is bound to the class rather than an instance of a class

```python
class Example:
    instance_count = 0

    def __init__(self, name: str):
        self.name = name
        Example.increment_count()

    @classmethod
    def overwrite_name(cls):
        cls.name = "BARF"
        print("Class method", cls)

    @classmethod
    def increment_count(cls):
        cls.instance_count += 1

    @classmethod
    def get_instance_count(cls):
        return cls.instance_count

    @staticmethod
    def static_method():
        print("Static method")

s = Example(name="boo")
f = Example(name="try")

Example.overwrite_name()
Example.name
Example.get_instance_count()

# these aren't affected
print(s.name)
print(f.name)
```

Useful when:

- You want to modify a class-wide default value that all instances of the class share
- Global counters when you want to track how many instances of the class exist
- Configuration settings that affect all instances

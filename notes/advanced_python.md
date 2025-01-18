# Advanced Python

## Context Managers

Context Managers are a way to manage resources efficiently and ensure they're properly acquired and released. They are defined using the `with` statement.

A Context Manager is an object that defines the runtime context when a `with` statement is used. It sets up a context, runs some code, and cleans up the context afterwards. It does this with:

- `__enter__(self)` - Method called when execution flow enters the context of the `with` statement.
- `__exit__(self, exc_type, exc_value, traceback)` - Method called when the execution flow leaves the context of the `with` statement. It handles the cleanup of the resource.

``` py
with open('example.txt', 'w') as file:
    file.write('Hello, World!')
```

Custom Context Manager Example

``` py
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

``` py
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

``` py
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

``` py
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

``` py
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

``` py
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

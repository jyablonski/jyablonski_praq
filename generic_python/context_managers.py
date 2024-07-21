# the old school way
class CustomContextManager:
    def __enter__(self):
        print("Entering the context")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        print("Exiting the context")


with CustomContextManager() as manager:
    print("Inside the context")


# the decorator route
from contextlib import contextmanager


@contextmanager
def custom_context(x: int = 5):
    print(f"Entering the context with x = {x}")
    try:
        x = x**2
        yield
    finally:
        print(f"Exiting the context with x = {x}")


with custom_context():
    print("Inside the context")

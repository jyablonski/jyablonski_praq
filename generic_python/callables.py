from typing import Callable


# use callables whenever you need to pass in a function to another function?
def first_text(name: str):
    return f"hello world {name}"


def my_function(input_obj: Callable):
    return input_obj


result = my_function(first_text("jacob"))

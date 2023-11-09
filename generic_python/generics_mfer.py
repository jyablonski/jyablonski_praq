from typing import TypeVar

T = TypeVar("T")


def my_function(input_var: T) -> T:
    print(f"hello world input was {input_var}")

    return input_var


str_input = "hi"
int_input = 1

test1 = my_function(input_var=str_input)
test2 = my_function(input_var=int_input)

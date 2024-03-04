from typing import Generic, TypeVar

T = TypeVar("T")


def my_function(input_var: T) -> T:
    print(f"hello world input was {input_var} with type {type(input_var)}")

    return input_var


str_input = "hi"
int_input = 1

test1 = my_function(input_var=str_input)
test2 = my_function(input_var=int_input)


class Box(Generic[T]):
    def __init__(self, item: T):
        self.item = item

    def get_item(self) -> T:
        return self.item


# Usage
box_int = Box(5)  # inferred as Box[int]
box_str = Box("hello")  # inferred as Box[str]

type(box_int.get_item())

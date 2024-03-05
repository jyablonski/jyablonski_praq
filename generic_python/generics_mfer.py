from typing import Any, Generic, TypeVar
import sys


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

    def get_item_list(self) -> list[T]:
        return [self.item]

    def get_item_dict(self, input_str: str) -> dict[T, str]:
        if not isinstance(input_str, str):
            raise ValueError("use a string mfer")
        # return {"test": input_object}     # <--- this would fail mypy
        # return {self.item * 2: input_str} # <--- this would fail mypy
        return {self.item: input_str}


# Usage
box_int = Box(5)  # inferred as Box[int]
box_str = Box("hello")  # inferred as Box[str]

box_int.get_item_list()
type(box_int.get_item_list())
type(box_int.get_item_list()[0])

d = box_int.get_item_dict("hello_world")
sys.getrefcount(d)

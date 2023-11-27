from typing import Any, Callable, Literal, NamedTuple


class InvalidStatusType(Exception):
    pass


def test_str(input_str: str | None = None) -> bool:
    if isinstance(input_str, str):
        return True
    else:
        return False


def add(x: int, y: int) -> int:
    return x + y


# Example Function that takes a `Callable`
def apply_operation(operation: Callable, int1: int, int2: int):
    """
    Apply a given operation to two operands.

    Args:
        - operation (callable): A callable that takes two arguments and performs an operation.
        - int1 (int): First Int
        - int2 (int): Second Int

    Returns:
    The result of applying the operation to the operands.
    """
    return operation(int1, int2)


apply_operation(operation=add, int1=10, int2=15)


def test_literals(status: Literal["yes", "no", "maybe"]) -> int:
    if status not in ("yes", "no", "maybe"):
        raise InvalidStatusType("Status must be one of 'yes', 'no', or 'maybe'")

    if status == "yes":
        return 1
    elif status == "no":
        return 2
    else:
        return 3


test_literals(status="yes")
test_literals(status="no")
# test_literals(status="zz")


def test_dictionary(input_dict: dict[Literal["id"], Any]) -> dict[Literal["id"], Any]:
    return input_dict


bb = test_dictionary({"id": [1, 2, 3]})
bb2 = test_dictionary({"id": "yah"})

# ENUMS
from enum import Enum, auto


class Status(Enum):
    YES = auto()
    NO = auto()
    MAYBE = auto()


d = Status.YES


class Point(NamedTuple):
    x: int
    y: int


# Creating instances of the named tuple
p1 = Point(1, 2)
p2 = Point(x=3, y=4)


# Accessing fields using attribute names
print(p1.x, p1.y)  # Output: 1 2
print(p2.x, p2.y)  # Output: 3 4


# tuple of variable amount of
def test_tuple(elements: tuple[str, ...]) -> None:
    print(elements)


test_tuple(elements=("hi", "yes", "hello"))
test_tuple(elements=("hi", "hi2"))

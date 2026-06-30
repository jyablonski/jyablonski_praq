from typing import overload, TypeVar

T = TypeVar("T")  # A generic type variable


def swap(a: T, b: T) -> tuple[T, T]:
    return b, a


x, y = swap(1, 2)  # Works with integers
s1, s2 = swap("hello", "world")  # Works with strings


# mypy passes successfully because the type isnt changing
def invalid_mypy_swap_1(a: T, b: int) -> tuple[T, T]:
    return (a, b)


# mypy error on line 21 bc b1 is an int and we expect it to be T
def invalid_mypy_swap_2(a: T, b: int) -> tuple[T, T]:
    b1 = b * 2
    return (a, b1)


# COMPLEX EXAMPLE

# Define a constrained TypeVar
Y = TypeVar("Y", int, str, list[int])


@overload
def process(value: int) -> int: ...


@overload
def process(value: str) -> str: ...


@overload
def process(value: list[int]) -> list[int]: ...


def process(value: Y) -> Y:
    if isinstance(value, int):
        return value**2  # Square the number
    elif isinstance(value, str):
        return value[::-1]  # Reverse the string
    elif isinstance(value, list):
        return value[::-1]  # Reverse the list

    # In Python, bool is actually a subclass of int
    # bool is implicitly included in the constrained
    # `Y` types because we included int already
    elif isinstance(value, bool):
        return not value
    raise TypeError("Unsupported type")


# Test cases
print(process(4))  # Output: 16
print(process("hello"))  # Output: "olleh"
print(process([1, 2, 3]))  # Output: [3, 2, 1]
print(process([True]))  # Output: [3, 2, 1]


# these both return true
isinstance(True, int)
isinstance(False, int)

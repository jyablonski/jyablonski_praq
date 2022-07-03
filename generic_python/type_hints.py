from typing import Mapping, Optional, Union

# Example 1:


def test(x: Mapping[str, Mapping[str, int]]) -> Optional[str]:
    pass


{"person_1": {"money": 1000}, "person_2": {"money": 1000}}


# Example 2:
def test(x: Mapping[str, Mapping[str, Union[str, int]]]) -> Optional[str]:
    pass


{"person_1": {"job": "coder", "money": 1000,}}

# Example 3 - 3 parts:
# this specifies that new_bandwiths is a dict, but not the data types of the keys or values
def change_bandwidths(new_bandwidths: dict, user_id: int, user_name: str) -> bool:
    pass


# this goes 1 level deeper to define the data type of the keys and values of the new_bandwidths dict
def change_bandwidths(
    new_bandwidths: typing.Dict[str, str], user_id: int, user_name: str
) -> bool:
    pass


# Example 4: x is either going to be an integer or a string
def fn(x: typing.Optional[int, str]):
    pass


# Example 5 - the first 2 examples below do the same thing.  Optional lets you avoid having to write the extra None parameter.
import typing


def foo(bar: typing.Optional[str]):
    pass


def foo(bar: typing.Union[str, None]):
    pass


# python 3.9 and above - you dont need to import typing.
def foo(bar: str = None):
    pass


# Example 6
def foobar(dict1: Mapping[str, Union[str, int, str]]) -> Optional[bool]:
    print(dict1)
    if len(dict1) > 0:
        return True
    else:
        return None


dict1 = {"id": {"name": "jacob", "rank": 1, "fakekey": "fakevalue"}}

# Example 7 TypedDict
from typing import List, TypedDict, Dict


class SalesSummary(TypedDict):
    sales: int
    country: str
    product_codes: List[str]


def get_sales_summary() -> SalesSummary:
    """Return summary for yesterday’s sales."""
    return {
        "sales": 1_000,
        "country": "UK",
        "product_codes": ["SUYDT"],
    }


# Example 8
def count_words(text: str) -> Dict[str, int]:
    return {"key1": 1}


# vs


def count_words(text: str) -> dict:
    return {"key1": 1}

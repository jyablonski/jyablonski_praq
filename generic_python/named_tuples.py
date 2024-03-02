from __future__ import annotations

from collections import namedtuple
from dataclasses import dataclass
from typing import NamedTuple


class Prefix(NamedTuple):
    prefix_dir: str


c = Prefix(prefix_dir="hello")

c.prefix_dir

ProductNamedTuple = namedtuple("ProductNamedTuple", ["name", "price", "color"])
product_namedtuple = ProductNamedTuple(name="Chair", price=50, color="Red")
print(product_namedtuple)


@dataclass
class ProductDataclass:
    name: str
    price: float
    color: str


product_dataclass = ProductDataclass(name="Table", price=100, color="Blue")
print(product_dataclass)


class ProductClass:
    def __init__(self, name, price, color):
        self.name = name
        self.price = price
        self.color = color

    def __repr__(self):
        return f"ProductClass(name='{self.name}', price={self.price}, color='{self.color}')"


product_class = ProductClass(name="Lamp", price=30, color="Yellow")
print(product_class)
product_class

from __future__ import annotations

import enum
from typing import NamedTuple
from typing import Union

_Unset = enum.Enum("_Unset", "UNSET")
UNSET = _Unset.UNSET


class Var(NamedTuple):
    name: str
    default: str = ""


SubstitutionT = tuple[Union[str, Var], ...]
ValueT = Union[str, _Unset, SubstitutionT]
PatchesT = tuple[tuple[str, ValueT], ...]

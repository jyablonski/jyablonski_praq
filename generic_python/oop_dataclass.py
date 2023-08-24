from dataclasses import dataclass


@dataclass
class Animal:
    """
    A class to represent an Animal.

    ...

    Attributes
    ----------
    species : str
        first name of the person
    color : str
        family name of the person

    Methods
    -------
    _internal_method():
        Prints Something

    public_method():
        Prints Something Else

    combo_method():
        Executes Internal Method and Public Method

    test_static_method(x=""):
        Returns a passed in input value for `x`

    add_numbers_raw(x="", y=""):
        Returns the sum of x & y

    add_numbers(x="", y=""):
        Returns the sum of x & y
    """

    species: str
    color: str

    # you need self otherwise shit broke m8
    # you can call both this method and the
    def _internal_method(self):
        print(f"yea shoreman")

    def public_method(self):
        print(f"see dude look")

    def combo_method(self):
        self._internal_method()
        self.public_method()

    def test_static_method(self, x: int):
        print(f"Input of {x}")
        return x

    def add_numbers_raw(self, x: int, y: int):
        return x + y

    # with staticmethod you don't need `self`
    @staticmethod
    def add_numbers(x: int, y: int):
        return x + y


b = Animal(species="Reptile", color="black")

b._internal_method()
b.public_method()
b.combo_method()

b.add_numbers_raw(x=4, y=5)
b.add_numbers(x=4, y=5)

# Given four integers length, width, height, and mass, representing the dimensions and mass of a box, respectively, return a string representing the category of the box.

# The box is "Bulky" if:
# Any of the dimensions of the box is greater or equal to 10000.
# Or, the volume of the box is greater or equal to 1000000000.
# If the mass of the box is greater or equal to 100, it is "Heavy".
# If the box is both "Bulky" and "Heavy", then its category is "Both".
# If the box is neither "Bulky" nor "Heavy", then its category is "Neither".
# If the box is "Bulky" but not "Heavy", then its category is "Bulky".
# If the box is "Heavy" but not "Bulky", then its category is "Heavy".
# Note that the volume of the box is the product of its length, width and height.


# straight forward, just read the directions
# `any_over_104 = any(dim >= dim_limit for dim in dims)` is handy to handle the any dim over xyz logic
# and then it's just an else if loop to return the right string
def solution(length: int, width: int, height: int, mass: int) -> str:
    dims = [length, width, height]
    volume = length * width * height

    vol_limit = 1000000000
    dim_limit = 10000

    any_over_104 = any(dim >= dim_limit for dim in dims)

    if mass >= 100 and (volume >= vol_limit or any_over_104):
        return "Both"
    elif mass >= 100 and not (volume >= vol_limit or any_over_104):
        return "Heavy"
    elif mass < 100 and (volume >= vol_limit or any_over_104):
        return "Bulky"
    else:
        return "Neither"


length = 1000
width = 35
height = 700
mass = 300

solution(length=length, width=width, height=height, mass=mass)

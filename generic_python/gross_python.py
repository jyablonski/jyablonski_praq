from typing import Dict


# using this in actual code is honestly so fucking stupid so grats lmfao
x = False

if not x:
    print(f"x is {x}, hello world")
else:
    print(f"x is {x}, what ")

x = True

if not x:
    print(f"x is {x}, hello world")
else:
    print(f"x is {x}, what ")


x = ""
if not x:
    print('x is "", hello world')
else:
    print('x is "", what ')

x = "something"
if not x:
    print(f"x is {x}, hello world")
else:
    print(f"x is {x}, what ")

x = []
if not x:
    print(f"x is {x}, hello world")
else:
    print(f"x is {x}, what ")

x = [1, 2, 3]
if not x:
    print(f"x is {x}, hello world")
else:
    print(f"x is {x}, what ")

x = {}
if not x:
    print(f"x is {x}, hello world")
else:
    print(f"x is {x}, what ")

x = {"yeet": "baby"}
if not x:
    print(f"x is {x}, hello world")
else:
    print(f"x is {x}, what")


##
z = [True, True, True]

if any(z) == False:
    print("hello world")
else:
    print("wooowoah")

if all(z) == False:
    print("hello world")
else:
    print("wooowoah")

if all(z) == True:
    print("hello world")
else:
    print("wooowoah")


def test_ink(my_dictionary: Dict[int, int]):
    print(my_dictionary)
    pass


my_dict = {1: 4}
test_ink(my_dict)


# this is -generally- what you should use dict for; just a general dictionary.
def test_ink2(my_dictionary: dict):
    print(my_dictionary)
    pass


test_ink2(my_dict)

# doing this is rly fkn stupid
dict1 = {"test": {"hello": "world"}, "test2": {"try": {"in": "ception"}}}

dict1["test2"]["try"]

import collections
from collections import defaultdict

phonebook = {
    "bob": 7387,
    "alice": 3719,
    "jack": 7052,
}

squares = {x: x * x for x in range(6)}

phonebook["alice"]


keys = phonebook.keys()

for i in keys:
    print(i)

# ordered dictionary remembers the order in which items were inserted
d = collections.OrderedDict(one=1, two=2, three=3)

d


d["four"] = 4
d


d.keys()

# this removes the key `four`
d.popitem()

# defaultdict is a dictionary that calls a factory function to supply missing values
dd = defaultdict(list)

# Accessing a missing key creates it and
# initializes it using the default factory,
# i.e. list() in this example:
dd["dogs"].append("Rufus")
dd["dogs"].append("Kathrin")
dd["dogs"].append("Mr Sniffles")

dd["dogsfds"]

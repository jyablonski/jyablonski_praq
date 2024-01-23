# https://thepythoncorner.com/posts/2020-08-21-hash-tables-understanding-dictionaries/
# https://www.youtube.com/watch?v=0M_kIqhwbFo
# dictionaries - abstract data type
# they use hashing to xyz
# dictionaries can insert, delete, or search for specific key - value pairs
import sys

test1 = {"hello": "world"}
dict_size_bytes = sys.getsizeof(test1)


test1["hello"] = "jacobs_world"

# value is now jacobs_world
print(test1)
print(type(test1))

# checking for types
if isinstance(test1, dict):
    print("hello world")
else:
    print("oof")

# remove the hello key
test1.pop("hello")
print(test1)

# keys will not always be integers
test1[0] = 1
test1

# cant do this bc list cannot be hashed.
my_list = [1, 2, 3]
test1[my_list] = 5


my_int = "hello world"


hash(my_int)

print(id(test1))

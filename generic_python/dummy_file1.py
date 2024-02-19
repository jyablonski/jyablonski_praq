str_multiplication = "*" * 25
edges = "*" + (" " * 23) + "*"

print(
    f"""{str_multiplication}
{edges}
{edges}
{edges}
{edges}
{str_multiplication}
"""
)

my_list = [0, 1, 2, 3]

# doubles the list from len 4 to len 8
my_list * 2

my_list2 = [x * 2 for x in my_list]


join1 = [1, 2, 3]
join2 = [3, 4, 5]

# returns 3
matches = [x for x in join1 if x in join2]

# returns every element that isn't in both lists
not_matches = list(set(join1) ^ set(join2))


my_unique_values = set()
my_unique_values.add(1)
my_unique_values.add(2)

# this doesnt actually do anything anymore
my_unique_values.add(1)
my_unique_values.pop()


my_pairs = {"store1": "1234 los alisos boulevard"}

for key, value in my_pairs.items():
    print(f"key is {key} and value is {value}")


my_normal_list = [1, 2, 4, 3, 7, 10, 8, 9]

max_sub = my_normal_list[0]

for index, value in enumerate(my_normal_list):
    max_sub = max(max_sub, value)
    print(f"index is {index} and value is {value}, while max sub is {max_sub}")

str1 = "hello world"
print(str1[::-1])  # reverse it

for i, v in enumerate(str1):
    if i > 0:
        print(str1[::i])

# ordered and immutable.  duplicates allowed
jacobs_tuples = ("hello", "world", "world")

for value in jacobs_tuples:
    print(value)

# an actual tuple
thistuple = ("apple",)
print(type(thistuple))

# NOT a tuple, just a str
thistuple = "apple"
print(type(thistuple))


try:
    jacobs_tuples.append(1)
except BaseException as e:
    print(f"oof error {e}")
    raise e


try:
    my_pairs["hello"]
    my_pairs["store1"]
except KeyError as e:
    print("that didnt do anything")
except BaseException as e:
    raise e("oof")
finally:
    print("hello world")


def palindrome_check(input_str: str) -> bool:
    # return input_str == input_str[::-1]
    if input_str == input_str[::-1]:
        return True
    else:
        return False


palindrome_check("racecar")
palindrome_check("fake")

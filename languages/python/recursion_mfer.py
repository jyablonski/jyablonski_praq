def factorial(n: int) -> int:
    # Base case: if n is 0 or 1, return 1
    if n == 0 or n == 1:
        print("1 boob")
        return 1
    # Recursive case: n * factorial(n-1)
    else:
        print(f"{n} boobs")
        return n * factorial(n - 1)


number = factorial(8)


def add_1_until_n(n: int) -> int:
    int_sum = 1
    int_count = 1

    while int_count <= n:
        int_sum += int_count
        int_count += 1

    return int_sum


add_1_until_n(n=120)


def fact(x: int) -> int:
    # base case
    if x == 1:
        return 1
    else:
        return x * fact(x - 1)


fact(4)


def add_1(x: int) -> int:
    if x == 1:
        return 1
    else:
        return x + add_1(x - 1)


add_1(5)

# In the recursive call, the argument is one less than the current value of n, so each recursion moves closer to the base case.


def countdown(n: int):
    print(n)

    # base case
    if n == 0:
        return
    else:
        # the recursive call
        countdown(n - 1)


countdown(15)


# non recursive way of doing it
def countdown(n):
    while n >= 0:
        print(n)
        n -= 1


countdown(15)


def factorial(n: int):
    return 1 if n <= 1 else n * factorial(n - 1)


factorial(4)

names = [
    "Adam",
    [
        "Bob",
        [
            "Chet",
            "Cat",
        ],
        "Barb",
        "Bert",
    ],
    "Alex",
    ["Bea", "Bill"],
    "Ann",
]


def count_leaf_items(item_list):
    """Recursively counts and returns the
    number of leaf items in a (potentially
    nested) list.
    """
    count = 0
    for item in item_list:
        if isinstance(item, list):
            count += count_leaf_items(item)
        else:
            count += 1

    return count


count_leaf_items(item_list=names)


def is_palindrome(word):
    """Return True if word is a palindrome, False if not."""
    if len(word) <= 1:
        return True
    else:
        return word[0] == word[-1] and is_palindrome(word[1:-1])


is_palindrome("racecar")

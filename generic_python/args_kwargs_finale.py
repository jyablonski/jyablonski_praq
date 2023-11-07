# args
# args can be used to pas a variable amount of non key-value pair arguments to a function
# the asterisk is ued to denote any amount of positional arguments can be passed in,
# and they're collected as a tuple
def my_arg_function(arg1, *args):
    print("arg1:", arg1)
    print("args:", args)
    print(isinstance(args, tuple))


my_arg_function("apple", "banana", "cherry", "date")


# kwargs
# kwargs can be used to pass a variable amount of key-value pairs to a function
def my_kwarg_function(arg1, **kwargs):
    print("arg1:", arg1)
    print("kwargs:", kwargs)


my_kwarg_function("apple", fruit="banana", color="yellow", size="small")

fruits = {"fruit": "banana", "color": "yellow", "size": "small"}
my_kwarg_function("apple", kwargs=fruits)


# combining both args and kwargs
def combined_function(arg1, *args, **kwargs):
    print("arg1:", arg1)
    print("args:", args)
    print("kwargs:", kwargs)


combined_function("apple", "banana", "cherry", color="yellow", size="small")


# common use cases are when you want to create more flexible and generic code
# that can handle a different number of arguments

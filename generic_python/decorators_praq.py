def make_pretty(func):
    def inner():
        print("I got decorated")
        func()

    return inner


def ordinary():
    print("I am ordinary")


pretty = make_pretty(ordinary)
pretty()


@make_pretty  # ordinary() gets passed INTO the make_pretty() function and both are technically "ran"
def ordinary2():
    print("I am ordinarry")


ordinary2()

# ordinary2() is the same as pretty()
# the decorator make_pretty is called using ordinary2() AS its input variable.


@make_pretty  # ordinary() gets passed INTO the make_pretty() function and both are technically "ran"
def ordinary():
    print("I am ordinary")


ordinary()


def my_decorator(func):
    def wrapper():
        print("Something is happening before the function is called.")
        func()
        print("Something is happening after the function is called.")

    return wrapper


@my_decorator
def tester():
    print(f"hello world")


tester()

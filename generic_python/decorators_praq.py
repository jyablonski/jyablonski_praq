from functools import wraps
import time
from typing import Any, Callable

# functools.wraps is needed when using 2 or more decorators
# so i can properly access func.__name__.
# it updates the attributes of the inner wrapper function to match those
# of the input `func` Function


def time_function(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator function used to record the execution time of any
    function it's applied to.

    Args:
        func (Callable): Function to track the execution time on.

    Returns:
        Callable[..., Any]: The wrapped function that records
            the execution time.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
        except BaseException as e:
            total_func_time = round(time.time() - start_time, 3)
            print(f"{func.__name__} took {total_func_time} seconds")
            raise e

        total_func_time = round(time.time() - start_time, 3)
        print(f"{func.__name__} took {total_func_time} seconds")
        return result

    return wrapper


def write_errors_to_slack(func: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except BaseException as e:
            print(f"{func.__name__} Error occurred: {e}, running code to handle error.")
            # write_so_slack(xyz)
            # Code to handle error, for example, sending error to Slack
            # This code will always run even if there's an error
            raise e
        else:
            # Code to execute if no error occurred
            # This code will run only if no error occurred
            print("it worked & this only prints during no errors")
            pass
        finally:
            # Code to execute regardless of whether an error occurred or not
            # This code will always run, even if there's an error
            print("Code in finally block always runs.")
        return result

    return wrapper


# @write_errors_to_slack
@time_function
def test(s: str) -> str:
    if s not in ("hello world"):
        raise ValueError("you fucked up buddy")

    return s


test("hello world")
test("fail")


## old gahbage


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

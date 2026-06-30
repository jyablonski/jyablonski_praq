class BadError(Exception):
    pass


def external_log(error):
    print("Sending Log to some external service ...")
    pass


def process_data():
    raise BadError("bad error occurred")


def get_thing(a: str) -> int:
    if not isinstance(a, str):
        raise ValueError("a should be a string")

    try:
        process_data()

    except Exception as e:
        external_log(e)
        raise

    finally:
        print("hit an error but im still running xd")
        # if you return here, then the function would never error out
        # if it hit an error

    return 1


get_thing("sad")


# with raise e
# Traceback (most recent call last):
#   File "/home/jacob/Documents/jyablonski_praq/generic_python/advanced_exceptions_yo.py", line 27, in <module>
#     get_thing("sad")
#   File "/home/jacob/Documents/jyablonski_praq/generic_python/advanced_exceptions_yo.py", line 20, in get_thing
#     raise e
#   File "/home/jacob/Documents/jyablonski_praq/generic_python/advanced_exceptions_yo.py", line 16, in get_thing
#     process_data()
#   File "/home/jacob/Documents/jyablonski_praq/generic_python/advanced_exceptions_yo.py", line 9, in process_data
#     raise BadError("bad error occurred")
# BadError: bad error occurred


# with just raise
# Traceback (most recent call last):
#   File "/home/jacob/Documents/jyablonski_praq/generic_python/advanced_exceptions_yo.py", line 27, in <module>
#     get_thing("sad")
#   File "/home/jacob/Documents/jyablonski_praq/generic_python/advanced_exceptions_yo.py", line 16, in get_thing
#     process_data()
#   File "/home/jacob/Documents/jyablonski_praq/generic_python/advanced_exceptions_yo.py", line 9, in process_data
#     raise BadError("bad error occurred")
# BadError: bad error occurred

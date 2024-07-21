def simple_generator():
    print("First Value")
    yield 1

    print("Second Value")
    yield 2

    print("Third Value")
    yield 3


gen = simple_generator()

# gen object
print(gen)

# `generator` class
print(type(gen))

# executes the print statements and the value in the gen
for value in gen:
    print(value)


def infinite_sequence():
    num = 0
    while True:
        yield num
        num += 1


gen = infinite_sequence()

for i in range(5):
    print(next(gen))

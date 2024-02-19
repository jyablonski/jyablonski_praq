# instantiate a list object
# loads everything into memory at once
list_instance = [1, 2, 3, 4]

# convert the list to an iterator
iterator = iter(list_instance)

# return items one at a time
print(next(iterator))
print(next(iterator))
print(next(iterator))
print(next(iterator))


def my_generator(data):
    for item in data:
        yield item


# Using the generator
# only puts objects into memory when you're accessing them, then removes them as you use them.
gen = my_generator([1, 2, 3, 4, 5])
for item in gen:
    print(item)

passed_items = {"hello": "world", "test": "value1"}

# this returns true
"hello" in passed_items

# this returns false
"helloworld" in passed_items


my_list = [1, 2, 3, ""]

# this returns true
3 in my_list

# this returns true
"" in my_list


# empty str
my_value = ""

# this will print 5
print(5) if not my_value else print(3)

# this will print 5
if not my_value:
    print(5)
else:
    print(3)


# boolean
my_value = False

# this will print 5
print(5) if not my_value else print(3)

# this will print 5
if not my_value:
    print(5)
else:
    print(3)

# None
my_value = None

# this will print 5
print(5) if not my_value else print(3)

# this will print 5
if not my_value:
    print(5)
else:
    print(3)

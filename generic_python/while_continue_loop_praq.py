a = 1

while a < 10:
    print(a)
    if a == 4:
        print(f"a is {a}, writing to xyz ...")
    if a == 8:
        print(f"Oooh shit dude")
        break
    a += 1


b = 10
while b > 0:
    print(b)
    b -= 1
    if b == 5:
        print(f"b is {b}")
        continue

    if b == 0:
        print(f"b is {b}, exiting ...")
        # don't need break or anything here bc it's done


test_list = [0, 1, 5, 10, 30]

# print values of items in list
for i in test_list:
    print(i)

# print index of items in list
for i in range(len(test_list)):
    print(i)


# old school way with range len
for index in range(len(test_list)):
    print(f"index {index} has value {test_list[index]}")

# same thing: zip allows you to iterate through both at the same time.
for index, value in zip(range(len(test_list)), test_list):
    print(f"index {index} has value {value}")


# enumerate is by far the best way to do this stuff
for index, value in enumerate(test_list):
    print(f"index {index} has value {value}")

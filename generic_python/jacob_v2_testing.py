# unsorted
my_array = [4, 3, 144, 1, 7, 5]

sorted_array = [1, 5, 8, 11, 15, 17, 22, 28]

for i in my_array:
    print(i)

for index, value in enumerate(my_array):
    print(f"{index}, {value}")

my_array = sorted(my_array)

first_index = my_array[0]
last_index = my_array[-1]

# remove last element from my_array in-place
my_array.pop()

# remove last element from my_array in-place & keep it
removed_value = my_array.pop()


dict = {}
my_array = sorted(my_array)

for index, value in enumerate(my_array):
    dict[index] = value

# pop by passing in the index in the dictionary
dict.pop(5)
dict.pop(0)

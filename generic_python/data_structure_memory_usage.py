import sys

key_name = "key1"

my_dict = {key_name: 123}

# Measure memory usage of dictionary keys and values
# this only counts the memory used for the dictionary, not all of the contents
dict_size_bytes = sys.getsizeof(my_dict)

# to find the total for a dictionary, sum the dictionary memory + the content memory
total_size_bytes = sys.getsizeof(my_dict)
for key, value in my_dict.items():
    total_size_bytes += sys.getsizeof(key)
    total_size_bytes += sys.getsizeof(value)

print(f"Total memory usage of dictionary and its elements: {total_size_bytes} bytes")


s = {"key1": "value1"}

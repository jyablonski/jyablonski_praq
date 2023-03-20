import datetime
import json
import os

my_list = []

my_list2 = [1, 2, 3, 4, 5]

for i in my_list2:
    my_list.append(i)

print(f"len of my_list is {my_list}")

my_list = []
my_list = [i for i in my_list2]

str_list = ["strip_this", "strip_this2", "strip_this3"]

my_list = [i.split("_")[1] for i in str_list]

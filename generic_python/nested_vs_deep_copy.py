import copy

# shallow copy - the default
list1 = [1, 2, 3]
tuple1 = (100, 250, 500)
combo_list = [list1, tuple1]

combo_list_copy = combo_list

print(f"before: \n{combo_list}\n{combo_list_copy}")

combo_list[0][1] = 20

print(f"after: \n{combo_list}\n{combo_list_copy}")


## deep copy - hardcoded
list1 = [1, 2, 3]
tuple1 = (100, 250, 500)
combo_list = [list1, tuple1]

combo_list_copy = copy.deepcopy(combo_list)

print(f"before: \n{combo_list}\n{combo_list_copy}")

combo_list[0][1] = 20

print(f"after: \n{combo_list}\n{combo_list_copy}")

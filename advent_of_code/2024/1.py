from typing import Counter


def solution_lc(list1: list[int], list2: list[int]) -> int:
    list1 = sorted(list1)
    list2 = sorted(list2)
    difference_sum = 0

    for list1_val, list2_val in zip(list1, list2):
        print(f"{list1_val} and {list2_val}")
        difference_sum += abs(list1_val - list2_val)

    return difference_sum


list1 = [3, 4, 2, 1, 3, 3]
list2 = [4, 3, 5, 3, 9, 3]

solution_lc(list1=list1, list2=list2)


def solution() -> int:
    list1 = []
    list2 = []
    difference_sum = 0

    with open("advent_of_code/2024/day_1_input.txt", "r") as file:
        for line in file:
            num1, num2 = map(int, line.split())
            list1.append(num1)
            list2.append(num2)

    list1 = sorted(list1)
    list2 = sorted(list2)

    for list1_val, list2_val in zip(list1, list2):
        print(f"{list1_val} and {list2_val}")
        difference_sum += abs(list1_val - list2_val)

    return difference_sum


solution()


def solution_part2() -> int:
    list1 = []
    list2 = []
    similarity_score = 0

    with open("advent_of_code/2024/day_1_input.txt", "r") as file:
        for line in file:
            num1, num2 = map(int, line.split())
            list1.append(num1)
            list2.append(num2)

    list1 = sorted(list1)
    list2_counter = Counter(list2)

    for val in list1:
        if val in list2_counter:
            similarity_score += val * list2_counter[val]

    return similarity_score


solution_part2()

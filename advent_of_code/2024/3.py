import re


def solution():
    # regex to find "mul(number, number)"
    pattern = r"mul\(\d+,\s*\d+\)"
    all_matches = []
    with open("advent_of_code/2024/day_3_input.txt", "r") as file:
        for line in file:
            matches = re.findall(pattern=pattern, string=line)
            all_matches.extend(matches)

    mul_sum = 0

    for pair in all_matches:
        int_pair = pair.replace("mul(", "").replace(")", "").split(",")
        mul_sum += int(int_pair[0]) * int(int_pair[1])

    return mul_sum


solution()

str1 = "mul(982,733)"
str2 = str1.replace("mul(", "").replace(")", "")
str3 = str2.replace("mul(", "").replace(")", "").split(",")


def solution_part2():
    pass

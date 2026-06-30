# https://adventofcode.com/2023/day/1
import re


def count_lines(file_input: str) -> int:
    # Matches one or more digits (\d+) surrounded by word boundaries (\b)
    pattern = r"\d"
    line_numbers = []
    line_pair_sum = 0

    with open(file_input, "r") as file:
        lines = (line for line in file)

        for line in lines:
            numbers = re.findall(pattern, line)

            if len(numbers) == 1:
                numbers = numbers * 2

            if len(numbers) > 2:
                numbers = [numbers[0], numbers[-1]]

            line_numbers.append(numbers)

    for pair in line_numbers:
        sum_pair = int("".join(pair))
        line_pair_sum += sum_pair

    return line_pair_sum


df = count_lines(file_input="day_1_input.txt")


# part 2
# do this dumbass shit because some strings were like `466vczmxdndg1nb72eightwos`
def count_lines_part2(file_input: str):
    replacements = {
        "one": "one1one",
        "two": "two2two",
        "three": "three3three",
        "four": "four4four",
        "five": "five5five",
        "six": "six6six",
        "seven": "seven7seven",
        "eight": "eight8eight",
        "nine": "nine9nine",
    }
    digit_pattern = r"\d"
    line_numbers = []
    line_pair_sum = 0

    with open(file_input, "r") as file:
        lines = (line for line in file)

        for line in lines:
            og_line = line
            for word, number in replacements.items():
                if word in line:
                    line = line.replace(word, replacements[word])

            numbers = re.findall(digit_pattern, line)

            if len(numbers) == 1:
                numbers = numbers * 2

            if len(numbers) > 2:
                numbers = [numbers[0], numbers[-1]]

            print(f"{numbers} - {line} - {og_line}")
            line_numbers.append(numbers)

    for pair in line_numbers:
        sum_pair = int("".join(pair))
        print(sum_pair)
        line_pair_sum += sum_pair

    return line_pair_sum


df = count_lines_part2(file_input="day_1_input.txt")

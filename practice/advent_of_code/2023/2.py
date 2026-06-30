# bag of colored cubes: red, green, or blue
# which games are possible if bag only contains if the bag contained only 12 red cubes, 13 green cubes, and 14 blue cubes?

import re


def sum_game_ids(file_input: str) -> int:
    digit_pattern = r"\d+"
    red_max = 12
    green_max = 13
    blue_max = 14
    game_id_sum = 0

    with open(file_input, "r") as file:
        lines = (line for line in file)

        for game in lines:
            line_object = game.split(":")
            line_object = [game.strip() for game in line_object]

            game_id = int(line_object[0].split(" ")[1])
            line_object.pop(0)

            iterations = line_object[0].split(";")
            iterations = [iteration.strip() for iteration in iterations]

            for marbles in iterations:
                marbles_list = marbles.split(", ")

                for marble_count in marbles_list:
                    red_value = 0
                    green_value = 0
                    blue_value = 0

                    if "red" in marble_count:
                        red_value = int(re.findall(digit_pattern, marble_count)[0])
                    elif "green" in marble_count:
                        green_value = int(re.findall(digit_pattern, marble_count)[0])
                    elif "blue" in marble_count:
                        blue_value = int(re.findall(digit_pattern, marble_count)[0])

                    if (
                        red_value > red_max
                        or green_value > green_max
                        or blue_value > blue_max
                    ):
                        game_id = 0
                        break
                    else:
                        pass

            print(
                f"adding {game_id} to {game_id_sum} for new total {game_id_sum + game_id}"
            )
            game_id_sum += game_id

    return game_id_sum


sum_game_ids(file_input="day_2_input.txt")


# part two
def sum_game_ids_part_two(file_input: str) -> int:
    digit_pattern = r"\d+"
    cube_power_sum = 0

    with open(file_input, "r") as file:
        lines = (line for line in file)

        for game in lines:
            red_game_max = 0
            green_game_max = 0
            blue_game_max = 0

            line_object = game.split(":")
            line_object = [game.strip() for game in line_object]

            game_id = int(line_object[0].split(" ")[1])
            line_object.pop(0)

            iterations = line_object[0].split(";")
            iterations = [iteration.strip() for iteration in iterations]

            for marbles in iterations:
                marbles_list = marbles.split(", ")

                for marble_count in marbles_list:
                    red_value = 0
                    green_value = 0
                    blue_value = 0

                    if "red" in marble_count:
                        red_value = int(re.findall(digit_pattern, marble_count)[0])
                        red_game_max = max(red_value, red_game_max)
                    elif "green" in marble_count:
                        green_value = int(re.findall(digit_pattern, marble_count)[0])
                        green_game_max = max(green_value, green_game_max)
                    elif "blue" in marble_count:
                        blue_value = int(re.findall(digit_pattern, marble_count)[0])
                        blue_game_max = max(blue_value, blue_game_max)

            print(
                f"{game} -- red max is {red_game_max} \n green max is {green_game_max} \n blue max is {blue_game_max}"
            )
            game_cube_power_sum = red_game_max * green_game_max * blue_game_max
            cube_power_sum += game_cube_power_sum

    return cube_power_sum


sum_game_ids_part_two(file_input="day_2_input.txt")

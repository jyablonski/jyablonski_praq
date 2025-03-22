# Given an encoded string, return its decoded string.

# The encoding rule is: k[encoded_string], where the encoded_string inside the
# square brackets is being repeated exactly k times. Note that k is guaranteed
# to be a positive integer.

# You may assume that the input string is always valid; there are no extra white
# spaces, square brackets are well-formed, etc. Furthermore, you may assume that
# the original data does not contain any digits and that digits are only for
# those repeat numbers, k. For example, there will not be input like 3a or 2[4].

# The test cases are generated so that the length of the output will never exceed
# 105.


def solution(s: str) -> str:
    # use a stack and tuples of current_strs and nums to kepe track of things
    stack = []
    current_num = 0
    current_str = ""

    # 4 possible scenarios: char is a digit, char is 1 of "[" "]", or char is a char
    for char in s:
        if char.isdigit():
            # this is some weird math to handle multi digit numbers like 12
            current_num = current_num * 10 + int(char)

        elif char == "[":
            # if we start a new sublist, push our current crap onto the stack
            stack.append((current_str, current_num))
            current_str = ""
            current_num = 0

        elif char == "]":
            # if we find the end of a sublist, pop the latest tuple off the stack
            last_str, num = stack.pop()

            # use that to add onto the current_str
            current_str = last_str + num * current_str

        else:
            current_str += char

    return current_str


s1 = "3[a]2[bc]"
s2 = "3[a2[c]]"
s3 = "12[ab]"

solution(s=s1)
solution(s=s2)
solution(s=s3)


# first solution taht i didnt get quite right
def solution(s: str) -> str:
    sublist_count = 0
    current_multiplier_list = [1]
    output = ""
    sublist_chars = []

    for char in s:
        print(f"on char {char}")
        if char.isdigit():
            current_multiplier_list.append(int(char))

        if sublist_count and not char.isdigit() and char not in ("[", "]"):
            print(f"Adding {char} to sublist chars {sublist_chars}")
            sublist_chars.append(char)

        if char == "[":
            sublist_count += 1

        if char == "]":
            print(f"Found a break, sublist count is {sublist_count}")
            current_multiplier = current_multiplier_list.pop()
            sublist_count -= 1
            print(f"Adding {current_multiplier} * {sublist_chars} to output")
            output += current_multiplier * sublist_chars
            print(f"Output is now {output}, resetting {sublist_chars} to ''")
            sublist_chars = ""

    return output

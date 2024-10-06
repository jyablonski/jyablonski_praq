# have to be able to check the current value you are on and the following value
# also need a running total int to keep track of the value we want to return
def solution(s: str) -> int:
    # initialize some starter variables. dictionary for the mapping
    mapping = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    int_sum = 0
    str_len = len(s)

    # trick here is to just use this simple loop and use `next_index` to clean it up
    # the next index ensures we dont
    for current_index in range(str_len):
        next_index = current_index + 1

        # this is the check to make sure we dont go out of bounds
        if next_index < str_len and mapping[s[current_index]] < mapping[s[next_index]]:
            print(f"subtracting {mapping[s[current_index]]} from {int_sum}")
            int_sum -= mapping[s[current_index]]

        else:
            print(f"adding {mapping[s[current_index]]} to {int_sum}")
            int_sum += mapping[s[current_index]]

    return int_sum


solution("LIV")
solution("XII")
solution("XIV")
solution("XXVII")

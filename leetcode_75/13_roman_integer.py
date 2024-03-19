# have to be able to check the current value you are on and the following value
# also need a running total int to keep track of the value we want to return
def solution(s: str) -> int:
    mapping = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    int_sum = 0
    str_len = len(s)

    for i in range(str_len):
        if (
            i + 1 < str_len  # this is the check to make sure
            and mapping[s[i]] < mapping[s[i + 1]]
        ):
            print(f"subtracting {mapping[s[i]]} from {int_sum}")
            int_sum -= mapping[s[i]]
        else:
            print(f"adding {mapping[s[i]]} to {int_sum}")
            int_sum += mapping[s[i]]

    return int_sum


solution("LIV")
solution("XII")
solution("XIV")
solution("XXVII")

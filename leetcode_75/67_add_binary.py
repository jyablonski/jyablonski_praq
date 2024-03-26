# Given two binary strings a and b, return their sum as a binary string.


# use int(x, 2) to convert to binary notation
# bianry numbers will start with 0b, so we want to strip that and just return
# the sum as a string
def solution(a: str, b: str) -> str:
    str_sum = int(a, 2) + int(b, 2)

    return str(bin(str_sum)[2:])


a = "11"
b = "1"

solution(a=a, b=b)

# it starts with `0b` and then continues with its number
bin(42)

bin(4)

# given a string, find length of the longest contiguous substring without
# any repeating characters

str1 = "abcbcbsadfadfadfsadagfdhgyrtjredb"


def solution(input_str: str) -> int:
    # set because we're working with duplicates
    char_set = set()
    l = 0
    result = 0

    for r in range(len(input_str)):
        print(r)

        # if there's a duplicate
        # and there can be multiple, so you cant use an if statement
        while input_str[r] in char_set:
            print(f"{input_str[r]} is in {char_set}")
            char_set.remove(input_str[l])
            l += 1
        char_set.add(input_str[r])
        print(f"result is {result}")
        result = max(result, r - l + 1)

    return result


solution(str1)

str1 = "abcbcbsadfadfadfsadagfdhgyrtjredb"
str2 = "abcyfew"


def s(str1):
    char_set = set()
    l = 0
    result = 0

    for r in range(len(str1)):
        while str1[r] in char_set:
            char_set.remove(str1[l])
            l += 1

        char_set.add(str1[r])
        result = max(result, r - l + 1)

    return result


s(str1)

# Write a function to find the longest common prefix string amongst an array of strings.
# If there is no common prefix, return an empty string "".


# trick here is to use the first string in the list of strs as a base
# because the common prefix must be in all 3
# then loop through all strings in the input list of strings
# then if we hit the edge cases we exit out
#   1) if the current index is out of bounds for the current string
#   2) if the current char in the string we're on is not equal to the same element in the first string
# If all strings have the same character at the current index, add it to the result
def solution(strs: list[str]) -> str:
    res = ""

    for i in range(len(strs[0])):
        for string in strs:
            if i == len(string) or string[i] != strs[0][i]:
                return res

        res += strs[0][i]

    return res


strs1 = ["flower", "flow", "flight"]
strs2 = ["dog", "racecar", "car"]
solution(strs1)
solution(strs2)

for i in range(3):
    print(i)

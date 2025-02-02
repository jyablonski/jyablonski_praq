# The string "PAYPALISHIRING" is written in a zigzag pattern on a given number
# of rows like this: (you may want to display this pattern in a fixed font for
# better legibility)

# P   A   H   N
# A P L S I I G
# Y   I   R
# And then read line by line: "PAHNAPLSIIGYIR"

# Write the code that will take a string and make this conversion given a
# number of rows:

# string convert(string s, int numRows);


# time complexity of O(n * numRows)
# space complexity (numRows + n)
def solution(s: str, numRows: int) -> str:
    # return string as is if we have numRows = 1
    if numRows == 1:
        return s

    # initialize a list of lists, 1 for every row
    matrix = [[] for _ in range(numRows)]
    current_index = 0

    # we'll decide which list to append the current char on
    # based on this direction, which will be 1 (go down) or -1 (go up)
    direction = 1

    for char in s:
        matrix[current_index].append(char)

        # this wont do anytihng on first iteration, but imagine
        # we're going up & down over a long string of chars
        # we have to set it to 1 so it can iterate back down again
        if current_index == 0:
            direction = 1

        # if we reach the last list in the matrix, we have to iterate
        # back up now. so set direction to the opposite value
        elif current_index == numRows - 1:
            direction = -1

        current_index += direction

    # add the list of strings together
    output = ""
    for i in range(numRows):
        output += "".join(matrix[i])

    return output


s1 = "PAYPALISHIRING"
numRows1 = 3

s2 = "PAYPALISHIRING"
numRows2 = 4

solution(s=s1, numRows=numRows1)
solution(s=s2, numRows=numRows2)

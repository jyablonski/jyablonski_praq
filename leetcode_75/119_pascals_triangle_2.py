# Given an integer rowIndex, return the rowIndexth (0-indexed) row of the Pascal's triangle.
# In Pascal's triangle, each number is the sum of the two numbers directly above it as shown:


# first part of pascal's triangle starts with [1]
# then have to create a loop and fill in the rest of pascal's triangle
# with that next_row bits and initialize the values to 0s
# then we start a second loop to start filling in values
# we set both j and j + 1 because each value of the triangle has 2 children
def solution(row_index: int) -> list[int]:
    res = [1]

    for i in range(row_index):
        next_row = [0] * (len(res) + 1)
        for j in range(len(res)):
            next_row[j] += res[j]
            next_row[j + 1] += res[j]

        res = next_row

    return res


row_index = 3
solution(row_index)

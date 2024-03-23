# Given an integer rowIndex, return the rowIndexth (0-indexed) row of the Pascal's triangle.
# In Pascal's triangle, each number is the sum of the two numbers directly above it as shown:


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

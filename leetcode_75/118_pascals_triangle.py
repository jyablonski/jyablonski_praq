# Given an integer numRows, return the first numRows of Pascal's triangle.

# In Pascal's triangle, each number is the sum of the two numbers directly above it as shown:


def solution(rows: int) -> list[list[int]]:
    res = [1]
    full_output = [[1]]

    for i in range(rows - 1):
        next_row = [0] * (len(res) + 1)
        for j in range(len(res)):
            next_row[j] += res[j]
            next_row[j + 1] += res[j]

        res = next_row
        full_output.append(next_row)

    return full_output


rows = 5
solution(rows)

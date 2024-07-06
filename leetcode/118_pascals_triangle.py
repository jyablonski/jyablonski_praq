# Given an integer numRows, return the first numRows of Pascal's triangle.

# In Pascal's triangle, each number is the sum of the two numbers directly above it as shown:


def solution(rows: int) -> list[list[int]]:
    # This initializes the first row of Pascal's Triangle with a single element 1.
    res = [1]

    # This initializes the result list full_output with the first row of Pascal's Triangle.
    full_output = [[1]]

    # run through rows - 1 because that first row is already initialized
    for _ in range(rows - 1):
        # this creates a new row initialized with 0s with 1 more value than
        # the current row `res` because each row in pascal's triangle has 1 more
        # element than the previous row
        next_row = [0] * (len(res) + 1)

        for j in range(len(res)):
            # This ensures that each element in the new row is the sum of two elements
            # from the previous row, maintaining the property of Pascal's Triangle.
            next_row[j] += res[j]
            next_row[j + 1] += res[j]
            print(next_row)

        res = next_row
        full_output.append(next_row)
        # print(f"full output is now {full_output} \n")

    return full_output


rows = 5
solution(rows)


res = [1]

full_res = [[1]]

for _ in range(rows - 1):
    next_row = [0] * (len(res) + 1)

    for j in range(len(res)):
        next_row[j] += res[j]
        next_row[j + 1] += res[j]

    res = next_row
    full_res.append(next_row)

return full_res

# Anti-theft security devices are activated inside a bank. You are given a 0-indexed binary string
# array bank representing the floor plan of the bank, which is an m x n 2D matrix. bank[i] represents
# the ith row, consisting of '0's and '1's. '0' means the cell is empty, while'1' means the cell
# has a security device.

# There is one laser beam between any two security devices if both conditions are met:

# The two devices are located on two different rows: r1 and r2, where r1 < r2.
# For each row i where r1 < i < r2, there are no security devices in the ith row.
# Laser beams are independent, i.e., one beam does not interfere nor join with another.

# Return the total number of laser beams in the bank.

# time complexity o(n * m) bc we have to iterate through all rows / columns in the input
# pretty basic solution, you just count the number of 1s for each entry in the list,
# and then keep track of a prev value.

# if the current row has 1s in it, then we multiply that 1s count by prev and then
# update prev so it's ready for the next row with 1s in it.
def solution(bank: list[str]) -> int:
    res = 0
    prev = 0

    for row in bank:
        ones = row.count("1")
        if ones != 0:
            res += ones * prev
            prev = ones

    return res


bank1 = ["011001", "000000", "010100", "001000"]
bank2 = ["000", "111", "000"]

solution(bank=bank1)
solution(bank=bank2)

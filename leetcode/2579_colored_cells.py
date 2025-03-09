# There exists an infinitely large two-dimensional grid of uncolored unit cells.\
# You are given a positive integer n, indicating that you must do the following routine for n minutes:

# At the first minute, color any arbitrary unit cell blue.
# Every minute thereafter, color blue every uncolored cell that touches a blue cell.
# Below is a pictorial representation of the state of the grid after minutes 1, 2, and 3.

# at n = 1, output is 1
# at n = 2, output is 5
# at n = 3, output is 13


# solution just computes the sum of squares for 2 consecutive integers
def solution(n: int) -> int:
    return (n**2) + ((n - 1) ** 2)


n1 = 1
n2 = 4

solution(n=n1)
solution(n=n2)

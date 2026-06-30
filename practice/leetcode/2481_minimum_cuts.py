# A valid cut in a circle can be:

# A cut that is represented by a straight line that touches two points on the edge of the circle and passes through its center, or
# A cut that is represented by a straight line that touches one point on the edge of the circle and its center.
# Some valid and invalid cuts are shown in the figures below.


def solution(n: int) -> int:
    # base case
    if n == 1:
        return 0

    # if it's even then we can make n cuts to produce n * 2 pieces
    elif n % 2 == 0:
        return n // 2

    # if it's odd then you're fked
    else:
        return n


n1 = 4
n2 = 3

solution(n=n1)
solution(n=n2)
solution(n=25)

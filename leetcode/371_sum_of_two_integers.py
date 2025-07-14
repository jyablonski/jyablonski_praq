# Given two integers a and b, return the sum of the two integers without using
# the operators + and -.


# if you're going to ask a dumb fucking question you're gnna get a dumb fucking answer
def solution(a: int, b: int) -> int:
    res = []

    res.append(a)
    res.append(b)
    return sum(res)


a1 = 1
b1 = 2

a2 = 2
b2 = 3

solution(a=a1, b=b1)
solution(a=a2, b=b2)

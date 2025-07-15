# Given a positive integer n, write a function that returns the number of set bits in its binary representation (also known as the Hamming weight).


def solution(n: int) -> int:
    # bin(n) turns an int into its binary number
    # bin(5) -> '0b101'
    return bin(n).count("1")


n1 = 11
n2 = 128
n3 = 2147483645

solution(n=n1)
solution(n=n2)
solution(n=n3)

# reverse bits of a given 32 bit unsigned integer


def reverse_bits(n: int):
    res = 0

    for i in range(32):
        bit = (n >> i) & 1
        res = res | (bit << (31 - i))
    return res


n = 100
solution = reverse_bits(n=n)

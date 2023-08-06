import dis


def f():
    x = [i * 2 for i in range(5)]
    return x


f()

dis.dis(f)

def fibonacci(n: int) -> int:
    if n < 0:
        raise ValueError(f"Please enter a non-negative Integer mfer")

    elif n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        a = 0
        b = 1

        for _ in range(2, n + 1):
            c = a + b
            a = b
            b = c
        return b


fibonacci(11)

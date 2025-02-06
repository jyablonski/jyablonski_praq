from itertools import cycle

height = 12

for i in range(0, 12):
    print(f" " * (height - i), "#" * i)

valid_chars = ["#", "$"]
char_cycle = cycle(valid_chars)

for i in range(1, 26):
    next_char = cycle(valid_chars)
    expr = i * next_char if i % 2 == 0 else i * next_char

    print(expr)

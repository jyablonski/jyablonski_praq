import random


def count_characters(s: str, c: str) -> int:
    return s.count(c)


def main():
    if random.random() < 0.5:
        return count_characters("Hello world", "o")
    else:
        return count_characters("Hello world", 23)


main()

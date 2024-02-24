str1 = "hey this is my string it's pretty cool it has thingsz"
words = str1.split(" ")


def sentence_parser(string: str) -> None:
    words = []
    current_chars = []
    for i in string:
        if i == " ":
            words.append(current_chars)
            current_chars = []
        else:
            current_chars.append(i)

    for word in words:
        print(str(word))
    return words


bb = sentence_parser(str1)


def how_many_unique_chars(string: str) -> int:
    unique_chars = set()

    for char in string:
        unique_chars.add(char)

    return len(unique_chars)


def how_many_unique_chars_v2(string: str) -> int:
    return len(set(string))


def how_many_vowels_chars(string: str) -> int:
    unique_chars = ("a", "e", "i", "o", "u")
    unique_vowels = 0

    for char in string:
        if char in unique_chars:
            unique_vowels += 1

    return len(unique_chars)


how_many_vowels_chars(str1)

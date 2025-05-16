# Given a string containing digits from 2-9 inclusive, return all possible letter combinations that the number could represent. Return the answer in any order.

# A mapping of digits to letters (just like on the telephone buttons) is given below. Note that 1 does not map to any letters.

from itertools import product


def solution(digits: str) -> list[str]:
    mapping = {
        "2": ["a", "b", "c"],
        "3": ["d", "e", "f"],
        "4": ["g", "h", "i"],
        "5": ["j", "k", "l"],
        "6": ["m", "n", "o"],
        "7": ["p", "q", "r", "s"],
        "8": ["t", "u", "v"],
        "9": ["w", "x", "y", "z"],
    }

    # create a list
    possible_chars = [mapping[digit] for digit in digits]

    if not possible_chars:
        return []

    # `*` unpacks a list (or any iterable) so that each of its elements is passed
    # as a separate positional argument to the function.
    combos = product(*possible_chars)
    return ["".join(combo) for combo in combos]


digits1 = "23"
digits2 = ""
digits3 = "2"

solution(digits=digits1)
solution(digits=digits2)
solution(digits=digits3)


# non itertools backtracking solution
def solution(digits: str) -> list[str]:
    mapping = {
        "2": ["a", "b", "c"],
        "3": ["d", "e", "f"],
        "4": ["g", "h", "i"],
        "5": ["j", "k", "l"],
        "6": ["m", "n", "o"],
        "7": ["p", "q", "r", "s"],
        "8": ["t", "u", "v"],
        "9": ["w", "x", "y", "z"],
    }

    def backtrack(index: int, path: str):
        if index == len(digits):
            combinations.append(path)
            return
        for letter in mapping[digits[index]]:
            backtrack(index + 1, path + letter)

    combinations = []
    backtrack(0, "")
    return combinations

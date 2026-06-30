# problems:
# 1. return the total # of repeating characters in a row
# 2. return the character that has the highest number of repeating characters in a row
# 3. return how many vowels that occur in the string
# 4. return how many unique vowels occur in the string

str1 = "adsgfdsagdsfgettttbddsahhgggggdoiu"
str2 = "helloworldiii"


def problem_1(s: str) -> int:
    l = 0
    current_sub = 1
    max_sub = 0

    for i in range(len(s) - 1):
        if s[l] == s[i + 1]:
            current_sub += 1
            max_sub = max(current_sub, max_sub)
        else:
            current_sub = 1
            l = i + 1

    return max_sub


problem_1(s=str1)


def problem_2(s: str) -> int:
    chars = {}
    l = 0
    current_sub = 1

    for i in range(len(s) - 1):
        if s[l] == s[i + 1]:
            current_sub += 1
        else:
            if current_sub > chars.get(s[l], 0):
                chars[s[l]] = current_sub

            current_sub = 1
            l = i + 1

    return max(chars, key=chars.get)


problem_2(s=str1)


def problem_3(s: str) -> int:
    vowels = set("aeiou")
    s = s.lower()
    vowel_count = 0

    for char in s:
        if char in vowels:
            vowel_count += 1

    return vowel_count


problem_3(s=str1)


def problem_4(s: str) -> str:
    vowels = set("aeiou")
    s = s.lower()
    unique_vowels = set()

    for char in s:
        if char in vowels:
            unique_vowels.add(char)

    return len(unique_vowels)


problem_4(s=str2)

# Given two strings ransomNote and magazine, return true if ransomNote
# can be constructed by using the letters from magazine and false otherwise.

# Each letter in magazine can only be used once in ransomNote.
from collections import Counter


# this solution works, but is less efficient
def solution(ransomNote: str, magazine: str) -> bool:
    if len(ransomNote) > len(magazine):
        return False

    magazine_list = list(magazine)

    for i in range(len(ransomNote)):
        if ransomNote[i] in magazine_list:
            magazine_list.remove(ransomNote[i])
            print(f"magazine list is now {magazine_list}")
        else:
            return False

    return True


ransomNote1 = "a"
magazine1 = "b"

ransomNote2 = "aa"
magazine2 = "ab"

ransomNote3 = "aabbab"
magazine3 = "bbaaa"

solution(ransomNote=ransomNote1, magazine=magazine1)
solution(ransomNote=ransomNote2, magazine=magazine2)
solution(ransomNote=ransomNote3, magazine=magazine3)


# more efficient solution
def solution(ransomNote: str, magazine: str) -> bool:
    # this creates a dictionary where the key is the letter,
    # and thevalue is the count of how many times it appeared in the str
    ransom_count = Counter(ransomNote)
    magazine_count = Counter(magazine)

    # iterate through ransom and check if magazine has enough letters for each
    # char in ransom. if not, then return false
    for letter, count in ransom_count.items():
        if magazine_count[letter] < count:
            return False
    return True

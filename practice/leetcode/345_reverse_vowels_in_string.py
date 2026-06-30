# Given a string s, reverse only all the vowels in the string and return it.

# The vowels are 'a', 'e', 'i', 'o', and 'u', and they can appear in both lower and upper cases, more than once.


def solution(s: str) -> str:
    # use a set here and turn the string into a list
    vowels = set("aeiouAEIOU")
    s_list = list(s)
    left = 0
    right = len(s_list) - 1

    while left < right:
        # the first inner while loop runs until the left pointer is on a vowel
        while left < right and s_list[left] not in vowels:
            left += 1

        # the second inner while loop runs until the right pointer is on a vowel too
        while left < right and s_list[right] not in vowels:
            right -= 1

        # then we swap them in place and adjust the pointers again
        s_list[left], s_list[right] = s_list[right], s_list[left]
        left += 1
        right -= 1

    return "".join(s_list)


s1 = "IceCreAm"
s2 = "leetcode"

solution(s=s1)
solution(s=s2)

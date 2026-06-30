# .Given an input string s, reverse the order of the words.

# A word is defined as a sequence of non-space characters. The words in s will be separated by at least one space.

# Return a string of the words in reverse order concatenated by a single space.

# Note that s may contain leading or trailing spaces or multiple spaces between two words.
# The returned string should only have a single space separating the words. Do not include any extra spaces.


# IS THAT IT.
def solution(s: str) -> str:
    # turn the word into a list of words, only if it's not an empty space
    words = [word for word in s.split(" ") if word != ""]

    # reverse the list of words
    words_reversed = words[::-1]

    # return it back as a string with 1 space between words
    return " ".join(words_reversed)


s1 = "the sky is blue"
s2 = "  hello world  "

solution(s=s1)
solution(s=s2)

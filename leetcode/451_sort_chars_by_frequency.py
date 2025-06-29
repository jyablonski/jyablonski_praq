# Given a string s, sort it in decreasing order based on the frequency of the characters.
# The frequency of a character is the number of times it appears in the string.

# Return the sorted string. If there are multiple answers, return any of them.


def solution(s: str) -> str:
    counts = {}

    for value in s:
        if value not in counts:
            counts[value] = 1
        else:
            counts[value] += 1

    # sort the dictionary in descending order by value count
    # this syntax would be a bitch to remember though
    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)

    # then multiple each char by its count and return it as a string
    return "".join([x[0] * x[1] for x in sorted_counts])


s1 = "tree"
s2 = "cccaaa"
s3 = "Aabb"

solution(s=s1)
solution(s=s2)
solution(s=s3)

d = {"a": 2, "b": 1, "c": 3}

# was onto something here but you still have to sort it
d_list = [d for d in d.items()]
d_str = [d[0] * d[1] for d in d_list]

# another option
from collections import Counter


def solution(s: str) -> str:
    counts = Counter(s)
    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    return "".join(char * freq for char, freq in sorted_counts)

# Given an array ofx strings strs, group the anagrams together. You can return the answer in any order.

# Anagrams share the same letters in the same counts, so if you sort each word alphabetically, all anagrams will look the same.

# pretty straight forward once you know to use a dictionary where the sorted input word
# is the key, and then you can just add the input words as a list of values for each key.
# return the values at the end


def solution(strs: list[str]) -> list[list[str]]:
    anagram_map = {}

    for word in strs:
        key = "".join(sorted(word))  # sorted letters as key
        if key not in anagram_map:
            anagram_map[key] = []
        anagram_map[key].append(word)

    print(anagram_map)
    return list(anagram_map.values())


strs1 = ["eat", "tea", "tan", "ate", "nat", "bat"]
strs2 = [""]
strs3 = ["a"]

solution(strs=strs1)
solution(strs=strs2)
solution(strs=strs3)

# the sorted word is the key, and each of the input words gets appended to the list of values for it
res = {"aet": ["eat", "tea", "ate"], "ant": ["tan", "nat"], "abt": ["bat"]}
[["eat", "tea", "ate"], ["tan", "nat"], ["bat"]]

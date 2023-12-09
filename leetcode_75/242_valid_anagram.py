# given 2 strings, s and t, return true if t is an anagram of s, and false otherwise


def anagram(s: str, t: str) -> bool:
    if sorted(s) == sorted(t):
        return True
    else:
        return False


c = "bat"
s = "anagram"
t = "margana"

anagram(s=s, t=t)
anagram(s="rat", t="car")
anagram(s="car", t="rac")

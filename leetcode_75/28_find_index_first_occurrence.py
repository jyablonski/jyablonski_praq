# Given two strings needle and haystack, return the index of the first occurrence of needle in haystack, or -1 if needle is not part of haystack.


def solution(haystack: str, needle: str) -> int:
    return haystack.find(needle)


haystack = "sabutsad"
needle = "sad"

solution(haystack=haystack, needle=needle)

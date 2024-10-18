# Given a string s, return true if the s can be palindrome after deleting at most one character from it.


def solution(s: str) -> bool:
    def is_palindrome_range(s, left, right):
        return all(s[i] == s[right - i + left] for i in range(left, right))

    left = 0
    right = len(s) - 1

    while left < right:
        if s[left] != s[right]:
            # Check by removing either the left or right character
            return is_palindrome_range(s, left + 1, right) or is_palindrome_range(
                s=s, left=left, right=right - 1
            )
        left += 1
        right -= 1

    return True


s1 = "aba"
s2 = "abca"

solution(s=s1)
solution(s=s2)

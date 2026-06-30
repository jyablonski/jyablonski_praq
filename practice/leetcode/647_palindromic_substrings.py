# Given a string s, return the number of palindromic substrings in it.
# A string is a palindrome when it reads the same backward as forward.
# A substring is a contiguous sequence of characters within the string.


# very similar to leetcode #5 longest palindromic substring
# here, we're just counting them. so we dont need all of the longest logic,
# we just have to adjust the inner expand center function to return count now,
# and then we call it on all odd length palindromes and all even ones
def solution(s: str) -> int:
    def expand_center(left, right):
        count = 0
        while left >= 0 and right < len(s) and s[left] == s[right]:
            count += 1
            left -= 1
            right += 1

        return count

    total_count = 0
    for i in range(len(s)):
        # count odd length palindromes centered at i
        total_count += expand_center(i, i)

        # count even length palindromes centered between i and i + 1
        total_count += expand_center(i, i + 1)

    return total_count


s1 = "abc"
s2 = "aaa"

solution(s=s1)
solution(s=s2)

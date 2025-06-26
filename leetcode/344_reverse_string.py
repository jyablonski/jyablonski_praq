# Write a function that reverses a string. The input string is given as an array of characters s.

# You must do this by modifying the input array in-place with O(1) extra memory.

# can just so s.reverse(), but this is a loop and tmp solution


# time complexity o(n) and space complexity is o(1)
def solution(s: list[str]) -> None:
    # setup n and left + right pters
    n = len(s)
    left = 0
    right = n - 1

    # loop through with a left < right loop and use tmp
    # to store the latest value you're swapping
    while left < right:
        tmp = s[left]
        s[left] = s[right]
        s[right] = tmp

        # always iterate left by 1 and right be -1
        left += 1
        right -= 1


s1 = ["h", "e", "l", "l", "o"]
s2 = ["H", "a", "n", "n", "a", "h"]

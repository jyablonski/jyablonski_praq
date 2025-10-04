# Given a string s and an integer k, reverse the first k characters for every 2k characters
#     counting from the start of the string.

# If there are fewer than k characters left, reverse all of them. If there are less than 2k but
# greater than or equal to k characters, then reverse the first k characters and leave the other
# as original.


def solution(s: str, k: int) -> str:
    s_list = list(s)

    # process every 2*k characters
    # so if k = 2 and s = "abcdefgh":
    #   1. process "abcd" (0 - 3) reverse first 2
    #   2. process "efgh" (4 - 7) reverse first 2
    for i in range(0, len(s), 2 * k):
        # reverse the first k characters in this chunk
        # Use min to handle case where fewer than k characters remain
        left = i

        # this handles:
        #   1. fewer than k characters left -> reverses all remaining
        #   2. between k and 2k characters, reverses first k, leaves the rest
        right = min(i + k - 1, len(s) - 1)

        # reverse characters from left to right
        while left < right:
            s_list[left], s_list[right] = s_list[right], s_list[left]
            left += 1
            right -= 1

    return "".join(s_list)


s1 = "abcdefg"
k1 = 2

s2 = "abcd"
k2 = 2

solution(s=s1, k=k1)
solution(s=s2, k=k2)

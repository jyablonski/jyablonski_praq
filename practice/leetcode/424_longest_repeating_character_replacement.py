# You are given a string s and an integer k. You can choose any character of the string and
# change it to any other uppercase English character. You can perform this operation at most k times.

# Return the length of the longest substring containing the same letter you can get after performing
# the above operations.


# utilize dictionary to keep track of characters you've passed and how many times
# they've appeared. this only tracks for items in our sliding window
def solution(s: str, k: int) -> int:
    state = {}
    max_freq = 0
    max_len = 0
    start = 0

    # iterate through the string, count the chars, and save them to state
    for end in range(len(s)):
        state[s[end]] = state.get(s[end], 0) + 1

        # keep track of the most frequently used char
        max_freq = max(max_freq, state[s[end]])

        # if the current window size (`end - start + 1`) - `max_freq` is > than `k`,
        # then we have to shrink the window by reducing the count of the character at s[start]
        # in `state` by 1 and also increment start by 1 because we're moving the window

        # we also add 1 to these windows because python is 0 based indexing
        # example: if start is 0 and end is 2, the window is actually 3 elements long, not 2
        if (end - start + 1) - max_freq > k:
            state[s[start]] -= 1
            start += 1

        # always calculate max_len, but only after the window check above ^^
        max_len = max(max_len, end - start + 1)

    return max_len


s1 = "ABAB"
k1 = 2

s2 = "AABABBA"
k2 = 1

solution(s=s1, k=k1)
solution(s=s2, k=k2)

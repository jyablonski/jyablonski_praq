# Given a string s and a list of strings wordDict, return true if s can be matched
# into a space-separated sequence of one or more dictionary words.

# Note that the same word in the dictionary may be reused multiple times in the segmentation.


# time complexity O(n * m) which is len of s multiplied by number of words in wordDict
def solution(s: str, wordDict: list[str]):
    len_s = len(s)

    # initialize our dp object
    # dp is a list of boolean values. dp[i] will be True if the substring s[i:]
    # can be matched into words from wordDict.
    dp = [False] * (len_s + 1)

    # Set base case for end of string: an empty substring can always be matched
    dp[len_s] = True

    # Iterate over the string indices in reverse order
    # In Python, if you're unpacking a tuple but only need one of the values,
    # conventionally _ is used as a placeholder for the second value
    # (in this case, the character from s).
    for i, _ in reversed(list(enumerate(s))):
        # For each index i, we check if there is any word w in wordDict such that:
        # 1. The word w matches the substring from `w[i:]` starting at index i
        # 2. The substring starting right after w can be matched (dp[i + len(w)] is True)

        # Check if the substring s[i:i+len(w)] matches the word w and if the rest of the string can be matched
        dp[i] = any(
            dp[i + len(w)] and s[i : i + len(w)] == w
            for w in wordDict
            if i + len(w) <= len_s  # Ensure the substring is within the bounds of len s
        )
        print(dp)  # Print the dp array for debugging purposes

    # this indiciates whether the entire string can be matched into the words from worddict
    return dp[0]


s = "leetcode"
word_dict = ["leet", "code"]

solution(s=s, wordDict=word_dict)

# this is how it looks when it iterates from the end of the string to the front
# with this kinda substring syntax `s[5:]`
# e
# e
# de
# de
# ode
# ode
# code
# code
# tcod
# tcod
# etco
# etco
# eetc
# eetc
# leet
# leet

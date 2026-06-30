# Given a string s and a list of strings wordDict, return true if s can be matched
# into a space-separated sequence of one or more dictionary words.

# Note that the same word in the dictionary may be reused multiple times in the segmentation.

# we're using a bottom up approach and  starting in reverse order of the string, iterating bigger
# and bigger until we evaluate the whole string to see if we can match it w/ a combination of the dictionary words


# time complexity O(n * m) which is len of s multiplied by number of words in wordDict
def solution(s: str, wordDict: list[str]):
    n = len(s)

    # initialize our dp object with n + 1 to account for the empty string base case
    # dp is a list of boolean values. dp[i] will be True if the substring s[i:]
    # can be matched into words from wordDict.
    dp = [False] * (n + 1)

    # Set base case for end of string: an empty substring can always be matched
    dp[n] = True

    # Iterate over the string indices in reverse order because we know d[n] = True
    # In Python, if you're unpacking a tuple but only need one of the values,
    # conventionally _ is used as a placeholder for the second value
    # (in this case, the character from s).
    for i, _ in reversed(list(enumerate(s))):
        # For each index i, we check if there is any word w in wordDict such that:
        # 1. `s[i:i+len(w)] == w` - does any word in wordDict match the current substring
        # 2. `dp[i + len(w)] == True` - if a match is found, is the rest of the string still breakable
        # 3. `if i + len(w) <= n` - bounds check. ensures you don't slice past the end of the string

        # Check if the substring s[i:i+len(w)] matches the word w and if the rest of the string can be matched
        dp[i] = any(
            s[i : i + len(w)] == w and dp[i + len(w)]
            for w in wordDict
            if i + len(w) <= n  # Ensure the substring is within the bounds of len s
        )
        print(dp)  # Print the dp array for debugging purposes

    # this indiciates whether the entire string can be matched into the words from worddict
    return dp[0]


s1 = "leetcode"
word_dict1 = ["leet", "code"]

s2 = "applepenapple"
word_dict2 = ["apple", "pen"]

solution(s=s1, wordDict=word_dict1)

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


def wordBreak(s: str, wordDict: list[str]) -> bool:
    n = len(s)
    dp = [False] * (n + 1)
    dp[n] = True

    for i, _ in reversed(list(enumerate(s))):
        for w in wordDict:
            if i + len(w) <= n:
                substring = s[i : i + len(w)]
                print(
                    f"i={i}, checking word='{w}', substring='{substring}', dp[{i + len(w)}]={dp[i + len(w)]}"
                )
                if substring == w and dp[i + len(w)]:
                    dp[i] = True
                    print(
                        f"  -> dp[{i}] set to True because '{substring}' is in dict and dp[{i + len(w)}] is True"
                    )
                    print(f"  -> {dp}")
                    break
    print("Final dp table:", dp)
    return dp[0]


s1 = "leetcode"
word_dict1 = ["leet", "code"]

wordBreak(s=s1, wordDict=word_dict1)
wordBreak(s=s2, wordDict=word_dict2)

n = len(s1)
dp = [False] * (n + 1)
dp[n] = True

# s[7: 7 + 4] e so this is s[7:11] but the string is only size 8, so even though it goes over you dont get an out of bounds or anything
# s[6: 7 + 4] de
# s[5: 7 + 4] ode
# s[4: 7 + 4] code

# dp[]

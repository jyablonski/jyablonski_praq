# given a string, find length of the longest contiguous substring without
# any repeating characters


# time complexity is O(n) because we just have to iterate through every character. some chars
# may have to get processed at most twice, but this is still considered linear
# sliding window technique
def solution(s: str) -> int:
    # initialize some variables:
    # values we've passed over in current iteration
    # left pter
    # result for len of longest substring found
    chars = set()
    l = 0
    result = 0

    # iterate through the string
    for value in s:
        # hardest part of this code
        # if the value we're on is found to be already in chars, then
        # we have to update the sliding window 1 record at a time
        # so we remove the value at the left pter and then increment the left pter
        # by 1 and check again if we have any dupes.
        # repeat this until we have no more dupes
        while value in chars:
            chars.remove(s[l])
            l += 1

        # add current value to the chars set
        chars.add(value)

        # update result if the current window is larger than the previous longest one
        # this is the length of all characters in between the current key and the left pter, inclsuive
        # so if key is index 4, and left pter is index 2, there's 3 total values there.
        result = max(result, len(chars))

    return result


str1 = "abcbcbsadfadfadfsadagfdhgyrtjredb"
str2 = "abcycfew"


solution(s=str1)
solution(s=str2)


chars = set()
l = 0
res = 0

for value in s:
    while value in chars:
        chars.remove(s[l])
        l += 1

    chars.add(value)

    res = max(res, len(chars))

return res

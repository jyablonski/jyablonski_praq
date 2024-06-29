# given a string, find length of the longest contiguous substring without
# any repeating characters


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
    for key, value in enumerate(s):
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
        result = max(result, key - l + 1)

    return result


str1 = "abcbcbsadfadfadfsadagfdhgyrtjredb"
str2 = "abcyfew"


solution(s=str1)
solution(s=str2)

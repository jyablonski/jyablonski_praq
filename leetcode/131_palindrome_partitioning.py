# Given a string s, partition s such that every substring of the partition is a palindrome.
# Return all possible palindrome partitioning of s.


def solution(s: str) -> list[list[str]]:
    def is_palindrome(substring):
        return substring == substring[::-1]

    def backtrack(start, current_partition):
        # base case: we've partitioned the entire string
        if start == len(s):
            result.append(current_partition[:])
            return

        # try all possible partitions starting from 'start'
        # we do start + 1 so we always end up at least 1 char, if you did
        #   s[0:0] you'd get an empty string
        #   and if `s = 'hi'` you can do s[0:15], there's no out of bounds issue
        # we do len(s) + 1 so we actually iterate through all the characters in s w/ range
        for end in range(start + 1, len(s) + 1):
            substring = s[start:end]
            if is_palindrome(substring):
                # include this palindrome in current partition
                current_partition.append(substring)

                # recursively partition the rest
                backtrack(end, current_partition)

                # backtrack: remove the substring to try other options
                current_partition.pop()

    result = []
    backtrack(0, [])
    return result


s1 = "aab"
s2 = "a"

solution(s=s1)
solution(s=s2)

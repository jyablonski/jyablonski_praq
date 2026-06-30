# Given the root of a binary tree, return the most frequent subtree sum.
# If there is a tie, return all the values with the highest frequency in any order.

# The subtree sum of a node is defined as the sum of all the node values
# formed by the subtree rooted at that node (including the node itself).
from collections import defaultdict


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def solution(root: TreeNode | None = None) -> list[int]:
    if not root:
        return []

    # use defaultdict so we can immediately increment counts
    # for an integer key that doesnt exist in the dict yet
    freq = defaultdict(int)
    max_freq = 0

    def dfs(node):
        # use nonlocal so we cna access the var out of scope
        nonlocal max_freq

        # return 0 if we hit a null leaf because we're dealing with sums and shit
        if not node:
            return 0

        # do left and right sum and then add eveyrtihng together to `total`
        left_sum = dfs(node.left)
        right_sum = dfs(node.right)
        total = node.val + left_sum + right_sum

        # then we update the frequency of that total by 1, and calculate
        # a new max freq
        freq[total] += 1
        max_freq = max(max_freq, freq[total])

        print(f"freq is {freq}")
        print(f"max_freq is {max_freq}")
        return total

    # run dfs on the root and return all the values that have a count
    # equal to the max freq that we found
    dfs(root)
    return [s for s, count in freq.items() if count == max_freq]


root = [5, 2, -3]

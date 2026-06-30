# Given the root of a binary tree, return all duplicate subtrees.
# For each kind of duplicate subtrees, you only need to return the root node of any one of them.
# Two trees are duplicate if they have the same structure with the same node values.


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


# Use DFS post-order traversal - process children first, then current node, so we build serialization bottom-up
# track result as a list of nodes to return, and a dictionary to track the count of times we've seen duplicate
# subtrees pop up
class Solution:
    def findDuplicateSubtrees(self, root: TreeNode | None) -> list[TreeNode | None]:
        if not root:
            return []

        res = []
        subtree = {}

        def dfs(node):
            if not node:
                return "null"

            left_serial = dfs(node.left)
            right_serial = dfs(node.right)

            # serialize each subtree - convert tree structure to a unique string representation like "val,left,right"
            subtree_serial = f"{node.val},{left_serial},{right_serial}"

            # count subtree occurrences - use a hash map to track how many times each serialized pattern appears
            subtree[subtree_serial] = subtree.get(subtree_serial, 0) + 1

            # add `node` to res only when count hits 2 to ensure we only add each duplicate pattern once, not multiple times
            if subtree[subtree_serial] == 2:
                res.append(node)

            return subtree_serial

        dfs(root)
        return res

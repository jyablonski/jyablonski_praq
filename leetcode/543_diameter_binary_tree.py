# Given the root of a binary tree, return the length of the diameter of the tree.

# The diameter of a binary tree is the length of the longest path between any two nodes in a tree.
# This path may or may not pass through the root.

# The length of a path between two nodes is represented by the number of edges between them.


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


class Solution:
    def diameterOfBinaryTree(self, root: TreeNode | None = None) -> int:
        max_ = 0

        def dfs(node):
            nonlocal max_

            if not node:
                return 0

            left = dfs(node.left)
            right = dfs(node.right)

            max_ = max(max_, left + right)

            return 1 + max(left, right)

        dfs(root)
        return max_


root = [1, 2, 3, 4, 5]

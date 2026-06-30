# Given the root of a binary tree, return the sum of every tree node's tilt.

# The tilt of a tree node is the absolute difference between the sum of all left subtree node values and all
# right subtree node values. If a node does not have a left child, then the sum of the left subtree node
# values is treated as 0. The rule is similar if the node does not have a right child.


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


class Solution:
    def findTilt(self, root: TreeNode | None = None) -> int:
        # define global tilt var to keep track of it
        tilt = 0

        def dfs(node):
            # this is needed in order for the dfs function to add to the global var
            nonlocal tilt

            # base case in recusion: when we try to go PAST a leaf node
            if not node:
                return 0

            # recursively run dfs on left and right
            left = dfs(node.left)
            right = dfs(node.right)

            # add the tilt of the 2 subtree portions that we're on
            tilt += abs(left - right)

            # return the next 2 nodes and the current node value
            return left + right + node.val

        dfs(root)
        return tilt


root1 = [1, 2, 3]
root = [4, 2, 9, 3, 5, None, 7]

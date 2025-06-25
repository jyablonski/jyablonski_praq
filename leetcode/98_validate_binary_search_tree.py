# Given the root of a binary tree, determine if it is a valid binary search tree (BST).

# A valid BST is defined as follows:

# The left subtree of a node contains only nodes with keys less than the node's key.
# The right subtree of a node contains only nodes with keys greater than the node's key.
# Both the left and right subtrees must also be binary search trees.

# maybe helper function to keep track of parent? use min and max
# check if were on a leaf node
# if we're not on a leaf node, ensure root.val > root.left and root.val < root.right
# return false immediately if our conditions ever break


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


class Solution:
    def isValidBST(self, root: TreeNode | None = None) -> bool:
        # use helper function to keep track of min and max for each subtree
        def dfs(node, min_, max_):
            if not node:
                return True

            # if node.val is ever less than the min or greater than the max that we're specifying,
            # then immediately return False as its not a valid BST
            if node.val <= min_ or node.val >= max_:
                return False

            # run dfs on left and right subtrees, and flip flop the node.val around
            # for the left subtree, the min val is -infinity, and the max is node.val
            # for the right subtree, the min val is node.val and the max is infinity
            return dfs(node.left, min_, node.val) and dfs(node.right, node.val, max_)

        # only have to call the actual dfs function on root here
        return dfs(root, float("-inf"), float("inf"))


root = [2, 1, 3]

# Given the roots of two binary trees root and subRoot, return true if there
# is a subtree of root with the same structure and node values of subRoot and false otherwise.

# A subtree of a binary tree tree is a tree that consists of a node in tree and
# all of this node's descendants. The tree tree could also be considered as a subtree of itself.


# this is an extension leetcode #100: same tree
# you basically take the same tree code, and run that while you recursively check the left and right sides
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


class Solution:
    def isSubtree(
        self, root: TreeNode | None = None, subRoot: TreeNode | None = None
    ) -> bool:
        if not root:
            return False

        if self.isSameTree(root, subRoot):
            return True

        return self.isSubtree(root.left, subRoot) or self.isSubtree(root.right, subRoot)

    def isSameTree(self, s, t):
        if not s and not t:
            return True

        if not s or not t:
            return False

        if s.val != t.val:
            return False

        return self.isSameTree(s.left, t.left) and self.isSameTree(s.right, t.right)

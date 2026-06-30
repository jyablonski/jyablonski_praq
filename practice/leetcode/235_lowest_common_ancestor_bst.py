# Given a binary search tree (BST), find the lowest common ancestor (LCA) node of two given
# nodes in the BST.

# According to the definition of LCA on Wikipedia: “The lowest common ancestor is
# defined between two nodes p and q as the lowest node in T that has both p and
# q as descendants (where we allow a node to be a descendant of itself).”

# can use a simple for loop solution because we're in a binary search tree.
# we only go to root.left or root.right if both p and q are over there.
# if not, then return root.


# time complexity is o(h) (height of the tree), as is the space complexity
class TreeNode:
    def __init__(self, x):
        self.val = x
        self.left = None
        self.right = None


class Solution:
    def lowestCommonAncestor(
        self, root: "TreeNode", p: "TreeNode", q: "TreeNode"
    ) -> "TreeNode":
        while root:
            # if root.val is > both p and q, then we can go left
            # and get a lower ancestor
            if root.val > p.val and root.val > q.val:
                root = root.left

            # if root.val is < both p and q, then we can go right
            # and get a lower ancestor
            elif root.val < p.val and root.val < q.val:
                root = root.right
            else:
                return root

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


class Solution:
    def invertTree(self, root: TreeNode | None = None) -> TreeNode | None:
        # if there's nothing to invert, then return None
        if not root:
            return None

        # swap child nodes on the current root node
        tmp = root.left
        root.left = root.right
        root.right = tmp

        # recursively invert left and right subtrees
        self.invertTree(root.left)
        self.invertTree(root.right)
        return root


# before
#      1
#    /   \
#   2     3
#  / \   / \
# 4   5 6   7

# after
#      1
#    /   \
#   3     2
#  / \   / \
# 7   6 5   4
# ```

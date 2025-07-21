# Given two integer arrays preorder and inorder where preorder is the preorder traversal
# of a binary tree and inorder is the inorder traversal of the same tree, construct and
# return the binary tree.


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


class Solution:
    def buildTree(self, preorder: list[int], inorder: list[int]) -> TreeNode | None:
        if not preorder or not inorder:
            return None

        # first value in preorder is always the root
        root_val = preorder[0]
        root = TreeNode(root_val)

        # find index of the root in inorder traversal
        # everything left of this is the left subtree
        # everything right of this is the right subtree
        mid = inorder.index(root_val)

        # recursively build the left and right subtrees from mid
        #   preorder[1 : mid + 1] - next elements after the root
        #   inorder[:mid]         - everything left of root
        #   preorder[mid + 1:]    - rest of preorder after left subtree
        #   inorder[mid + 1:]     - everything right of root
        root.left = self.buildTree(preorder[1 : mid + 1], inorder[:mid])
        root.right = self.buildTree(preorder[mid + 1 :], inorder[mid + 1 :])

        return root


l1 = [10, 15, 20, 25, 30]

mid = 20

# index = 2
mid = l1.index(mid)

# includes everything before mid
# [10, 15]
left = l1[:mid]

# includes everything before and including mid
# [10, 15, 20]
left = l1[: mid + 1]

# includes mid and everything after it
# [20, 25, 30]
mid_inclusive = l1[mid:]

# includes everything after mid only
# [25, 30]
right = l1[1 + mid :]

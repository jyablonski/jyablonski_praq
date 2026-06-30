# You are given two binary trees root1 and root2.

# Imagine that when you put one of them to cover the other, some nodes of the two trees
# are overlapped while the others are not. You need to merge the two trees into a new
# binary tree. The merge rule is that if two nodes overlap, then sum node values up
# as the new value of the merged node. Otherwise, the NOT null node will be used as
# the node of the new tree.

# Return the merged tree.

# Note: The merging process must start from the root nodes of both trees.


# time complexity O(n * m) for number of nodes in tree 1 and number of nodes in tree 2
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


class Solution:
    def mergeTrees(
        self, root1: TreeNode | None = None, root2: TreeNode | None = None
    ) -> TreeNode | None:
        # These checks handle scenarios where one tree might be smaller
        # than the other or where one tree is completely None.
        if not root1:
            return root2
        if not root2:
            return root1

        # If neither root1 nor root2 is None, the method proceeds to merge the nodes

        # root1.val += root2.val adds the value of root2 to root1.
        # This step merges the values of the nodes from both trees.
        root1.val += root2.val

        # then Recursively merge the left and right subtrees:
        root1.left = self.mergeTrees(root1.left, root2.left)
        root1.right = self.mergeTrees(root1.right, root2.right)

        # Finally, the method returns root1, which now represents the merged tree structure.
        return root1


root1 = [1, 3, 2, 5]
root2 = [2, 1, 3, None, 4, None, 7]


# tree 1
#      1
#     / \
#    3   2
#   /
#  5

# tree 2
#    2
#   / \
#  1   3
#   \   \
#    4   7

# resulting merged tree
#      3
#     / \
#    4   5
#   / \   \
#  5   4   7

# Given the root of a binary tree, return its maximum depth.

# A binary tree's maximum depth is the number of nodes along the longest path
# from the root node down to the farthest leaf node.


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def solution(root: TreeNode | None = None) -> int:
    if root is None:
        return 0

    # recursively compute the depth of both left + right subtrees
    left = solution(root.left)
    right = solution(root.right)

    # pick the longer of the 2 subtrees, and add 1 for the root node
    return max(left, right) + 1


root1 = [4, 2, 7, 1, None, 6, 9, None, 8, None, None, None, None, None, None]
root2 = [3, 9, 20, None, None, 15, 7]

solution(root=root1)
solution(root=root2)

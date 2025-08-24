# Given the root of a binary tree and an integer targetSum, return true
# if the tree has a root-to-leaf path such that adding up all the values along the path equals targetSum.

# A leaf is a node with no children.


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


# use a recursive solution to iterate through the tree and keep subtracting the currnet root.val from targetSum
def solution(root, targetSum):
    if not root:
        return False  # Base case: If the tree is empty, no path exists

    # if we hit a leaf node, then check if the path sum equals targetSum
    if not root.left and not root.right:
        return root.val == targetSum

    # take the targetSum we were given, and subtract the current value of the node we're on
    remainder = targetSum - root.val

    # recursively check the left and right subtrees with the reduced target sum
    # use or to return True if any path matches the target sum
    return solution(root.left, remainder) or solution(root.right, remainder)


root1 = [5, 4, 8, 11, None, 13, 4, 7, 2, None, None, None, 1]
targetSum1 = 22

solution(root=root1, targetSum=targetSum1)

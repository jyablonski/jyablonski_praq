# Given the root of a binary tree and an integer targetSum, return all root-to-leaf paths
# where the sum of the node values in the path equals targetSum. Each path should be returned
# xas a list of the node values, not node references.

# A root-to-leaf path is a path starting from the root and ending at any leaf node. A leaf is a
# node with no children.


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


# dont keep track of current path's sum, we just shrink the `targetSum` on each
# recursive call
class Solution:
    def pathSum(
        self,
        targetSum: int,
        root: TreeNode | None = None,
    ) -> list[list[int]]:

        def dfs(node, target, path):
            if not node:
                return
            
            # append current value to the path
            path.append(node.val)

            # if we hit a leaf node, then lets check
            if not node.left and not node.right:

                # if we find a path that equals our target, then append
                # the current path to result
                if node.val == target:
                    result.append(path[:])

            dfs(node.left, target - node.val, path)
            dfs(node.right, target - node.val, path)

            # when our code reaches here, we're done exploring all
            # the root-to-leaf paths that go through the current node.
            # pop the current value from the path to prepare for the next path
            path.pop()

        result = []
        dfs(root, targetSum, [])
        return result


root = [5,4,8,11,None,13,4,7,2,None,None,5,1], targetSum = 22

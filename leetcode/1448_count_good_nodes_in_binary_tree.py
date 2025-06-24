# Given a binary tree root, a node X in the tree is named good if in the path from
# root to X there are no nodes with a value greater than X.

# Return the number of good nodes in the binary tree.


# In order to tell if a root node is "good", we need to know the maximum value of any node on the path starting from the
# original root of the tree to the current node. Since this is a value that must be passed down from parent nodes to children,
# we need to introduce a helper function that introduces an extra parameter max_, which represents the maximum value seen so
# far on the current path from the root.


# To check if the current node is a good node, we compare the current node's value to max_. If the current node's value is
# greater than or equal to max_, then the current node is a good node, and we increment our count by 1.
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


# use a helper function to keep track of the extra param data we need (like the max value we've found along our path so far)
def goodNodes(root: TreeNode) -> int:
    def dfs(root, max_val):
        if root is None:
            return 0

        # set count in each one, and if we find a good node then add 1 to count and update the max
        # value we've found in this subtree
        count = 0
        if root.val >= max_val:
            count += 1
            max_val = root.val

        # then use the new max in the remaining recursive calls for each side
        left = dfs(root.left, max_val)
        right = dfs(root.right, max_val)
        return left + right + count

    # this negativity infinity shit is dumb but w.e
    return dfs(root, -float("inf"))


root = [3, 1, 4, 3, None, 1, 5]

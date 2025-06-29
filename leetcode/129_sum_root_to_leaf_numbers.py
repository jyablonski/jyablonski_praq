# You are given the root of a binary tree containing digits from 0 to 9 only.

# Each root-to-leaf path in the tree represents a number.

# For example, the root-to-leaf path 1 -> 2 -> 3 represents the number 123.
# Return the total sum of all root-to-leaf numbers. Test cases are generated so that the answer will fit in a 32-bit integer.

# A leaf node is a node with no children.


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


# more optimal solution
class Solution:
    def sumNumbers(self, root: TreeNode | None = None) -> int:
        def dfs(node, current_num):
            if not node:
                return 0

            # use current_num to keep track of the numbers we're on
            current_num = current_num * 10 + node.val

            # we hit a leaf node, just return current_num
            if not node.left and not node.right:
                return current_num

            # return dfs on both the left and right nodes recursively
            return dfs(node.left, current_num) + dfs(node.right, current_num)

        return dfs(root, 0)


# my first solution, but of course a more optimal solution exists
class Solution:
    def sumNumbers(self, root: TreeNode | None = None) -> int:
        if not root:
            return 0

        paths = []

        def dfs(node, path):
            if not node:
                return 0

            path.append(node.val)

            if not node.left and not node.right:
                paths.append(path[:])

            dfs(node.left, path)
            dfs(node.right, path)

            path.pop()

        dfs(root, [])
        res = 0
        for sublist in paths:
            individual_res = ""
            for char in sublist:
                individual_res += str(char)

            res += int(individual_res)

        return res


# about to set num to 0 * 10 + 1
# about to set num to 1 * 10 + 2
# about to set num to 12 * 10 + 3
# about to set num to 0 * 10 + 4
# about to set num to 4 * 10 + 5
paths = [[1, 2, 3], [4, 5]]
res = 0
for sublist in paths:
    num = 0
    for digit in sublist:
        print(f"about to set num to {num} * 10 + {digit}")
        num = num * 10 + digit
    res += num

# Given the root of a binary tree, return the maximum width of the given tree.

# The maximum width of a tree is the maximum width among all levels.

# The width of one level is defined as the length between the end-nodes (the leftmost and rightmost non-null nodes),
# where the null nodes between the end-nodes that would be present in a complete binary tree extending down
# to that level are also counted into the length calculation.

# It is guaranteed that the answer will in the range of a 32-bit signed integer.
from collections import deque


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


class Solution:
    def widthOfBinaryTree(self, root: TreeNode | None) -> int:
        if not root:
            return []

        # enqueue the root node with position 0
        queue = deque([(root, 0)])
        max_width = 0

        while queue:
            level_size = len(queue)

            # left_pos is the position of the leftmost node at the current level
            _, left_pos = queue[0]
            right_pos = -1

            for i in range(level_size):
                node, pos = queue.popleft()

                # when we reach the last node in the level, then
                # update rightPos to the position of the rightmost node
                if i == level_size - 1:
                    right_pos = pos

                # add the children to the queue with their positions
                if node.left:
                    queue.append((node.left, 2 * pos))

                if node.right:
                    queue.append((node.right, 2 * pos + 1))

            # the width is right_pos - left_pos + 1, same as sliding window problems
            # if the max level has index 0 and index 7, then the actual width = 8
            width = right_pos - left_pos + 1
            max_width = max(max_width, width)

        return max_width


root = [1, 3, 2, 5, 3, None, 9]

# Given the root of a binary tree, imagine yourself standing on the right side of it,
# return the values of the nodes you can see ordered from top to bottom.

from collections import deque


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


class Solution:
    def rightSideView(self, root: TreeNode | None = None) -> list[int]:
        if not root:
            return []

        nodes = []

        # turn the root node into a queue
        queue = deque([root])

        # while we have levels in the queue:
        while queue:
            level_size = len(queue)

            # for every node in the current level
            for i in range(level_size):
                node = queue.popleft()

                # append the right most node
                # think like right = len(n) - 1
                if i == level_size - 1:
                    nodes.append(node.val)

                # then add its children, if any exist
                if node.left:
                    queue.append(node.left)

                if node.right:
                    queue.append(node.right)

        return nodes


d = [1, 2, 3, None, 5, None, 4]

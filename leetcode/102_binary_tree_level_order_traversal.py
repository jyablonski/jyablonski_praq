# Given the root of a binary tree, return the level order traversal
# of its nodes' values. (i.e., from left to right, level by level).

from collections import deque


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


class Solution:
    def levelOrder(self, root: TreeNode | None = None) -> list[list[int]]:
        # handle edge case where root is passed in as [] or something
        if not root:
            return []

        # initialize `nodes` which we will return later, and setup the queue
        nodes = []
        queue = deque([root])

        # BFS solution, so we operate from top down, left to right, at each level
        # while we still have elements in the queue:
        while queue:
            # standard BFS stuff
            level_size = len(queue)
            nodes_for_level = deque()

            # for every level in the tree:
            for _ in range(level_size):
                # grab a node, add it to our current level node list
                node = queue.popleft()
                nodes_for_level.append(node.val)

                # if current node has left or right children that are not None,
                # then add them to the queue
                if node.left:
                    queue.append(node.left)

                if node.right:
                    queue.append(node.right)

            # after we finish the level, append that list to our `nodes` variable
            nodes.append(list(nodes_for_level))

        return nodes

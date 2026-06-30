# Given the root of a binary tree, return the zigzag level order traversal of its nodes' values.
# (i.e., from left to right, then right to left for the next level and alternate between).


from collections import deque


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


class Solution:
    def zigzagLevelOrder(self, root: TreeNode | None = None) -> list[list[int]]:
        if not root:
            return []

        # standard setup
        nodes = []
        queue = deque([root])

        # to enable the zigzag functionality, use a boolean
        left_to_right = True

        while queue:
            level_size = len(queue)

            # use dequeu and appendleft to figure out if we want to add node values
            # on the left or the right
            nodes_for_level = deque()

            for i in range(level_size):
                node = queue.popleft()

                if left_to_right:
                    nodes_for_level.append(node.val)
                else:
                    nodes_for_level.appendleft(node.val)

                # then add its children, if any exist
                if node.left:
                    queue.append(node.left)

                if node.right:
                    queue.append(node.right)

            # after we finished the level, append the nodes for level
            # to nodes and flip left_to_right
            nodes.append(list(nodes_for_level))
            left_to_right = not left_to_right

        return nodes

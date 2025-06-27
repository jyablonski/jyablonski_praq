# Given a reference of a node in a connected undirected graph.

# Return a deep copy (clone) of the graph.

# Each node in the graph contains a value (int) and a list (List[Node]) of its neighbors.

# class Node {
#     public int val;
#     public List<Node> neighbors;
# }


# Test case format:

# For simplicity, each node's value is the same as the node's index (1-indexed). For example, the first node with val == 1,
# the second node with val == 2, and so on. The graph is represented in the test case using an adjacency list.

# An adjacency list is a collection of unordered lists used to represent a finite graph. Each list describes the set of
# neighbors of a node in the graph.

# The given node will always be the first node with val = 1. You must return the copy of the given node as a reference
# to the cloned graph.


# this is pretty fucking stupid lmfao
class Node:
    def __init__(self, val=0, neighbors=None):
        self.val = val
        self.neighbors = neighbors if neighbors is not None else []


from typing import Optional


# time complexity is O(N + M) where N is number of nodes and M is number of edges in the graph
# space compleixty also O(N + M), we have to store N keys and all M edges as values in the dictionary
class Solution:
    def cloneGraph(self, node: Optional["Node"]) -> Optional["Node"]:
        if not node:
            return None

        visited = {}

        # recursive helper function to perform DFS
        def dfs(n):
            if id(n) in visited:
                return visited[id(n)]

            clone = Node(n.val)
            visited[id(n)] = clone

            for neighbor in n.neighbors:
                clone.neighbors.append(dfs(neighbor))

            return clone

        return dfs(node)


adjList = [[2, 4], [1, 3], [2, 4], [1, 3]]

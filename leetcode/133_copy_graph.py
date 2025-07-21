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

# the solution involves DFS and basically 3 parts:
#   - check if the id of node we're on is in the `visited` dictionary, and skip it if so
#   - if node not in visited, add it
#   - then recursively go through the node's neighbors to build it up
# a bit weird beceause you call dfs in both the parent function and again in the function itself


# time complexity is O(N + M) where N is number of nodes and M is number of edges in the graph
# space compleixty also O(N + M), we have to store N keys and all M edges as values in the dictionary
class Node:
    def __init__(self, val=0, neighbors=None):
        self.val = val
        self.neighbors = neighbors if neighbors is not None else []


class Solution:
    def cloneGraph(self, node: Node | None = None) -> Node | None:
        if not node:
            return None

        visited = {}

        # recursive helper function to perform DFS
        def dfs(n):
            # base case: if the node was already cloned, return the clone
            if id(n) in visited:
                return visited[id(n)]

            # clone the node and add it to `visited` to avoid reprocessing it
            clone = Node(n.val)
            visited[id(n)] = clone

            # recursively go through each neighbor and add its clone to the clone's
            # neighbors list to build up the same neighbor structure in the clone
            for neighbor in n.neighbors:
                clone.neighbors.append(dfs(neighbor))

            return clone

        return dfs(node)


adjList = [[2, 4], [1, 3], [2, 4], [1, 3]]

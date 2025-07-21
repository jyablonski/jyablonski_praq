# There are a total of numCourses courses you have to take, labeled from 0 to numCourses - 1.
# You are given an array prerequisites where prerequisites[i] = [ai, bi] indicates that you must
# take course bi first if you want to take course ai.

# For example, the pair [0, 1], indicates that to take course 0 you have to first take course 1.
# Return true if you can finish all courses. Otherwise, return false.

# Time: O(V + E), where V = numCourses, E = number of prerequisites
# Space: O(V + E) for graph + recursion stack
# solution involves DFS w/ cycle detection

from collections import defaultdict


def solution(numCourses: int, prerequisites: list[list[int]]) -> bool:
    # default dict jsut makes it easier to do the appending for the adj list
    graph = defaultdict(list)

    # build adjacency list to represent this problem as a graph
    for dest, src in prerequisites:
        graph[src].append(dest)

    # 0 = unvisited, 1 = visiting, 2 = visited
    visited = [0] * numCourses

    #
    def dfs(course):
        # found cycle
        if visited[course] == 1:
            return False

        # already checked
        if visited[course] == 2:
            return True

        # mark as visiting
        visited[course] = 1

        for neighbor in graph[course]:
            if not dfs(neighbor):
                return False

        # mark as fully visited
        visited[course] = 2
        return True

    # for every course, run dfs on it and if we detect a cycle and cant
    # complete all courses, then we return false
    for course in range(numCourses):
        if not dfs(course):
            return False

    # else return true if we havent hit a cycle after iterating through all courses
    return True


numCourses1 = 2
prerequisites1 = [[1, 0]]

numCourses2 = 2
prerequisites2 = [[1, 0], [0, 1]]

solution(numCourses=numCourses1, prerequisites=prerequisites1)
solution(numCourses=numCourses2, prerequisites=prerequisites2)

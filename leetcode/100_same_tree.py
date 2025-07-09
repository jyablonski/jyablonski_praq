# Given the roots of two binary trees p and q, write a function to check if they are the same or not.

# Two binary trees are considered the same if they are structurally identical, and the nodes have the same value.


# use recursion and check for the following conditions everytime:
#   1. if both nodes are None, then return True
#   2. if only 1 of them is None, return False
#   3. if the value we're on is not the same, return False
def solution(p, q):
    if not p and not q:
        return True

    if not p or not q:
        return False

    if p.val != q.val:
        return False

    return solution(p.left, q.left) and solution(p.right, q.right)

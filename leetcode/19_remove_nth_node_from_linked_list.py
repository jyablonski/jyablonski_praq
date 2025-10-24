# Given the head of a linked list, remove the nth node from the end of the list and return its head.


class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


# you can modify the `head` through `current = head`
# find length of list first
# then check edge case, reset current, and skip over the node to "delete"
def solution(n: int, head: ListNode | None = None) -> ListNode | None:
    length = 0
    current = head
    while current:
        length += 1
        current = current.next

    # handle edge case where the list is as large as n
    if n == length:
        return head.next

    # iterate up until we get to the node BEFORE the node we're removing
    # we do -1 as well because we want to update the previous node
    current = head
    for _ in range(length - n - 1):
        current = current.next

    current.next = current.next.next
    return head


# 2 pointer approach
def removeNthFromEnd(head, n):
    # initial fast and slow pointers
    fast = slow = head

    # move faster point n + 1 steps ahead
    for _ in range(n):
        fast = fast.next

    # special case: if we're asked to remove the head
    # of the linked list, then we just return head.next
    if not fast:
        return head.next

    # Move both pointers until fast reaches the end
    # This maintains a gap of n+1 nodes between them
    while fast.next:
        fast = fast.next
        slow = slow.next

    # Now slow is at the node right before the one we want to remove
    # Skip the target node
    slow.next = slow.next.next
    return head


head = [1, 2, 3, 4, 5]
n = 2

for i in range(2):
    print(i)

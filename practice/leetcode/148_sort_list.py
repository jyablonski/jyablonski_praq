# Given the head of a linked list, return the list after sorting it in ascending order.


# use concepts from merge sort to split the linked list into 2 parts and then incrementally
# build the new sorted list

# time complexity O(n log n) and space complexity of O(log n) for recursion stack
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def solution(head: ListNode | None = None) -> ListNode | None:
    if not head or not head.next:
        return head

    # use slow and fast pointers to split the current linked list
    # into 2 halves
    slow = head
    fast = head.next
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next

    # set mid to slow.next and then chop slow.next off
    mid = slow.next
    slow.next = None

    # recursively sort both halves
    left = solution(head)
    right = solution(mid)

    # combine the sorted halves
    return merge(left, right)


def merge(l1: ListNode, l2: ListNode) -> ListNode:
    dummy = ListNode()
    tail = dummy

    while l1 and l2:
        if l1.val < l2.val:
            # set the next tail
            tail.next = l1

            # then trim the current list we just used
            l1 = l1.next
        else:
            tail.next = l2
            l2 = l2.next

        # always update the pointer
        tail = tail.next

    # Attach the rest
    tail.next = l1 if l1 else l2
    return dummy.next


head = [4, 2, 1, 3]

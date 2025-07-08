class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


class Solution:
    def reverseList(self, head: ListNode | None = None) -> ListNode | None:
        prev = None
        current = head

        while current:
            # 1. make pointer to next_node
            next_node = current.next

            # 2. update current to point to prev
            current.next = prev

            # 3. get ready for next node
            #       update prev to point to current
            #       update current to point to next
            prev = current
            current = next_node

        # prev is now the head of the mf list
        return prev

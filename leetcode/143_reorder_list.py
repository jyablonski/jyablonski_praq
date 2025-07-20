# You are given the head of a singly linked-list. The list can be represented as:

# L0 → L1 → … → Ln - 1 → Ln
# Reorder the list to be on the following form:

# L0 → Ln → L1 → Ln - 1 → L2 → Ln - 2 → …
# You may not modify the values in the list's nodes. Only nodes themselves may be changed.

#

# Time: O(n) – one pass to find middle, one to reverse, one to merge.
# Space: O(1) – in-place reordering with no extra memory.


class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


class Solution:
    def reorderList(self, head: ListNode | None = None) -> None:
        if not head or not head.next:
            return

        # find the middle of the list
        # because fast moves 2x as fast, when fast reaches the end,
        # slow will be at the midpoint
        slow = head
        fast = head
        while fast and fast.next:
            slow = slow.next
            fast = fast.next.next

        # now that we have the midpoint w/ `slow`, we can reverse the second
        # half of the list
        prev = None
        curr = slow.next
        slow.next = None  # cut off first half

        #
        while curr:
            next_node = curr.next
            curr.next = prev
            prev = curr
            curr = next_node

        # merge the two halves together now
        first = head
        second = prev
        while second:
            tmp1, tmp2 = first.next, second.next
            first.next = second
            second.next = tmp1

            first = tmp1
            second = tmp2

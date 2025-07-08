# Given the head of a singly linked list, return true if it is a palindrome or false otherwise.


class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


# o(n) solution with o(n) space
def solution(head: ListNode | None = None) -> bool:
    vals = []
    current_node = head

    while current_node:
        vals.append(current_node.val)
        current_node = current_node.next

    print(vals)
    return vals == vals[::1]


head = [1, 2, 2, 1]


# o(n) solution with o(1) spacew oooooh wooooah
class Solution:
    def isPalindrome(self, head: ListNode | None = None) -> bool:
        if not head or not head.next:
            return True

        # Step 1: Find the middle using fast and slow pointers
        slow = head
        fast = head
        while fast and fast.next:
            fast = fast.next.next
            slow = slow.next

        # Step 2: Reverse the second half of the list
        prev = None
        curr = slow
        while curr:
            next_temp = curr.next
            curr.next = prev
            prev = curr
            curr = next_temp

        # Step 3: Compare first and second half
        first = head
        second = prev
        while second:
            if first.val != second.val:
                return False
            first = first.next
            second = second.next

        return True

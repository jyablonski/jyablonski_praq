# some dumb lniked list shit
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def solution(list1, list2):
    # dummy is like a placeholder head, we only use it to know the starting
    # point of the new list
    dummy = ListNode(-1)
    tail = dummy

    # while we have values in both linked lists:
    while list1 and list2:
        # compare list1 vs list2 values, and adjust
        # tail and the list accordingly depending on what one is chosen
        if list1.val < list2.val:
            tail.next = list1
            list1 = list1.next

        else:
            tail.next = list2
            list2 = list2.next

        # always increment the tail
        tail = tail.next

    # once we break out of the loop, set the remaining list to tail.next
    tail.next = list1 or list2
    return dummy.next


list1 = [1, 2, 4]
list2 = [1, 3, 4]

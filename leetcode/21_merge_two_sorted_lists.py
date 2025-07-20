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

    # only iterate while we have elements in both lists still
    while list1 and list2:
        # compare list1 vs list2 values, and adjust
        # tail and the list accordingly depending on what one is chosen
        if list1.val < list2.val:
            tail.next = list1
            list1 = list1.next

        else:
            tail.next = list2
            list2 = list2.next

        # always advance the tail pointer so we're pointing to the last node
        # in the merged list, and ready to add the next node
        tail = tail.next

    # once we run out of elements in one of the lists, attach the remainder of
    # whichever list to tail.next
    tail.next = list1 or list2

    # return dummy.next, which is the actual start of the new merged linked list we
    # just made
    return dummy.next


list1 = [1, 2, 4]
list2 = [1, 3, 4]

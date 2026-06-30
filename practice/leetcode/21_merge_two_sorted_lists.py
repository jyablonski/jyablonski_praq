# some dumb lniked list shit
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


# 1. create a dummy node as a placeholder head and set tail equal to it
# 2. while loop for while we have elemnts in l1 and l2:
# 3. compare l1.val and l2.val, and append the smaller one so we merge them in order
#     - this syntax looks like tail.next = l1, l1 = l1.next so we're connecting nodes by reference here
#     - The beauty of this algorithm is that it reuses existing nodes by just rearranging the pointers.
# 4. at the end of every loop, do tail = tail.next to advance the pointer so its ready to add a new node
# 5. after 1 list is finished, you just do tail.next = l1 or l2 to append the rest of those nodes
# 6. return dummy.next so we get the entire linked lists thats now merged, and not the dummy value
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

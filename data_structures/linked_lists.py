class Node:
    def __init__(self, data):
        self.data = data
        self.next_node = None


class LinkedList:
    def __init__(self):
        self.head = None

    def is_empty(self):
        return self.head is None

    def append(self, data):
        new_node = Node(data)
        if self.head is None:
            self.head = new_node
            return

        current_node = self.head
        while current_node.next_node:
            current_node = current_node.next_node

        current_node.next_node = new_node

    def prepend(self, data):
        new_node = Node(data)
        new_node.next_node = self.head
        self.head = new_node

    def delete(self, data):
        if self.head is None:
            return

        if self.head.data == data:
            self.head = self.head.next_node
            return

        current_node = self.head
        while current_node.next_node and current_node.next_node.data != data:
            current_node = current_node.next_node

        if current_node.next_node:
            current_node.next_node = current_node.next_node.next_node

    def display(self):
        current_node = self.head
        while current_node:
            print(current_node.data, end=" -> ")
            current_node = current_node.next_node
        print("None")

    def get_head(self):
        return self.head.data


# Example usage:
linked_list = LinkedList()

linked_list.is_empty()
linked_list.append([1, 2])
linked_list.append({1: 2})
linked_list.display()
linked_list.append(3)
linked_list.append(300)
linked_list.prepend(0)
linked_list.display()
linked_list.get_head()

linked_list.delete(2)
linked_list.display()


class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

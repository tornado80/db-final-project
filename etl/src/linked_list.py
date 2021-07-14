class Node:
    def __init__(self, key):
        self.__next = None
        self.__key = key

    @property
    def key(self):
        return self.__key

    @property
    def next(self):
        return self.__next

    @next.setter
    def next(self, node):
        self.__next = node


class LinkedList:
    def __init__(self):
        self.__length = 0
        self.__head = None

    def add(self, key):
        node = Node(key)
        node.next = self.__head
        self.__head = node
        self.__length += 1

    def __iter__(self):
        ptr = self.__head
        while ptr is not None:
            yield ptr.key
            ptr = ptr.next

    def __len__(self):
        return self.__length


__all__ = ["LinkedList"]

if __name__ == "__main__":
    l = LinkedList()
    for i in range(5):
        l.add(i)
    for j in l:
        print(j)

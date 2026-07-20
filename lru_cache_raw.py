
from typing import Any

class Node:

    def __init__(self, key: Any = None, value: Any = None):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None
    
class LRUcacheRaw:
    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("Capacity must be a positive integer.")
        self.capacity = capacity
        self.cache = {}
        self.head = Node()
        self.tail = Node()
        self.head.next = self.tail
        self.tail.prev = self.head
    
    def remove(self, node: Node):
        node.prev.next = node.next
        node.next.prev = node.prev

    def add_to_front(self, node: Node):
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node
    
    def move_to_front(self, node: Node):
        self.remove(node)
        self.add_to_front(node)
    
    def get(self, key: Any) -> Any:
        if key in self.cache:
            node = self.cache[key]
            self.move_to_front(node)
            return node.value
        return None
    
    def put(self, key: Any, value: Any):
        if key in self.cache:
            node = self.cache[key]
            node.value = value
            self.move_to_front(node)
        else:
            if len(self.cache) >= self.capacity:
                # Remove the least recently used item
                lru_node = self.tail.prev
                self.remove(lru_node)
                del self.cache[lru_node.key]
            new_node = Node(key, value)
            self.add_to_front(new_node)
            self.cache[key] = new_node
            
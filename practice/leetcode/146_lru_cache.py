# Design a data structure that follows the constraints of a Least Recently Used (LRU) cache.

# Implement the LRUCache class:

# LRUCache(int capacity) Initialize the LRU cache with positive size capacity.
# int get(int key) Return the value of the key if the key exists, otherwise return -1.
# void put(int key, int value) Update the value of the key if the key exists. Otherwise,
# add the key-value pair to the cache. If the number of keys exceeds the capacity from
# this operation, evict the least recently used key.
# The functions get and put must each run in O(1) average time complexity.

# dumb as fuck
class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}
        self.last_key = None

    def get(self, key: int) -> int:
        item = self.cache.get(key)

        return item if not None else -1

    def put(self, key: int, value: int) -> None:
        if len(self.cache) >= self.capacity:
            self.cache.pop(self.last_key)

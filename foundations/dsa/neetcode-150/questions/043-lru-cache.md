# LRU Cache

**LeetCode 146** · Linked List · concepts: [[03-hash-maps|hash-maps]], [[04-linked-lists|linked-lists]]

## Problem

Design a fixed-capacity cache with O(1) `get` and `put`. When full, evict the **least recently used** entry. Any access (get or put) counts as "using" a key.

## The idea — hash map + doubly linked list

Two O(1) requirements pull in different directions: **lookup by key** (hash map) and **ordering by recency with fast move-to-front and evict-from-back** (doubly linked list). Combine them: the map points key → node; the DLL maintains recency order.

- **Doubly** linked (not singly) so any node can be unlinked in O(1) given its neighbors.
- Two sentinel nodes (`head`, `tail`) remove all null-edge-case branching. Most-recent sits next to `head`; least-recent next to `tail`.

```python
class Node:
    def __init__(self, k, v):
        self.key, self.val = k, v
        self.prev = self.next = None

class LRUCache:
    def __init__(self, capacity):
        self.cap = capacity
        self.map = {}                       # key -> Node
        self.head, self.tail = Node(0, 0), Node(0, 0)   # sentinels
        self.head.next, self.tail.prev = self.tail, self.head

    def _remove(self, node):
        node.prev.next, node.next.prev = node.next, node.prev

    def _insert_front(self, node):          # right after head = most recent
        node.next, node.prev = self.head.next, self.head
        self.head.next.prev = node
        self.head.next = node

    def get(self, key):
        if key not in self.map:
            return -1
        node = self.map[key]
        self._remove(node); self._insert_front(node)    # mark most-recently-used
        return node.val

    def put(self, key, value):
        if key in self.map:
            self._remove(self.map[key])
        node = Node(key, value)
        self.map[key] = node
        self._insert_front(node)
        if len(self.map) > self.cap:                    # evict least recent
            lru = self.tail.prev
            self._remove(lru)
            del self.map[lru.key]
```

**Time O(1) per operation, space O(capacity).**

## Why doubly linked + sentinels

A singly linked list can't unlink a node in O(1) (no back pointer). Sentinel head/tail mean `_remove`/`_insert_front` never check for null — every real node always has both neighbors. This is the cleanest expression of "hash map for lookup, linked list for order."

## Key insight

**O(1) lookup + O(1) recency ordering → hash map (key→node) over a doubly linked list.** The map answers "where is this key," the list answers "what's least recent." It's the canonical structure-combination design problem, and the same pattern (map + DLL) underlies LFU and many caches.

## Related
- concepts: [[03-hash-maps|hash-maps]], [[04-linked-lists|linked-lists]]
- prev: [[042-find-the-duplicate-number|Find the Duplicate Number]] · next: [[044-merge-k-sorted-lists|Merge K Sorted Lists]]

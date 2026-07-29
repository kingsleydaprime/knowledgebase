# Linked Lists

A linked list is a sequence of nodes where each node holds a value and a pointer to the next node. Unlike an [[01-arrays|array]], the nodes don't have to sit next to each other in memory — they can be scattered anywhere, connected purely by pointers. That one difference flips almost every tradeoff an array has.

## Why it exists

Arrays need one contiguous block, which means growing or shrinking in the middle means shifting every element after the change — O(n). A linked list never shifts anything: to insert a node, you just repoint a couple of pointers, O(1), *if you already have a reference to the node it goes next to*. The cost is that you lose direct indexing — to get to the 5th node you have to walk from the head, one pointer at a time.

## How it works

**Singly linked list** — each node points only forward:

```
head -> [10 | *] -> [22 | *] -> [7 | *] -> [41 | None]
```

**Doubly linked list** — each node points forward and backward, so you can walk in either direction and delete a node in O(1) without needing a separate reference to its predecessor:

```
None <- [10 | *|*] <-> [22 | *|*] <-> [7 | *|*] -> None
```

A node is just a small object/struct:

```python
class Node:
    def __init__(self, value):
        self.value = value
        self.next = None
```

## Complexity

| Operation | Time | Why |
|---|---|---|
| Access by index | O(n) | must walk from the head |
| Search | O(n) | same reason |
| Insert/delete at head | O(1) | just repoint `head` |
| Insert/delete given a node reference | O(1) | just repoint a couple of pointers |
| Insert/delete at tail (singly, no tail pointer) | O(n) | have to walk to the end first |

Compare directly against [[01-arrays|arrays]]: linked lists win at insert/delete near a known position, arrays win at random access and cache locality. Neither is strictly better — pick based on which operation dominates your use case.

## Example

```python
class Node:
    def __init__(self, value):
        self.value = value
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None

    def push_front(self, value):       # O(1)
        node = Node(value)
        node.next = self.head
        self.head = node

    def find(self, value):             # O(n)
        cur = self.head
        while cur:
            if cur.value == value:
                return cur
            cur = cur.next
        return None
```

## Why use it over an array at all

- **LRU caches**: doubly linked list + hash map is the classic combo — the list gives O(1) reordering (move a node to the front), the map gives O(1) lookup of *which* node to move.
- **Undo/redo stacks**, **implementing other structures** (stacks, queues) where you only ever touch the ends.
- Anywhere insert/delete frequency is high relative to random-access reads.

In practice, for most everyday code, dynamic arrays win because of cache locality (see [[01-arrays|arrays]]) even when the Big-O favors linked lists — this is a case where real hardware behavior matters more than asymptotic complexity.

## Gotchas

- **Losing the head reference is fatal** — if you overwrite `head` before saving a pointer to the old first node, the rest of the list becomes unreachable (garbage, in a language without manual memory management it just leaks conceptually; in C it's a real memory leak).
- Off-by-one errors when manipulating `.next` pointers during insert/delete are the single most common source of bugs — always draw the before/after picture (`A -> B -> C` becoming `A -> X -> B -> C`) before writing the pointer reassignment lines, and reassign in an order that doesn't overwrite a pointer you still need.
- Singly linked lists can't be traversed backward — if you need that, you need a doubly linked list or you need to reverse it first.
- Detecting a cycle (a node's `.next` eventually points back into the list) needs its own technique — see the fast/slow pointer pattern we'll get to when covering LeetCode patterns.

## Related
- [[01-arrays|arrays]]
- [[02-traversal|traversal]]

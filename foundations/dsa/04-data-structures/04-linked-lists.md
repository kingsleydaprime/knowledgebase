# Module: Linked Lists (Pointer-Based Nodes)

Welcome to the **Linked Lists** module. Unlike [[01-arrays|Arrays]], where elements are stored side-by-side in contiguous memory, a **Linked List** stores data in scattered, independent memory blocks called **Nodes**. Each node holds a piece of data and a **Pointer** holding the memory address of the next node.

---

## 1. Why Do Linked Lists Exist? (Real-World Motivation)

Imagine a physical **Scavenger Hunt / Treasure Hunt**:

```
Clue 1 (Base Camp)   --->  Clue 2 (Under Oak Tree)  --->  Clue 3 (Inside Cave)
[ Location: Cave ]         [ Location: Lake ]             [ Treasure! ]
```

- Each clue holds a message *and* directions to where the next clue is hidden.
- If you want to add a new clue between Clue 1 and Clue 2, you don't need to move the Oak Tree or the Cave! You simply write a new sticky note and update the directions.

In computer science, this is a **Linked List**. Because nodes are connected purely by pointers, you can insert or remove nodes in **$O(1)$ Constant Time** without shifting any other items in memory.

---

## 2. Plain-English Terminology & Concept Table

| Term | Plain-English Definition | Example / Analogy |
| :--- | :--- | :--- |
| **Node** | A container object holding a data value and pointer(s). | A single scavenger clue card. |
| **Pointer (`next`)** | A memory address reference pointing to another node. | Address written on a sticky note. |
| **Head** | A pointer pointing to the very first node in the list. | The starting clue at Base Camp. |
| **Tail** | The final node in the list (`next` points to `None`). | The final clue card. |
| **Sentinel (Dummy Head)** | A fake initial node added to simplify pointer code. | An empty placeholder envelope at the start. |

---

## 3. The 4 Main Variations of Linked Lists

```
1. Singly Linked List:
   Head -> [ Value | Next ] -> [ Value | Next ] -> None

2. Doubly Linked List:
   None <- [ Prev | Value | Next ] <-> [ Prev | Value | Next ] -> None

3. Circular Singly Linked List:
   ┌──────────────────────────────────────────────┐
   └─> [ Value | Next ] -> [ Value | Next ] ──────┘

4. Circular Doubly Linked List:
   ┌────────────────────────────────────────────────────────┐
   └─> [ Prev | Value | Next ] <-> [ Prev | Value | Next ] ─┘
```

### Feature Comparison Table

| Variant | Pointers per Node | Traversal Direction | Delete Node in $O(1)$? | Real-World Use Case |
| :--- | :--- | :--- | :--- | :--- |
| **Singly Linked** | 1 (`next`) | Forward only | ✗ (Requires predecessor) | Simple Stacks, memory-constrained devices. |
| **Doubly Linked** | 2 (`prev`, `next`) | Forward & Backward | **✓ Yes** | **LRU Caches**, Browser back/forward history. |
| **Circular Singly** | 1 (`next`) | Forward (Loops) | ✗ | Round-robin CPU schedulers, music playlists. |
| **Circular Doubly**| 2 (`prev`, `next`) | Both (Loops) | **✓ Yes** | **Linux Kernel Process List** (`list_head`). |

---

## 4. The Sentinel Node (Dummy Head) Trick

> [!TIP]
> 90% of linked list bugs (and interview crashes) happen during special edge cases: inserting into an empty list, deleting the head, or deleting the last node.

A **Sentinel (Dummy Head)** is a fake node placed before the real head. It ensures the list is **never empty**, eliminating special `if` conditions!

```python
class Node:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def remove_element(head: Node, target: int) -> Node:
    """Removes all nodes with val == target using a Sentinel Node."""
    dummy = Node(0)       # Sentinel node
    dummy.next = head     # Connect sentinel to real head
    
    current = dummy
    while current.next:
        if current.next.val == target:
            # Skip the target node by re-routing pointers
            current.next = current.next.next
        else:
            current = current.next
            
    return dummy.next     # Return the real head
```

Notice how `remove_element` handles deleting the head node effortlessly without a single `if head is None` check!

---

## 5. Linked Lists vs. Arrays: The Hardware Reality Check

On paper, linked lists seem superior for insertions ($O(1)$ vs $O(n)$). However, in modern computer hardware, **Dynamic Arrays usually outperform Linked Lists**:

```
Array (Contiguous in RAM):
[ Node 0 ][ Node 1 ][ Node 2 ][ Node 3 ]  <-- Loaded into CPU L1 Cache in 1 step!

Linked List (Scattered on Heap):
[ Node 0 ] -------> [ Node 1 ] -------> [ Node 2 ]
Address 100         Address 8500        Address 410
  ^-- Cache Miss!     ^-- Cache Miss!     ^-- Cache Miss!
```

- **Array**: Sequential memory allows the CPU to fetch 64-byte blocks at once (**Cache Locality**).
- **Linked List**: Every pointer hop jumps to a random memory address, causing a **CPU Cache Miss**. A single cache miss takes hundreds of clock cycles!

---

## 6. Time & Space Complexity Summary

| Operation | Singly Linked List | Doubly Linked List | Array / Dynamic Array |
| :--- | :--- | :--- | :--- |
| **Access by Index** | $O(n)$ | $O(n)$ | **$O(1)$** |
| **Search Value** | $O(n)$ | $O(n)$ | $O(n)$ |
| **Insert / Delete at Head** | **$O(1)$** | **$O(1)$** | $O(n)$ |
| **Insert / Delete at Tail** | $O(n)$ (or $O(1)$ with tail pointer) | **$O(1)$** | **$O(1)$ Amortized** |
| **Space Overhead** | 1 pointer per item | 2 pointers per item | 0 pointer overhead |

---

## 7. Common Pitfalls & Traps

1. **Losing the Head Reference**: If you reassign `head = head.next` without saving a reference to the old head node, the previous node becomes unreachable and is garbage collected.
2. **Order of Pointer Reassignment**: When inserting node $X$ between $A$ and $B$, you must assign `X.next = B` **before** assigning `A.next = X`. Doing it in reverse overwrites the link to $B$, losing the rest of the list!
3. **Infinite Loops in Circular Lists**: A circular list has no `None` at the end. Looping `while current:` creates an infinite loop. You must loop `while current is not start_node`.

---

## 8. Check Your Understanding (University Self-Assessment)

1. **Question**: Why is deleting a node $X$ in a Singly Linked List an $O(n)$ operation if you are given a direct reference to node $X$?
   - <details><summary>Click for Answer</summary><b>Answer:</b> In a Singly Linked List, pointers only move forward. To delete node X, you must re-route its <b>predecessor's</b> pointer (<code>prev.next = X.next</code>). Finding node X's predecessor requires walking from the head node, taking O(n) time.</details>

2. **Question**: What problem does a Dummy Head (Sentinel Node) solve in linked list implementations?
   - <details><summary>Click for Answer</summary><b>Answer:</b> A Sentinel Node eliminates edge-case code for deleting or inserting at the head of a list, ensuring the first real data node always has a predecessor.</details>

3. **Question**: Why does an LRU Cache require a **Doubly Linked List** combined with a Hash Map instead of a Singly Linked List?
   - <details><summary>Click for Answer</summary><b>Answer:</b> When a cache entry is accessed, the LRU cache must move that node to the front of the list in O(1) time. A Doubly Linked List allows unlinking a node in O(1) time because the node knows both its predecessor (<code>prev</code>) and successor (<code>next</code>).</details>

---

## Related Modules
- [[01-arrays|Arrays]] — Contiguous memory alternative
- [[07-stacks-and-queues|Stacks & Queues]] — Structures commonly backed by linked lists
- [[03-hash-maps|Hash Maps]] — Using chaining linked lists to handle collisions

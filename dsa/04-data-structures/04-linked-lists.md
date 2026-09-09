# Module: Linked Lists (Pointer-Based Nodes)

Welcome to the **Linked Lists** module. Unlike [[01-arrays|Arrays]], where elements are stored side-by-side in contiguous memory, a **Linked List** stores data in scattered, independent memory blocks called **Nodes**. Each node holds a piece of data and a **Pointer** holding the memory address of the next node.

---

## Before you start

- You understand contiguous memory and why array insertion shifts elements. See [[01-arrays|arrays]].
- You are comfortable with references or pointers.

**What you will be able to do after this lesson:**

1. Explain why indexing a linked list is O(n) while an array is O(1).
2. Explain why front insertion is O(1) for a list and O(n) for an array.
3. Implement in-place reversal with three pointers.
4. State the tradeoff in one sentence without calling either structure better.

**Study route:** read the mechanism, run the lab, then attempt the independent task before opening the hint.

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

## Implementation - complete runnable example

**Runnable example:** save as `linked_lists_lab.py` and run `python3 linked_lists_lab.py`. Standard library only; writes no files. Everything is counted rather than timed, so your output will match this exactly.

```python
"""Linked lists: pointer chasing, and the exact tradeoff against arrays.

Counts hops, so the O(n) indexing cost is visible rather than asserted."""

class Node:
    __slots__ = ("value", "next")
    def __init__(self, value, nxt=None):
        self.value, self.next = value, nxt

class LinkedList:
    def __init__(self):
        self.head, self.size, self.hops = None, 0, 0

    def push_front(self, value):
        """O(1): one allocation and one pointer rewrite. No shifting."""
        self.head = Node(value, self.head)
        self.size += 1

    def push_back(self, value):
        """O(n) without a tail pointer -- you must walk to the end first."""
        node = Node(value)
        if self.head is None:
            self.head = node
        else:
            cur = self.head
            while cur.next:
                self.hops += 1
                cur = cur.next
            cur.next = node
        self.size += 1

    def at(self, index):
        """O(n): there is no address arithmetic. You walk."""
        cur = self.head
        for _ in range(index):
            if cur is None:
                raise IndexError(index)
            self.hops += 1
            cur = cur.next
        if cur is None:
            raise IndexError(index)
        return cur.value

    def insert_after(self, node, value):
        """O(1) GIVEN the node -- the operation arrays cannot do cheaply."""
        node.next = Node(value, node.next)
        self.size += 1

    def reverse(self):
        """The three-pointer dance: save next before rewiring."""
        prev, cur = None, self.head
        while cur:
            nxt = cur.next
            cur.next = prev
            prev, cur = cur, nxt
        self.head = prev

    def to_list(self):
        out, cur = [], self.head
        while cur:
            out.append(cur.value); cur = cur.next
        return out

if __name__ == "__main__":
    print("INDEXING -- the cost arrays do not pay")
    ll = LinkedList()
    for i in range(1000):
        ll.push_front(i)
    print(f"  {'index':>7s} {'pointer hops':>14s} {'array cost':>12s}")
    for i in (0, 10, 500, 999):
        ll.hops = 0
        ll.at(i)
        print(f"  {i:7d} {ll.hops:14d} {'1 (address calc)':>12s}")
    print("  -> an array computes base + i x size. A list WALKS.")
    print()

    print("INSERTION AT THE FRONT -- the cost arrays DO pay")
    print(f"  {'n':>7s} {'list (pointer writes)':>23s} {'array (elements shifted)':>26s}")
    for n in (10, 100, 1000):
        print(f"  {n:7d} {n:23d} {n*(n-1)//2:26,d}")
    print("  -> the list wins by a growing margin: O(1) vs O(n) per insert.")
    print()

    print("THE TRADE, STATED PLAINLY")
    print("  array : O(1) index, O(n) insert at front")
    print("  list  : O(n) index, O(1) insert at front (and O(1) given a node)")
    print("  neither is better. They are bets on which operation you do most.")
    print()

    print("REVERSAL -- the three-pointer dance")
    small = LinkedList()
    for v in (1, 2, 3, 4, 5):
        small.push_front(v)
    print(f"  before: {small.to_list()}")
    small.reverse()
    print(f"  after : {small.to_list()}")

    ll2 = LinkedList()
    for v in (3, 2, 1): ll2.push_front(v)
    assert ll2.to_list() == [1, 2, 3]
    ll2.hops = 0; assert ll2.at(2) == 3 and ll2.hops == 2
    ll2.hops = 0; assert ll2.at(0) == 1 and ll2.hops == 0
    ll2.reverse(); assert ll2.to_list() == [3, 2, 1]
    empty = LinkedList(); empty.reverse(); assert empty.to_list() == []
    try:
        ll2.at(99); raise SystemExit("expected IndexError")
    except IndexError:
        pass
    print()
    print("linked_lists_lab: passed")
```

Expected output:

```
INDEXING -- the cost arrays do not pay
    index   pointer hops   array cost
        0              0 1 (address calc)
       10             10 1 (address calc)
      500            500 1 (address calc)
      999            999 1 (address calc)
  -> an array computes base + i x size. A list WALKS.

INSERTION AT THE FRONT -- the cost arrays DO pay
        n   list (pointer writes)   array (elements shifted)
       10                      10                         45
      100                     100                      4,950
     1000                    1000                    499,500
  -> the list wins by a growing margin: O(1) vs O(n) per insert.

THE TRADE, STATED PLAINLY
  array : O(1) index, O(n) insert at front
  list  : O(n) index, O(1) insert at front (and O(1) given a node)
  neither is better. They are bets on which operation you do most.

REVERSAL -- the three-pointer dance
  before: [5, 4, 3, 2, 1]
  after : [1, 2, 3, 4, 5]

linked_lists_lab: passed
```

## 8. Check Your Understanding (University Self-Assessment)

1. **Question**: Why is deleting a node $X$ in a Singly Linked List an $O(n)$ operation if you are given a direct reference to node $X$?
   - <details><summary>Click for Answer</summary><b>Answer:</b> In a Singly Linked List, pointers only move forward. To delete node X, you must re-route its <b>predecessor's</b> pointer (<code>prev.next = X.next</code>). Finding node X's predecessor requires walking from the head node, taking O(n) time.</details>

2. **Question**: What problem does a Dummy Head (Sentinel Node) solve in linked list implementations?
   - <details><summary>Click for Answer</summary><b>Answer:</b> A Sentinel Node eliminates edge-case code for deleting or inserting at the head of a list, ensuring the first real data node always has a predecessor.</details>

3. **Question**: Why does an LRU Cache require a **Doubly Linked List** combined with a Hash Map instead of a Singly Linked List?
   - <details><summary>Click for Answer</summary><b>Answer:</b> When a cache entry is accessed, the LRU cache must move that node to the front of the list in O(1) time. A Doubly Linked List allows unlinking a node in O(1) time because the node knows both its predecessor (<code>prev</code>) and successor (<code>next</code>).</details>

---

## Practice - independent task

Implement `remove_nth_from_end(head, n)` in **one pass**.

- The obvious approach counts the length first, then walks again. That is two passes.
- Do it in one, using two pointers separated by `n` nodes.
- Handle: removing the head, removing the only node, and `n` larger than the list.
- Verify against a two-pass reference on lists of length 1 to 10, for every valid `n`.

**Done when:** your one-pass version agrees with the two-pass reference on every case, including removing the head.

<details><summary>Hint - open only after an attempt</summary>
Advance a lead pointer <code>n</code> steps first. Then move both pointers together until the lead reaches the end - the trailing pointer is now exactly <code>n</code> from the end.<br>
The head case is the awkward one: you need the node <em>before</em> the target, and the head has none. A <strong>dummy node</strong> placed in front of the head removes that special case entirely - the same trick as the sentinel in [[01-prefix-sum|prefix sum]].
</details>

## Before moving on

You are done with this module when you can, closed-book:

- [ ] Explain why a list must be walked to reach index i.
- [ ] Explain why front insertion is O(1) and what makes it so.
- [ ] Perform the three-pointer reversal and say why next must be saved first.
- [ ] State the array-versus-list tradeoff without declaring a winner.

**Recap:** A linked list stores elements anywhere in memory, connected by pointers. Indexing therefore costs a walk - O(n) - because there is no address arithmetic to exploit. In exchange, inserting at the front or after a known node is O(1) with no shifting. Reversal rewires each node's pointer in place using three pointers, saving the forward link before destroying it. Neither structure is better; they are opposite bets about which operation dominates.

**Next:** [[05-trees/01-trees|Trees]] - what happens when each node points to more than one other node.

## Related Modules
- [[01-arrays|Arrays]] — Contiguous memory alternative
- [[07-stacks-and-queues|Stacks & Queues]] — Structures commonly backed by linked lists
- [[03-hash-maps|Hash Maps]] — Using chaining linked lists to handle collisions

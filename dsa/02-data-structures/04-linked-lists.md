---
id: 86c17f41-0a44-4cbb-bbba-981b8bb8669a
---

# Module: Linked Lists (Pointer-Based Nodes)

Welcome to the **Linked Lists** module. Unlike [[01-arrays|Arrays]], where elements are stored side-by-side in contiguous memory, a **Linked List** stores data in scattered, independent memory blocks called **Nodes**. Each node holds a piece of data and a **Pointer** holding the memory address of the next node.

---

## Before you start
<!-- bite: 9afa2819-a704-40df-9a61-5b4c19332d00 -->

- You understand contiguous memory and why array insertion shifts elements. See [[01-arrays|arrays]].
- You are comfortable with references or pointers.

**What you will be able to do after this lesson:**

1. Explain why indexing a linked list is O(n) while an array is O(1).
2. Explain why front insertion is O(1) for a list and O(n) for an array.
3. Implement in-place reversal with three pointers.
4. State the tradeoff in one sentence without calling either structure better.

**Study route:** read the mechanism, run the lab, then attempt the independent task before opening the hint.

## 1. Why Do Linked Lists Exist? (Real-World Motivation)
<!-- bite: 5c03afe2-d75e-4f49-a5ff-0045bcde8921 -->

Imagine a physical **Scavenger Hunt / Treasure Hunt**:

```text
Clue 1 (Base Camp)   --->  Clue 2 (Under Oak Tree)  --->  Clue 3 (Inside Cave)
[ Location: Cave ]         [ Location: Lake ]             [ Treasure! ]
```

- Each clue holds a message *and* directions to where the next clue is hidden.
- If you want to add a new clue between Clue 1 and Clue 2, you don't need to move the Oak Tree or the Cave! You simply write a new sticky note and update the directions.

In computer science, this is a **Linked List**. Because nodes are connected purely by pointers, you can insert or remove nodes in **$O(1)$ Constant Time** without shifting any other items in memory.

---

## Terms used with linked lists
<!-- bite: e1fc25c8-7b78-4c2a-8abe-959b6c4b9eac -->

1. **Node**: This is a small container holding two things: one data value, and a pointer to another node. A linked list is nothing more than a chain of these. Think of a treasure-hunt clue card holding a message and telling you where the next card is.

2. **Pointer**: This is a stored memory address — a note saying "the next item lives over there". Following a pointer is how you move from one node to the next. In Python it is a reference held in a variable; in C it is a literal address.

3. **`next`**: This is the usual name for the pointer inside a node that points to the following node.

4. **Head**: This is the pointer to the very first node. It is the only way in — lose the head and the whole list becomes unreachable, because nothing else points at the start.

5. **Tail**: This is the last node in the list. Its `next` points at nothing, written `None` in Python and `NULL` in C, and that nothing is how you know you have reached the end.

6. **Traversal**: This means walking the list from the head, following `next` pointers one at a time. It is the only way to reach the middle, which is why reaching position $i$ costs $O(i)$ rather than $O(1)$.

7. **Singly linked list**: This is a list where each node points only **forwards**. You can walk from head to tail but never backwards.

8. **Doubly linked list**: This is a list where each node holds **two** pointers, one to the next node and one to the previous. It costs extra memory per node and buys backwards traversal and $O(1)$ deletion when you already hold the node.

9. **Sentinel**: This is also called a **dummy head**. It is a fake node placed before the real first one, holding no useful data. Its purpose is to remove special cases: with a sentinel there is always a node before the one you are working on, so inserting at the front is the same code as inserting anywhere else.

10. **Cycle**: This is when some node's `next` points back to an earlier node, so the chain loops forever instead of ending. Detecting one is what [[04-patterns/04-fast-slow-pointers|fast and slow pointers]] are for.

## 3. The 4 Main Variations of Linked Lists
<!-- bite: 28010003-f357-45b5-a50a-6f2dda605e35 -->

```text
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
<!-- bite: 567923ed-189a-4998-afa0-621266e96eab -->

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
<!-- bite: 0fcf3a1a-0f6f-45a8-b2f5-746a284da459 -->

On paper, linked lists seem superior for insertions ($O(1)$ vs $O(n)$). However, in modern computer hardware, **Dynamic Arrays usually outperform Linked Lists**:

```text
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
<!-- bite: cb6b8f6b-c658-4cfa-b059-c0965a3655fc -->

| Operation | Singly Linked List | Doubly Linked List | Array / Dynamic Array |
| :--- | :--- | :--- | :--- |
| **Access by Index** | $O(n)$ | $O(n)$ | **$O(1)$** |
| **Search Value** | $O(n)$ | $O(n)$ | $O(n)$ |
| **Insert / Delete at Head** | **$O(1)$** | **$O(1)$** | $O(n)$ |
| **Insert / Delete at Tail** | $O(n)$ (or $O(1)$ with tail pointer) | **$O(1)$** | **$O(1)$ Amortized** |
| **Space Overhead** | 1 pointer per item | 2 pointers per item | 0 pointer overhead |

---

## 7. Common Pitfalls & Traps
<!-- bite: 0cec5b7d-f6a5-4cf3-8067-2108da1c2b54 -->

1. **Losing the Head Reference**: If you reassign `head = head.next` without saving a reference to the old head node, the previous node becomes unreachable and is garbage collected.
2. **Order of Pointer Reassignment**: When inserting node $X$ between $A$ and $B$, you must assign `X.next = B` **before** assigning `A.next = X`. Doing it in reverse overwrites the link to $B$, losing the rest of the list!
3. **Infinite Loops in Circular Lists**: A circular list has no `None` at the end. Looping `while current:` creates an infinite loop. You must loop `while current is not start_node`.

---

## The linked list ADT
<!-- bite: a046efe2-989b-4f0e-948d-11f5aaf8d88a -->

A linked list holds items in order, like an array, but makes the **opposite trade**. Reading this beside [[01-arrays|the array ADT]] is the quickest way to see why both exist.

1. `insert_front(item)` — Adds `item` at the start. **$O(1)$** — make a node, point it at the current head, move the head. Nothing else moves. An array cannot do this without shifting every element.

2. `delete_front()` — Removes the first item. **$O(1)$**, for the same reason.

3. `insert_after(node, item)` — Adds `item` directly after a node you already hold. **$O(1)$**: two pointer assignments, whatever the list length.

4. `delete_after(node)` — Removes the node after the one you hold. **$O(1)$**.

5. `get(i)` — Returns the item at position `i`. **$O(i)$** — you must walk from the head following `i` pointers. There is no arithmetic shortcut, because the nodes are scattered in memory rather than laid out in a row.

6. `find(value)` — Returns the first node holding `value`. $O(n)$, by walking.

7. `is_empty()` and `size()` — Whether the list is empty, and how many nodes it holds. $O(1)$ if you keep a running count, $O(n)$ if you do not.

### The trade, stated plainly

An array gives you **$O(1)$ access by position** and charges **$O(n)$** for insertion and deletion in the middle.

A linked list gives you **$O(1)$ insertion and deletion** — *provided you already hold the node* — and charges **$O(n)$** for access by position.

That proviso does a lot of work and is the most commonly missed point. "Deleting from a linked list is $O(1)$" is only true once you are standing at the right node. If all you have is an index you must walk there first, and the walk is $O(i)$ — so deleting the $i$th item is $O(i)$ overall. The $O(1)$ claim is genuine when the node reference comes from somewhere else, which is exactly the situation in an LRU cache, where a hash map hands you the node directly.

### The cost the complexity table does not show

Array elements sit next to each other, so reading one pulls its neighbours into cache for free. Linked list nodes are allocated separately and may be anywhere in memory, so every `next` you follow can be a cache miss. **In practice this makes walking a linked list several times slower than scanning an array of the same length, even though both are $O(n)$.** That is much of why arrays are the default and linked lists are reached for only when their specific $O(1)$ splice genuinely matters.

## Implementation - complete runnable example
<!-- bite: 336446f1-92bd-4328-aa56-8efe004c5a3c -->

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

```text
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

## Check your understanding
<!-- bite: e102c640-2ff1-4f95-99bb-62c68d23b5c3 -->

Try each one before you open the answer.

1. <!-- q: mcq id="09c969c1" -->
   You hold a direct reference to node X in a singly linked list of n nodes. Why does deleting X still cost O(n)?

   - [x] You must change the node before X, and finding it means walking from the head
   - [ ] Every later node has to shift one place left
   - [ ] The list must be copied into a new block
   - [ ] It doesn't; it is always O(1)

   <details><summary>Answer</summary>

   Deleting X means setting `prev.next = X.next`. A singly linked node only points forwards, so the only way to find `prev` is to walk from the head. A doubly linked node stores `prev`, which makes this O(1).

   </details>

2. <!-- q: mcq id="7edca4a7" -->
   What problem does a sentinel (dummy head) node solve?

   - [ ] It makes indexing O(1)
   - [x] Every real node always has a node before it, so inserting or deleting at the front needs no special case
   - [ ] It stops cycles from forming
   - [ ] It stores the length of the list

   <details><summary>Answer</summary>

   With a fake node before the real head, the head is no longer special. The code for "delete the first node" or "insert into an empty list" is the same as for any other position.

   </details>

3. <!-- q: mcq id="646dd1bb" -->
   To insert node X between nodes A and B in a singly linked list, which order of pointer updates is safe?

   - [x] First X.next = B, then A.next = X
   - [ ] First A.next = X, then X.next = B
   - [ ] Either order works

   <details><summary>Answer</summary>

   First `X.next = B`, then `A.next = X`. If you set `A.next = X` first, the only pointer to B is overwritten and everything from B onwards is lost.

   </details>

4. <!-- q: mcq id="1646cb36" -->
   Which operations cost O(1) on a singly linked list with only a head pointer? Choose all that apply.

   - [x] Insert at the front
   - [x] Delete the front node
   - [ ] Get the item at position i
   - [x] Insert after a node you already hold

   <details><summary>Answer</summary>

   Front insert, front delete and insert-after-a-known-node are a couple of pointer changes. Getting position i means following i `next` pointers, which is O(i).

   </details>

5. <!-- q: mcq id="d45b2d57" -->
   Why does an LRU cache use a doubly linked list together with a hash map?

   - [ ] Doubly linked lists use less memory
   - [x] The hash map finds the node in O(1), and the `prev` pointer lets you unlink and move it to the front in O(1)
   - [ ] So the cache can be sorted by key
   - [ ] A singly linked list cannot hold strings

   <details><summary>Answer</summary>

   On every access the entry moves to the front. The map gives you the node directly, and because the node knows its predecessor, it can be unlinked without a walk from the head.

   </details>

6. <!-- q: open id="59fda757" -->
   Walking a linked list and scanning an array are both O(n). Why is the linked list walk usually several times slower in practice?

   <details><summary>Answer</summary>

   Array elements sit side by side, so one 64-byte cache line fetch brings in several neighbours for free. Linked list nodes are allocated separately and can be anywhere in memory, so each `next` hop can be a cache miss costing hundreds of cycles. Big-O counts steps, not the cost of each step.

   </details>

## Check your understanding: worked problems
<!-- bite: 6048fe34-c1df-4dc3-a5ab-b40459afb9d4 -->

Work each one out on paper first, then type your answer.

1. <!-- q: gap id="8996a843" answers="1;5;9;3" -->
   Fill in the gaps. Start with an empty singly linked list and run: insert_front(3), insert_front(8), insert_after(head, 5), delete_front(), insert_front(1), then insert_after(the node holding 5, 9). Reading from the head, the list is ___ → ___ → ___ → ___.

   <details><summary>Answer</summary>

   1 → 5 → 9 → 3. After the first two: 8 → 3. Insert 5 after the head: 8 → 5 → 3. Delete the front: 5 → 3. Insert 1 at the front: 1 → 5 → 3. Insert 9 after 5: 1 → 5 → 9 → 3.

   </details>

2. <!-- q: gap id="fcd1bdce" answers="20;10;30" -->
   Fill in the gaps. The list 10 → 20 → 30 → 40 is reversed in place with three pointers:

   ```python
   prev, cur = None, head
   while cur:
       nxt = cur.next
       cur.next = prev
       prev = cur
       cur = nxt
   ```

   After the loop body has run twice, the nodes reachable from `prev` are ___ → ___, and `cur` points at the node holding ___.

   <details><summary>Answer</summary>

   prev is 20 → 10, and cur is at 30. Each pass flips one arrow: the first makes 10 point to None, the second makes 20 point to 10. 30 → 40 has not been touched yet.

   </details>

3. <!-- q: exact id="31e30e52" answer="6" -->
   A singly linked list has 1,000 nodes, numbered from position 0 at the head. How many `next` pointers must you follow to reach the node at position 6?

   <details><summary>Answer</summary>

   6. You start at position 0 and each hop moves one position. Reaching position i costs i hops, where an array would need one address calculation.

   </details>

## Practice - independent task
<!-- bite: 70743164-a7df-4016-8728-726a6a3ec3fd -->

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
<!-- bite: 9c3a3e4f-2016-4417-8bf4-42f9f883836e -->

You are done with this module when you can, closed-book:

- [ ] Explain why a list must be walked to reach index i.
- [ ] Explain why front insertion is O(1) and what makes it so.
- [ ] Perform the three-pointer reversal and say why next must be saved first.
- [ ] State the array-versus-list tradeoff without declaring a winner.

**Recap:** A linked list stores elements anywhere in memory, connected by pointers. Indexing therefore costs a walk - O(n) - because there is no address arithmetic to exploit. In exchange, inserting at the front or after a known node is O(1) with no shifting. Reversal rewires each node's pointer in place using three pointers, saving the forward link before destroying it. Neither structure is better; they are opposite bets about which operation dominates.

**Next:** [[05-stacks-and-queues|Stacks and Queues]] - two structures defined by *where* you're allowed to add and remove, often built on the arrays and linked lists you now know.

## Related Modules
<!-- bite: feb561e0-1365-4eef-a46c-0d1d06848527 -->
- [[01-arrays|Arrays]] — Contiguous memory alternative
- [[05-stacks-and-queues|Stacks & Queues]] — Structures commonly backed by linked lists
- [[03-hash-maps|Hash Maps]] — Using chaining linked lists to handle collisions

# Linked Lists — Question Bank

Micro-questions over [[04-linked-lists|the linked lists module]]. Answer in a full sentence before opening the toggle. Format explained in [[01-arrays-qb|the arrays bank]].

---

## A. The object itself

**1. What is a linked list?**

<details><summary>Answer</summary>

A chain of nodes, each holding a data value and a pointer to the next node. Nothing more than that.

</details>

**2. Why do linked lists exist?**

<details><summary>Answer</summary>

To make insertion and deletion cheap. An [[01-arrays|array]] must shift elements to open a gap; a linked list just rewires two pointers, because nothing has to be adjacent to anything.

</details>

**3. Give a real-world illustration.**

<details><summary>Answer</summary>

A treasure hunt. Each clue card holds a message and tells you where the next card is. The cards can be anywhere in the city — only the chain of references matters.

</details>

**4. Draw a singly linked list.**

<details><summary>Answer</summary>

```
Head -> [ Value | Next ] -> [ Value | Next ] -> None
```

</details>

**5. What does a linked list give up compared to an array?**

<details><summary>Answer</summary>

Contiguity — and therefore random access, address arithmetic, and cache locality.

</details>

---

## B. The vocabulary

**6. What is a node?**

<details><summary>Answer</summary>

A small container holding one data value and a pointer to another node.

</details>

**7. What is a pointer?**

<details><summary>Answer</summary>

A stored memory address — a note saying "the next item lives over there". In Python it is a reference held in a variable; in C it is a literal address.

</details>

**8. What is `next`?**

<details><summary>Answer</summary>

The usual name for the pointer inside a node that points to the following node.

</details>

**9. What is the head, and why does it matter so much?**

<details><summary>Answer</summary>

The pointer to the very first node. It is the only way in — lose it and the whole list becomes unreachable, because nothing else points at the start.

</details>

**10. What is the tail, and how do you recognise it?**

<details><summary>Answer</summary>

The last node. Its `next` points at nothing — `None` in Python, `NULL` in C — and that nothing is how you know you have reached the end.

</details>

**11. What is traversal?**

<details><summary>Answer</summary>

Walking from the head following `next` pointers one at a time. It is the only way to reach the middle, which is why reaching position $i$ costs $O(i)$.

</details>

**12. What is a singly linked list?**

<details><summary>Answer</summary>

Each node points only forwards. You can walk head to tail, never backwards.

</details>

**13. What is a doubly linked list, and what does the extra pointer buy?**

<details><summary>Answer</summary>

Each node holds `prev` as well as `next`. It costs extra memory per node and buys backwards traversal and $O(1)$ deletion when you already hold the node.

</details>

**14. What is a sentinel?**

<details><summary>Answer</summary>

Also called a dummy head — a fake node placed before the real first one, holding no useful data. It removes special cases by guaranteeing there is always a node before the one you are working on.

</details>

**15. What is a cycle?**

<details><summary>Answer</summary>

When some node's `next` points back to an earlier node, so the chain loops forever instead of ending. Detecting one is what [[04-patterns/04-fast-slow-pointers|fast and slow pointers]] are for.

</details>

---

## C. The four variants

**16. Name the four main variations.**

<details><summary>Answer</summary>

Singly linked, doubly linked, circular singly linked, circular doubly linked.

</details>

**17. Which variants can delete a node you hold in $O(1)$, and why?**

<details><summary>Answer</summary>

The doubly linked ones. Deletion means rewiring the **predecessor**, and only a `prev` pointer gives you the predecessor without walking from the head.

</details>

**18. Why can a singly linked list not delete a held node in $O(1)$?**

<details><summary>Answer</summary>

You need the node *before* it to re-route around it, and a singly linked node has no way back. Finding the predecessor is an $O(n)$ walk.

</details>

**19. Give a real use for a doubly linked list.**

<details><summary>Answer</summary>

LRU caches and browser back/forward history — anything needing movement in both directions plus $O(1)$ removal from the middle.

</details>

**20. Give a real use for a circular list.**

<details><summary>Answer</summary>

Round-robin CPU schedulers and music playlists (circular singly); the Linux kernel process list, `list_head`, is circular doubly linked.

</details>

---

## D. The sentinel trick

**21. Where do 90% of linked list bugs happen?**

<details><summary>Answer</summary>

Edge cases: inserting into an empty list, deleting the head, deleting the last node.

</details>

**22. How does a sentinel eliminate them?**

<details><summary>Answer</summary>

It guarantees the list is never empty and that every real node has a predecessor, so head operations use exactly the same code as middle operations — no `if head is None` branches.

</details>

**23. In a function using a sentinel, what do you return at the end?**

<details><summary>Answer</summary>

`dummy.next` — the real head, which may have changed during the operation. Never the dummy itself, and never the original `head` variable.

</details>

---

## E. Costs

**24. Cost of access by index?**

<details><summary>Answer</summary>

$O(n)$ for both singly and doubly linked — you must walk. Arrays do it in $O(1)$.

</details>

**25. Cost of insert or delete at the head?**

<details><summary>Answer</summary>

$O(1)$ for both variants. This is what the structure is *for*; an array charges $O(n)$ for the same thing.

</details>

**26. Cost of insert or delete at the tail?**

<details><summary>Answer</summary>

Singly: $O(n)$, or $O(1)$ if you keep a tail pointer — but deletion at the tail is still $O(n)$ because you need the predecessor. Doubly: $O(1)$.

</details>

**27. Cost of searching for a value?**

<details><summary>Answer</summary>

$O(n)$ — the same as an unsorted array, and with worse constants.

</details>

**28. What is the space overhead per item?**

<details><summary>Answer</summary>

One pointer per item for singly linked, two for doubly linked, zero for an array. On a 64-bit machine that is 8 or 16 extra bytes per element, which for small values can exceed the data itself.

</details>

**29. Why is binary search useless on a sorted linked list?**

<details><summary>Answer</summary>

Binary search needs $O(1)$ access to the midpoint. Reaching the midpoint of a linked list is $O(n)$, which destroys the saving entirely.

</details>

---

## F. The ADT and the proviso

**30. List the linked list ADT.**

<details><summary>Answer</summary>

`insert_front`, `delete_front`, `insert_after(node)`, `delete_after(node)` — all $O(1)$; `get(i)` — $O(i)$; `find(value)` — $O(n)$; `is_empty()` and `size()` — $O(1)$ with a running count, $O(n)$ without.

</details>

**31. State the array/linked-list trade as two sentences.**

<details><summary>Answer</summary>

An array gives $O(1)$ access by position and charges $O(n)$ for middle insertion and deletion.
A linked list gives $O(1)$ insertion and deletion — *provided you already hold the node* — and charges $O(n)$ for access by position.

</details>

**32. What is the most commonly missed point about "$O(1)$ deletion"?**

<details><summary>Answer</summary>

The proviso. It is only true once you are standing at the right node. Given only an index you must walk there first, so deleting the $i$th item is $O(i)$ overall.

</details>

**33. Where does the node reference genuinely come from somewhere else?**

<details><summary>Answer</summary>

An **LRU cache**: a hash map maps the key straight to the node, so the delete really is $O(1)$ with no walk. That combination is the whole design.

</details>

---

## G. The hardware reality check

**34. On paper linked lists beat arrays for insertion. Why do dynamic arrays usually win in practice?**

<details><summary>Answer</summary>

Cache. Array elements sit next to each other, so one fetch brings in several; linked list nodes are scattered on the heap, so every `next` you follow can be a cache miss costing hundreds of clock cycles.

</details>

**35. Both walks are $O(n)$. What does the complexity table fail to show?**

<details><summary>Answer</summary>

The constant factor. Walking a linked list is several times slower than scanning an array of the same length, because Big-O counts operations and cannot see memory behaviour.

</details>

**36. What follows from that for everyday code?**

<details><summary>Answer</summary>

Arrays are the default. A linked list is reached for only when its specific $O(1)$ splice genuinely matters and you genuinely hold the node.

</details>

---

## H. Traps

**37. What happens if you reassign `head = head.next` without saving the old head?**

<details><summary>Answer</summary>

The previous node becomes unreachable and is garbage collected — in C, leaked. Whatever you were meant to do with it is gone.

</details>

**38. Inserting node X between A and B — what is the correct order of assignments, and why?**

<details><summary>Answer</summary>

`X.next = B` **first**, then `A.next = X`. Doing it in reverse overwrites `A.next` before you have read it, losing B and the entire rest of the list.

</details>

**39. Why does `while current:` infinite-loop on a circular list?**

<details><summary>Answer</summary>

A circular list has no `None` at the end, so the condition never fails. You must loop `while current is not start_node`.

</details>

**40. Summarise the linked list in one sentence.**

<details><summary>Answer</summary>

Order without adjacency — which buys $O(1)$ splicing at a held node and costs random access, cache locality, and a pointer's worth of memory per item.

</details>

---

## Scorecard

| Pass | Date | Got it | Close | Blank | Questions missed |
| :--- | :--- | :----- | :---- | :---- | :--------------- |
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |

---

## Related

- [[04-linked-lists|Linked Lists]] — the module
- [[01-arrays-qb|Arrays — Question Bank]] — the opposite trade
- [[04-patterns/04-fast-slow-pointers|Fast & Slow Pointers]] — cycle detection
- [[04-patterns/05-linked-list-reversal|Linked List Reversal]] — the pointer-order trap in anger

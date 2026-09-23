# Stacks and Queues — Question Bank

Micro-questions over [[07-stacks-and-queues|the stacks and queues module]]. Answer in a full sentence before opening the toggle. Format explained in [[01-arrays-qb|the arrays bank]].

---

## A. The one rule

**1. What is a collection, and what separates a stack from a queue?**

<details><summary>Answer</summary>

A collection is any structure holding a group of items. What separates them is **the single rule deciding which item comes out next**.

</details>

**2. What does LIFO stand for, and give two examples.**

<details><summary>Answer</summary>

**Last in, first out** — the most recently added item is removed first. A stack of plates; pressing undo repeatedly.

</details>

**3. What does FIFO stand for, and give two examples.**

<details><summary>Answer</summary>

**First in, first out** — the item waiting longest is removed first. A queue at a counter; a printer working through jobs.

</details>

**4. In one sentence, how do the two ADTs relate?**

<details><summary>Answer</summary>

**They are the same ADT with one rule changed**, and everything else follows from it.

</details>

---

## B. The vocabulary

**5. What are push and pop?**

<details><summary>Answer</summary>

Adding to and removing from a **stack**. Push puts the item on top; pop takes it off the top.

</details>

**6. What are enqueue and dequeue?**

<details><summary>Answer</summary>

Adding to and removing from a **queue**. Enqueue joins the back; dequeue takes from the front.

</details>

**7. What is peek, and what is it called on each?**

<details><summary>Answer</summary>

Looking at the item that would come out next **without removing it**. Often `top` on a stack and `front` on a queue.

</details>

**8. Why is peek useful?**

<details><summary>Answer</summary>

When you must decide what to do based on what is next, **before committing to taking it** — as in the iterative post-order traversal and every monotonic-stack problem.

</details>

**9. What is underflow?**

<details><summary>Answer</summary>

Trying to remove from an empty collection. Every implementation must decide what to do — raise an error or return a "nothing here" value — **and must say which**.

</details>

**10. What is overflow, and where does it apply?**

<details><summary>Answer</summary>

Trying to add to a collection with no room left. **Only applies to fixed-capacity implementations.**

</details>

**11. What is a circular buffer?**

<details><summary>Answer</summary>

Also a ring buffer — a fixed-capacity queue inside a flat array, where front and back wrap around using `%`. It **avoids ever shifting elements**, which is what keeps operations $O(1)$.

</details>

---

## C. Stacks

**12. How do you build a stack in Python, and what are the costs?**

<details><summary>Answer</summary>

A plain `list` with `.append()` — $O(1)$ amortised — and `.pop()` — $O(1)$, because both act on the **end** of the array where nothing needs shifting.

</details>

**13. Name four places stacks appear in production.**

<details><summary>Answer</summary>

The function call stack (active calls, locals, return addresses); undo/redo; balanced parentheses validation; depth-first search.

</details>

**14. What connects all four?**

<details><summary>Answer</summary>

Each needs **the most recent thing back first** — the innermost call, the last action, the last opened bracket, the deepest branch.

</details>

---

## D. Queues

**15. What is the `pop(0)` trap?**

<details><summary>Answer</summary>

`queue.pop(0)` on a Python list is $O(n)$ — it removes index 0 and **shifts every remaining item left by one**. It looks like an $O(1)$ operation and is not.

</details>

**16. What is the correct Python queue?**

<details><summary>Answer</summary>

`collections.deque`, with `.append()` to enqueue and `.popleft()` to dequeue — both genuinely $O(1)$, because it is a doubly linked structure of blocks.

</details>

**17. Why does a queue built on a plain array need a ring buffer?**

<details><summary>Answer</summary>

Because removing from the front of a contiguous array shifts everything. Wrapping the front index around with `%` moves the *index* instead of the *data*.

</details>

**18. Write the two wraparound lines.**

<details><summary>Answer</summary>

```python
self.tail = (self.tail + 1) % self.capacity   # on enqueue
self.head = (self.head + 1) % self.capacity   # on dequeue
```

</details>

**19. Why does a circular queue track `size` separately?**

<details><summary>Answer</summary>

Because `head == tail` is ambiguous — it means both **empty** and **full**. Keeping a count disambiguates it. (The alternative is deliberately wasting one slot.)

</details>

---

## E. Costs

**20. Give the cost table for all four implementations.**

<details><summary>Answer</summary>

| Structure | Insert | Delete | Peek | Space |
| :--- | :--- | :--- | :--- | :--- |
| Stack (array) | $O(1)$ amortised | $O(1)$ | $O(1)$ | $O(n)$ |
| Queue (`deque`) | $O(1)$ | $O(1)$ | $O(1)$ | $O(n)$ |
| Queue (`list.pop(0)`) | $O(1)$ | **$O(n)$** | $O(1)$ | $O(n)$ |
| Circular buffer | $O(1)$ | $O(1)$ | $O(1)$ | $O(\text{capacity})$ |

</details>

**21. Why is the stack's insert amortised rather than exact?**

<details><summary>Answer</summary>

Because it sits on a [[02-dynamic-arrays|dynamic array]], and the occasional append triggers a resize copy.

</details>

---

## F. The ADTs

**22. List the stack ADT.**

<details><summary>Answer</summary>

`push(item)`, `pop()`, `peek()`, `is_empty()`, `size()` — all $O(1)$.

</details>

**23. List the queue ADT.**

<details><summary>Answer</summary>

`enqueue(item)`, `dequeue()`, `front()`, `is_empty()`, `size()` — all $O(1)$.

</details>

**24. Do the ADTs say anything about memory or layout?**

<details><summary>Answer</summary>

No. You can build either on an array or on a [[04-linked-lists|linked list]] and the ADT does not change.

</details>

**25. What operation do both deliberately refuse, and why is that the point?**

<details><summary>Answer</summary>

**There is no `get(i)`** — no reaching into the middle. By refusing random access, they **guarantee the order things come out in**, and that guarantee is what makes them useful for reasoning.

</details>

**26. What guarantee does each buy, and what depends on it?**

<details><summary>Answer</summary>

Stack: *most recent first* — DFS, undo histories, the call stack, bracket matching. Queue: *oldest first* — BFS exploring level by level, and a fair print queue.

</details>

**27. State the choice in one sentence.**

<details><summary>Answer</summary>

**Choosing a stack or a queue is choosing a guarantee, not choosing a container.**

</details>

---

## G. Traps

**28. What causes a stack overflow?**

<details><summary>Answer</summary>

Recursive calls filling the call stack — most often infinite recursion, but also a legitimately deep traversal on a degenerate structure.

</details>

**29. What happens if you pop without checking `is_empty()`?**

<details><summary>Answer</summary>

An index error at runtime. Underflow must be handled explicitly, not assumed away.

</details>

**30. You need $O(1)$ at *both* ends. What do you use?**

<details><summary>Answer</summary>

A **deque** (double-ended queue) — which is what Python's `collections.deque` actually is, and why it serves as both stack and queue.

</details>

**31. Summarise the pair in one sentence.**

<details><summary>Answer</summary>

Two containers that refuse random access in exchange for a promise about ordering — LIFO for recency, FIFO for fairness.

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

- [[07-stacks-and-queues|Stacks and Queues]] — the module
- [[05-trees/04-traversal/01-depth-first-traversals-qb|Depth-First Traversals — Question Bank]] — the stack in use
- [[06-graphs/05-traversal/02-breadth-first-search-qb|BFS — Question Bank]] — the queue in use
- [[dsa/04-patterns/06-monotonic-stack|Monotonic Stack]] — the pattern built on peek

# Heaps & Priority Queues — Question Bank

Micro-questions over [[08-heaps|the heaps module]]. Answer in a full sentence before opening the toggle. Format explained in [[01-arrays-qb|the arrays bank]].

---

## A. The one rule

**1. What is a heap?**

<details><summary>Answer</summary>

A tree-shaped structure with one rule — **every parent is ordered relative to its children**. That rule is weaker than full sorting, and the weakness is what makes it cheap to maintain.

</details>

**2. State the heap property for a min-heap and a max-heap.**

<details><summary>Answer</summary>

Min-heap: every parent $\le$ both children. Max-heap: every parent $\ge$ both children.

</details>

**3. What does the heap property deliberately *not* say?**

<details><summary>Answer</summary>

**Anything about siblings.** Two children of the same parent are in no particular order relative to each other.

</details>

**4. What sits at the root of a min-heap, and what does it cost to find?**

<details><summary>Answer</summary>

The global minimum — and it costs **nothing**. You simply look at it.

</details>

**5. Is a heap a sorted structure?**

<details><summary>Answer</summary>

**No.** Printing a heap's array gives something that looks almost random. It maintains one relationship — parent versus child — and refuses to order siblings, **because knowing the minimum never required that work**.

</details>

---

## B. The array representation

**6. What shape must a heap be, and why is that not decoration?**

<details><summary>Answer</summary>

A **complete binary tree** — every level full except possibly the last, which fills from the left. That shape is what lets the whole tree live in a plain array **with no pointers at all**.

</details>

**7. Give the three index formulas.**

<details><summary>Answer</summary>

$$\text{parent}(i) = \left\lfloor \frac{i-1}{2} \right\rfloor, \quad \text{left}(i) = 2i+1, \quad \text{right}(i) = 2i+2$$

</details>

**8. What does the array layout save?**

<details><summary>Answer</summary>

Two pointers per node of memory, plus the cache misses — the whole structure is one contiguous block.

</details>

---

## C. The operations

**9. What is sift-up, and what does it cost?**

<details><summary>Answer</summary>

Also bubble-up — after adding an item at the bottom, compare with the parent and swap upwards until the property holds. $O(\log n)$, because the tree's height is $\log n$.

</details>

**10. What is sift-down?**

<details><summary>Answer</summary>

Also bubble-down — after removing the root, move the last item to the top and swap downwards with the **smaller** child until the property holds. Also $O(\log n)$.

</details>

**11. Give push in three steps.**

<details><summary>Answer</summary>

1. Append the new item to the end of the array (keeping the complete shape).
2. Compare with the parent; swap if it violates the property.
3. Repeat upwards until the parent is smaller, or you reach the root.

</details>

**12. Give pop in four steps.**

<details><summary>Answer</summary>

1. The extreme item is `array[0]`.
2. Replace `array[0]` with the **last** item and remove the last slot.
3. Compare the new root with its children; swap with the smaller one.
4. Repeat downwards until both children are larger, or you hit a leaf.

</details>

**13. Why does pop move the *last* item to the root rather than promoting a child?**

<details><summary>Answer</summary>

Because the tree must stay **complete**. Removing the last slot is the only removal that preserves the shape, so the array arithmetic keeps working.

</details>

**14. In a min-heap sift-down, why swap with the *smaller* child?**

<details><summary>Answer</summary>

Because the promoted child becomes the parent of the other one, and it must be $\le$ both. Swapping with the larger child would immediately violate the property on the other side.

</details>

---

## D. Heapify

**15. What is heapify?**

<details><summary>Answer</summary>

Turning an unordered array into a valid heap.

</details>

**16. What does it cost naively, and what does it cost properly?**

<details><summary>Answer</summary>

Naively — inserting one at a time — $O(n \log n)$. Properly — sifting down from the middle of the array backwards — **$O(n)$**.

</details>

**17. Give the counting argument for why it is $O(n)$.**

<details><summary>Answer</summary>

About $N/2$ elements are leaves and need **0 swaps**. $N/4$ are one level up and need at most 1. $N/8$ need at most 2, and so on:

$$\sum_{h=0}^{\log n} \frac{N}{2^{h+1}} \cdot h = O(N)$$

**Most nodes are near the bottom, where the work is cheapest.**

</details>

**18. Why does the naive version fail to get this saving?**

<details><summary>Answer</summary>

Inserting sifts **up**, and most nodes are near the bottom — which is **far** from the root. Sifting down puts the cheap direction where the many nodes are.

</details>

**19. Where do you start the bottom-up loop, and why?**

<details><summary>Answer</summary>

At index $\lfloor n/2 \rfloor - 1$ — the last non-leaf node. Everything after it is a leaf and already a valid heap of one.

</details>

---

## E. The priority queue ADT

**20. What is the difference between a priority queue and a heap?**

<details><summary>Answer</summary>

A **priority queue** is the ADT — add freely, always remove the highest priority. A **heap** is the usual implementation of it. **This is the clearest example in the folder of why ADTs and implementations are different things.**

</details>

**21. List the priority queue ADT with heap costs.**

<details><summary>Answer</summary>

`insert` $O(\log n)$; `peek_min` $O(1)$; `extract_min` $O(\log n)$; `is_empty`/`size` $O(1)$; `heapify(list)` $O(n)$; `decrease_key` $O(\log n)$.

</details>

**22. What is the catch with `decrease_key`?**

<details><summary>Answer</summary>

It needs a way to **find** the item first, which a plain heap does not provide. This is why [[06-graphs/06-algorithms/02-dijkstra|Dijkstra]] usually pushes a duplicate entry and skips stale ones instead.

</details>

**23. Compare unsorted list, sorted list and heap on the three operations.**

<details><summary>Answer</summary>

| Operation | Unsorted list | Sorted list | Heap |
| :--- | :---: | :---: | :---: |
| `insert` | $O(1)$ | $O(n)$ | $O(\log n)$ |
| `peek_min` | $O(n)$ | $O(1)$ | $O(1)$ |
| `extract_min` | $O(n)$ | $O(1)$ | $O(\log n)$ |

</details>

**24. State the heap's whole value in one sentence.**

<details><summary>Answer</summary>

**It is good at all three at once**, by maintaining exactly enough order to know the minimum and no more.

</details>

---

## F. Python's `heapq`

**25. Is Python's `heapq` a min-heap or a max-heap?**

<details><summary>Answer</summary>

Strictly a **min-heap**.

</details>

**26. What is the max-heap trick?**

<details><summary>Answer</summary>

Negate on the way in and on the way out: push `-value`, and read `-heappop(h)`.

</details>

**27. How do you peek in `heapq`?**

<details><summary>Answer</summary>

`heap[0]` — there is no `peek` function; the root is just index 0.

</details>

**28. What does `heapq.heapify(numbers)` do, and at what cost?**

<details><summary>Answer</summary>

Transforms the list **in place** into a valid heap, in $O(n)$.

</details>

---

## G. Costs and traps

**29. Give the full cost table.**

<details><summary>Answer</summary>

Peek $O(1)$; push $O(\log n)$; pop $O(\log n)$; build via heapify $O(n)$; **search for an arbitrary element $O(n)$**; space $O(n)$.

</details>

**30. Why can you not use a heap to answer "does 42 exist?"**

<details><summary>Answer</summary>

**Heaps are not search trees.** There is no ordering between siblings, so there is no branch to discard — you must scan every element. Use a [[03-hash-maps|hash map]] or a [[05-trees/03-binary-search-trees|BST]].

</details>

**31. What is the tuple comparison crash, and what is the fix?**

<details><summary>Answer</summary>

Storing `(priority, item)` raises `TypeError` when two priorities tie and `item` is unorderable. Fix: an incrementing counter tiebreaker — `(priority, counter, item)`.

</details>

**32. Building a heap from an existing array — what is the mistake?**

<details><summary>Answer</summary>

Pushing one element at a time, at $O(n \log n)$, when `heapify` does it in $O(n)$.

</details>

**33. Summarise the heap in one sentence.**

<details><summary>Answer</summary>

A complete tree in a flat array that maintains only the parent–child ordering — just enough to know the extreme in $O(1)$ and change it in $O(\log n)$, and deliberately not enough to search.

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

- [[08-heaps|Heaps & Priority Queues]] — the module
- [[05-trees/02-binary-trees-qb|Binary Trees — Question Bank]] — where the complete-tree array layout is derived
- [[06-graphs/06-algorithms/02-dijkstra-qb|Dijkstra — Question Bank]] — the heap's most important customer
- [[dsa/04-patterns/07-top-k-elements|Top K Elements]] — the pattern built on it

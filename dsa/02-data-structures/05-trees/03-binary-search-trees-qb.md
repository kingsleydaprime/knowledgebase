# Binary Search Trees — Question Bank

Micro-questions over [[03-binary-search-trees|the BST module]]. Answer in a full sentence before opening the toggle. Format explained in [[dsa/02-data-structures/01-arrays-qb|the arrays bank]].

---

## A. The invariant

**1. What is a binary search tree?**

<details><summary>Answer</summary>

A binary tree with an ordering rule — the **BST invariant** — added on top.

</details>

**2. State the BST invariant precisely.**

<details><summary>Answer</summary>

For every node $X$: all values in $X$'s **left subtree** are strictly smaller than $X$, and all values in $X$'s **right subtree** are strictly larger.

</details>

**3. What is the most common bug when checking the invariant?**

<details><summary>Answer</summary>

Only checking immediate children. The invariant applies to **entire subtrees** — a node deep inside the left subtree could still be greater than the root while every parent-child pair looks fine.

</details>

**4. How do you check the invariant correctly?**

<details><summary>Answer</summary>

Carry a `(low, high)` bound down the recursion: every node must satisfy `low < node.val < high`, with the bound narrowing as you descend. (Equivalently: check that an in-order traversal is strictly increasing.)

</details>

**5. What does an in-order traversal of a BST produce?**

<details><summary>Answer</summary>

The values in **strictly ascending order**. Left → Root → Right walks the tree in sorted order.

</details>

---

## B. Searching

**6. Describe BST search in four steps.**

<details><summary>Answer</summary>

1. Start at the root.
2. If `target == current.val`, found.
3. If `target < current.val`, go left — discard the entire right subtree.
4. Otherwise go right — discard the entire left subtree.

</details>

**7. What is BST search structurally the same as?**

<details><summary>Answer</summary>

Binary search on a sorted array — made into a structure rather than an algorithm over one.

</details>

**8. What makes each comparison worth so much?**

<details><summary>Answer</summary>

It discards *half the remaining tree*, not one element. That halving is where $O(\log n)$ comes from.

</details>

**9. What is the cost of search, stated honestly?**

<details><summary>Answer</summary>

$O(h)$ — the height. Not $O(\log n)$ unless the tree is balanced.

</details>

---

## C. The ADT

**10. List the BST ADT with costs.**

<details><summary>Answer</summary>

`insert`, `search`, `delete`, `min`, `max`, `successor` — all $O(h)$; `range(low, high)` — $O(h + k)$ for $k$ results; `in_order()` — $O(n)$.

</details>

**11. How do you find the minimum and maximum?**

<details><summary>Answer</summary>

Walk left as far as possible for the minimum, right as far as possible for the maximum. A hash map cannot do this at all without checking everything.

</details>

**12. Why is deletion the fiddliest operation?**

<details><summary>Answer</summary>

A node with two children cannot simply be removed — it must be replaced by its **in-order successor** (the smallest value in its right subtree), which is then deleted from where it was.

</details>

**13. What is `range(low, high)` and why does it matter?**

<details><summary>Answer</summary>

Returns every value between two bounds, in $O(h + k)$. **This is the operation databases are built on** — `WHERE age BETWEEN 20 AND 30`.

</details>

**14. Why are all the costs stated in $h$ and not $n$?**

<details><summary>Answer</summary>

Because the cost genuinely depends on the height, and the relationship between $h$ and $n$ is not fixed — it is decided by the shape, which is decided by the insertion order.

</details>

---

## D. Height, and why it is not guaranteed

**15. What is $h$ for a balanced tree, and what does that mean concretely?**

<details><summary>Answer</summary>

$h \approx \log_2 n$. For a million items that is about 20 comparisons.

</details>

**16. What is $h$ for a degenerate tree?**

<details><summary>Answer</summary>

$h = n$. Every operation becomes $O(n)$ and the structure is a [[04-linked-lists|linked list]] wearing a tree's clothes.

</details>

**17. What input produces a degenerate tree?**

<details><summary>Answer</summary>

Already-sorted input. Insert `1, 2, 3, 4, 5` and every value goes to the right of the last — a straight line.

</details>

**18. Why is that catastrophic rather than a curiosity?**

<details><summary>Answer</summary>

**Sorted input is the most common input there is.** The worst case is not exotic; it is the default. Which is why unbalanced BSTs are essentially never used in production.

</details>

---

## E. Self-balancing

**19. What do self-balancing trees do to keep $h$ at $\log n$?**

<details><summary>Answer</summary>

**Tree rotations** — local rearrangements that reduce height while preserving the BST invariant.

</details>

**20. What does a right rotation do?**

<details><summary>Answer</summary>

Lifts the left child into the parent's position and pushes the parent down to the right, reattaching the middle subtree. Order is preserved; height on the heavy side drops by one.

</details>

**21. What balance rule does an AVL tree enforce, and what is it best for?**

<details><summary>Answer</summary>

Height difference between left and right subtrees $\le 1$ at every node — strict. Best for read-heavy workloads where lookup speed is critical.

</details>

**22. What rule does a red-black tree enforce instead?**

<details><summary>Answer</summary>

Node colours and rules ensuring the longest path is at most $2\times$ the shortest. Looser, so it needs **fewer rotations** on insert and delete.

</details>

**23. Where are red-black trees used in the real world?**

<details><summary>Answer</summary>

Java `TreeMap`, C++ `std::map`, and the Linux kernel process scheduler.

</details>

**24. What do B-trees and B+ trees change, and why?**

<details><summary>Answer</summary>

Nodes hold **hundreds** of keys and have hundreds of children instead of two. This cuts the height to 3–4 levels for billions of records, minimising expensive **disk reads/seeks**.

</details>

**25. Where are B-trees used?**

<details><summary>Answer</summary>

Every major database index (PostgreSQL, MySQL InnoDB, SQLite) and filesystems (ext4, NTFS).

</details>

**26. Complete the complexity table: unbalanced BST vs AVL vs red-black, average and worst case.**

<details><summary>Answer</summary>

| | Average search | Worst search |
| :--- | :--- | :--- |
| Unbalanced BST | $O(\log n)$ | $O(n)$ |
| AVL | $O(\log n)$ | $O(\log n)$ |
| Red-black | $O(\log n)$ | $O(\log n)$ |

The whole value of self-balancing is in the **second column**.

</details>

---

## F. BST versus hash map

**27. Which is faster for search, insert and delete?**

<details><summary>Answer</summary>

A hash map — $O(1)$ average versus $O(\log n)$. But the tree's $O(\log n)$ is **guaranteed** and the hash map's $O(1)$ is not.

</details>

**28. Cost of min/max in each?**

<details><summary>Answer</summary>

Hash map: $O(n)$ — you must check everything. Balanced BST: $O(\log n)$.

</details>

**29. Cost of a range query in each?**

<details><summary>Answer</summary>

Hash map: **not possible** without a full scan. Balanced BST: $O(\log n + k)$.

</details>

**30. Cost of getting everything in sorted order?**

<details><summary>Answer</summary>

Hash map: $O(n \log n)$ — you have to sort it. BST: $O(n)$ — just traverse in order.

</details>

**31. Worst case of each?**

<details><summary>Answer</summary>

Hash map: $O(n)$ (collisions or an adversary). Balanced BST: $O(\log n)$.

</details>

**32. Summarise the choice in one sentence.**

<details><summary>Answer</summary>

A hash map is faster on average for the operations it supports; a balanced tree is slower but **guaranteed**, and it keeps the ordering that hashing throws away.

</details>

**33. Why is a database index a B-tree and not a hash index?**

<details><summary>Answer</summary>

Because `WHERE age BETWEEN 20 AND 30` is a range query, and a hash index simply cannot answer it.

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

- [[03-binary-search-trees|Binary Search Trees]] — the module
- [[02-binary-trees-qb|Binary Trees — Question Bank]] — the previous bank
- [[dsa/02-data-structures/03-hash-maps-qb|Hash Maps — Question Bank]] — the structure this one is contrasted with
- [[04-traversal/index|Tree Traversal]] — where in-order is done properly

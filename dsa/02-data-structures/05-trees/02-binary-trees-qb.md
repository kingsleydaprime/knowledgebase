# Binary Trees — Question Bank

Micro-questions over [[02-binary-trees|the binary trees module]]. Answer in a full sentence before opening the toggle. Format explained in [[dsa/02-data-structures/01-arrays-qb|the arrays bank]].

---

## A. The definition

**1. What is a binary tree?**

<details><summary>Answer</summary>

A tree in which every node has **at most two** children, named the left child and the right child.

</details>

**2. Is that the whole definition?**

<details><summary>Answer</summary>

Yes. There is no rule about values, no ordering requirement and no balance requirement. Ordering makes a [[03-binary-search-trees|binary search tree]]; balance is what makes it fast.

</details>

**3. Does it matter which child is left and which is right?**

<details><summary>Answer</summary>

Yes. Swapping them gives a **different tree**, even with the same values present — and an in-order traversal will show it.

</details>

**4. Write the node class.**

<details><summary>Answer</summary>

```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
```

</details>

**5. Why does shape matter so much?**

<details><summary>Answer</summary>

A tree's shape directly dictates its performance — $O(\log n)$ when short, $O(n)$ when it degenerates into a line.

</details>

---

## B. The five shapes

**6. What is a full (proper) binary tree?**

<details><summary>Answer</summary>

Every node has **either 0 or 2 children**. No node has exactly one.

</details>

**7. Where are full binary trees used?**

<details><summary>Answer</summary>

Arithmetic expression trees — operators take 2 operands, numbers take 0, so no node can have exactly one child.

</details>

**8. What is a complete binary tree?**

<details><summary>Answer</summary>

Every level completely filled except possibly the last, which is filled **strictly from left to right**.

</details>

**9. Where are complete binary trees used, and why?**

<details><summary>Answer</summary>

[[08-heaps|Heaps]] and priority queues. Because there are no gaps, a complete tree can be stored in a flat array with no pointers at all.

</details>

**10. What is a perfect binary tree?**

<details><summary>Answer</summary>

All internal nodes have 2 children **and** all leaves sit at the exact same depth.

</details>

**11. Give the node-count formula for a perfect tree of height $h$.**

<details><summary>Answer</summary>

$$n = 2^{h+1} - 1$$

For height 2: $2^3 - 1 = 7$ nodes.

</details>

**12. What is a balanced binary tree?**

<details><summary>Answer</summary>

One where the heights of the left and right subtrees of **every node** differ by at most 1.

</details>

**13. Why does balance matter?**

<details><summary>Answer</summary>

It keeps height bounded to $O(\log n)$, which is what guarantees fast searches.

</details>

**14. What is a degenerate (pathological) binary tree?**

<details><summary>Answer</summary>

Every node has only one child — the tree degrades into a straight line.

</details>

**15. Why is a degenerate tree dangerous?**

<details><summary>Answer</summary>

It is structurally identical to a [[04-linked-lists|linked list]]. Height becomes $n-1$ and every operation slows from $O(\log n)$ to $O(n)$.

</details>

---

## C. Telling the shapes apart

**16. What is the difference between full and complete?**

<details><summary>Answer</summary>

**Full** is about the *number* of children — 0 or 2. **Complete** is about *where the gaps are* — only at the end of the last level. A tree can be either one without being the other.

</details>

**17. Is a perfect tree also full and complete?**

<details><summary>Answer</summary>

Yes, both. Perfect is the strictest shape — no gaps anywhere and every internal node with two children.

</details>

**18. Give a tree that is complete but not full.**

<details><summary>Answer</summary>

```
     1
    / \
   2   3
  /
 4
```
Node 2 has exactly one child, so it is not full; the last level fills from the left, so it is complete.

</details>

**19. Give a tree that is full but not complete.**

<details><summary>Answer</summary>

```
     1
    / \
   2   3
      / \
     4   5
```
Every node has 0 or 2 children (full), but the last level's gap is on the left rather than filled left-to-right (not complete).

</details>

---

## D. The shape checks

**20. How do you test for full?**

<details><summary>Answer</summary>

A node fails if exactly one child is `None`. Recurse both sides; an empty tree is vacuously full.

```python
if (node.left is None) != (node.right is None):
    return False
```

</details>

**21. How do you test for perfect without walking every level?**

<details><summary>Answer</summary>

By the numbers: `count_nodes(root) == 2**(height(root)+1) - 1`. No other shape hits that count.

</details>

**22. What is the clean check for complete?**

<details><summary>Answer</summary>

A level-order walk that enqueues `None` children too: **once you have seen a gap, you must never see another real node.**

</details>

**23. Why is the naive balance check $O(n^2)$?**

<details><summary>Answer</summary>

It calls `height()` from inside the recursion, recomputing the same subtree heights over and over at every level.

</details>

**24. How does the one-pass balance check work?**

<details><summary>Answer</summary>

The helper returns the height **and** a sentinel (`-2`) meaning "already unbalanced below here". One traversal, $O(n)$, with failure propagating straight up.

</details>

**25. How do you test for degenerate?**

<details><summary>Answer</summary>

Every node has at most one child — fail if any node has both.

</details>

---

## E. Complete trees in an array

**26. Why can a complete tree live in a flat array?**

<details><summary>Answer</summary>

Because it has no gaps except at the end, you can number nodes level by level, left to right, and store them at exactly those positions with nothing missing in between.

</details>

**27. Give the three index formulas.**

<details><summary>Answer</summary>

Left child of $i$: $2i + 1$.
Right child of $i$: $2i + 2$.
Parent of $i$: $\lfloor (i-1)/2 \rfloor$.

</details>

**28. What two things does the array layout save?**

<details><summary>Answer</summary>

The memory of two pointers per node, and the cache misses — the whole tree sits in one contiguous block, so walking it is cache-friendly in a way a pointer-based tree never is.

</details>

**29. What is the catch?**

<details><summary>Answer</summary>

It only works while the tree stays complete. One gap in the middle and every later position shifts, breaking the arithmetic.

</details>

**30. How does a heap guarantee it stays complete?**

<details><summary>Answer</summary>

By construction: inserting always adds at the next free array slot, and removing always takes the last one.

</details>

**31. Why can a BST not be stored this way?**

<details><summary>Answer</summary>

Its shape is dictated by the order keys arrive in, not chosen. A lopsided BST would leave most of the array empty.

</details>

---

## F. Traps

**32. Does "binary tree" imply ordering?**

<details><summary>Answer</summary>

No. A heap and an expression tree are both binary and neither is sorted.

</details>

**33. What is the empty-tree height convention here, and why does it matter?**

<details><summary>Answer</summary>

`height(None) = -1`, so a single node has height 0. Some books use 0 for empty and 1 for a single node. Neither is wrong — **mixing the two produces off-by-one errors everywhere**.

</details>

**34. Are two trees with the same values the same tree?**

<details><summary>Answer</summary>

No. Left and right are not interchangeable, so mirrored positions give a genuinely different tree.

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

- [[02-binary-trees|Binary Trees]] — the module
- [[01-trees-qb|Trees — Question Bank]] — the previous bank
- [[03-binary-search-trees-qb|Binary Search Trees — Question Bank]] — the next bank
- [[08-heaps|Heaps]] — where the array layout is put to work

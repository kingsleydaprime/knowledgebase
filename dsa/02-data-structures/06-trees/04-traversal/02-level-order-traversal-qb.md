# Level-Order Traversal — Question Bank

Micro-questions over [[02-level-order-traversal|the level-order traversal module]]. Answer in a full sentence before opening the toggle. Format explained in [[dsa/02-data-structures/01-arrays-qb|the arrays bank]].

Reference tree:

```
        1
      /   \
     2     3
    / \
   4   5
```

---

## A. The idea

**1. What is level-order traversal?**

<details><summary>Answer</summary>

Visiting nodes level by level, top to bottom and left to right within each level.

</details>

**2. What is its other name?**

<details><summary>Answer</summary>

Breadth-first traversal — [[02-breadth-first-search|BFS]] applied to a tree.

</details>

**3. Level-order output on the reference tree?**

<details><summary>Answer</summary>

`[1, 2, 3, 4, 5]`

</details>

**4. Why can level-order not be written recursively (in the natural way)?**

<details><summary>Answer</summary>

Recursion uses the call stack, which is **LIFO**. Level-order needs **FIFO** — you must finish the nodes you met earliest first, and a stack gives you the latest.

</details>

**5. What data structure does it use instead?**

<details><summary>Answer</summary>

An explicit **queue** — `collections.deque` in Python, with `popleft()`.

</details>

---

## B. The mechanism

**6. Describe the loop.**

<details><summary>Answer</summary>

Start with the root in the queue. While the queue is non-empty: `popleft()` a node, visit it, and enqueue its left child then its right child if they exist.

</details>

**7. Why enqueue left before right?**

<details><summary>Answer</summary>

A queue returns things in the order they went in, so enqueuing left first makes left come out first — giving left-to-right order within each level.

</details>

**8. How do you produce output *grouped by level* rather than a flat list?**

<details><summary>Answer</summary>

At the top of each iteration, record `len(queue)` — that is exactly the number of nodes on the current level. Process that many, collecting them into one sublist, before starting the next.

</details>

**9. Why does `len(queue)` at the start of an iteration equal the level width?**

<details><summary>Answer</summary>

Because at that moment the queue holds every node of the current level and nothing else — all of the previous level has been popped, and none of the next level has been enqueued except by nodes you are about to process.

</details>

---

## C. Costs

**10. Time complexity?**

<details><summary>Answer</summary>

$O(n)$ — every node is enqueued once and dequeued once.

</details>

**11. Space complexity, and in terms of what?**

<details><summary>Answer</summary>

$O(w)$ where $w$ is the **maximum width** of the tree — the widest level, not the height.

</details>

**12. What is $w$ for a perfect binary tree?**

<details><summary>Answer</summary>

About $n/2$ — the bottom level holds half of all nodes. So BFS can use far more memory than DFS on the same tree.

</details>

**13. Compare DFS and BFS space on a balanced tree, and on a degenerate one.**

<details><summary>Answer</summary>

Balanced: DFS $O(\log n)$, BFS $O(n/2)$ — **DFS wins**.
Degenerate: DFS $O(n)$, BFS $O(1)$ (one node per level) — **BFS wins**.
They are worst on opposite shapes.

</details>

---

## D. Choosing between them

**14. When is level-order the right choice?**

<details><summary>Answer</summary>

When the answer depends on **depth** — finding the shallowest node satisfying something, shortest path in an unweighted graph, printing a tree level by level.

</details>

**15. When is depth-first the right choice?**

<details><summary>Answer</summary>

When the answer depends on a whole root-to-leaf path or on combining results from subtrees, and when memory on a wide tree matters.

</details>

**16. Why does BFS find the shallowest match and DFS does not?**

<details><summary>Answer</summary>

BFS exhausts depth $d$ entirely before touching depth $d+1$, so the first match it finds is guaranteed minimal-depth. DFS may plunge down a deep branch and find a much deeper match first.

</details>

---

## E. Traps

**17. What happens on a deep tree with recursive DFS?**

<details><summary>Answer</summary>

Stack overflow — a `RecursionError` in Python at a height around 10,000. Use an explicit iterative stack for deep trees.

</details>

**18. What happens if you use `pop()` instead of `popleft()` in BFS?**

<details><summary>Answer</summary>

The queue becomes a stack and BFS silently turns into a bizarre right-to-left DFS. It still runs and still visits every node, which is what makes the bug hard to spot.

</details>

**19. What is the in-order fallacy?**

<details><summary>Answer</summary>

Assuming in-order gives sorted output on **any** binary tree. It only does so on a **binary search tree**; on an arbitrary binary tree it guarantees nothing.

</details>

**20. Summarise level-order in one sentence.**

<details><summary>Answer</summary>

The same traversal with a queue instead of a stack — which trades $O(h)$ memory for $O(w)$ and buys the guarantee that shallower nodes come first.

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

- [[02-level-order-traversal|Level-Order Traversal]] — the module
- [[01-depth-first-traversals-qb|Depth-First Traversals — Question Bank]] — the other three orders
- [[02-breadth-first-search|Breadth-First Search]] — the same idea on a general graph

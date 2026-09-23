# Depth-First Traversals — Question Bank

Micro-questions over [[01-depth-first-traversals|the depth-first traversals module]]. Answer in a full sentence before opening the toggle. Format explained in [[dsa/02-data-structures/01-arrays-qb|the arrays bank]].

The reference tree throughout:

```
        1
      /   \
     2     3
    / \
   4   5
```

---

## A. The vocabulary

**1. What is a traversal?**

<details><summary>Answer</summary>

Visiting every node in a tree exactly once, in some definite order. The tree does not change; what changes is the **sequence** in which you see the nodes.

</details>

**2. What is a "visit"?**

<details><summary>Answer</summary>

The moment you actually do something with a node — print it, append it, compare it. The whole difference between traversal orders is *when* the visit happens relative to the recursive calls.

</details>

**3. What is depth-first traversal, and what does it use?**

<details><summary>Answer</summary>

Going as deep as possible down one branch before backing up. It uses a **stack** — either an explicit one or the call stack recursion provides.

</details>

**4. What is breadth-first traversal, and what does it use?**

<details><summary>Answer</summary>

Visiting every node at one depth before moving down. It uses a **queue**. Also called level-order.

</details>

**5. Define pre-order, in-order and post-order in terms of where the visit sits.**

<details><summary>Answer</summary>

Pre-order: node **first**, then left, then right.
In-order: left, then node, then right.
Post-order: left, then right, then node **last**.

</details>

**6. What is the call stack?**

<details><summary>Answer</summary>

The private memory the language uses to remember where it was — a record per call saying which line to return to and what the locals were. **Recursion is not magic; it is a stack you did not have to write.**

</details>

**7. What is an explicit stack, and why would you write one?**

<details><summary>Answer</summary>

A stack you create yourself, usually a list. It lets you do the same traversal without recursion — which matters because the call stack is small and fixed while a list can grow as large as memory allows.

</details>

**8. What does "iterative" mean here?**

<details><summary>Answer</summary>

Written as a loop rather than a function calling itself. Every recursive traversal has an iterative twin doing exactly the same work; the difference is only **who keeps track of where you were**.

</details>

---

## B. The three recursive orders

**9. Write pre-order recursively.**

<details><summary>Answer</summary>

```python
def preorder(node, result):
    if node is None: return
    result.append(node.val)
    preorder(node.left, result)
    preorder(node.right, result)
```

</details>

**10. What do the three recursive functions have in common?**

<details><summary>Answer</summary>

Exactly the same three lines. **The only thing that moves is where the visit line sits** — and that single difference is the entire topic.

</details>

**11. Pre-order output on the reference tree?**

<details><summary>Answer</summary>

`[1, 2, 4, 5, 3]`

</details>

**12. In-order output on the reference tree?**

<details><summary>Answer</summary>

`[4, 2, 5, 1, 3]`

</details>

**13. Post-order output on the reference tree?**

<details><summary>Answer</summary>

`[4, 5, 2, 3, 1]`

</details>

**14. What is pre-order *for*?**

<details><summary>Answer</summary>

Anything where the root must come out first — copying a tree, serialising it to a file.

</details>

**15. What is in-order *for*?**

<details><summary>Answer</summary>

Sorted output. On a [[../03-binary-search-trees|BST]] it always yields values in strictly ascending order.

</details>

**16. What is post-order *for*, and why?**

<details><summary>Answer</summary>

Anything where a parent needs results from **both** children before it can compute its own — directory sizes, expression evaluation, freeing memory in C. A node is visited only after everything beneath it.

</details>

---

## C. Going iterative

**17. Why bother writing the iterative versions at all? Two reasons.**

<details><summary>Answer</summary>

1. **Recursion has a depth limit and an explicit stack does not.** Python stops around 1,000 nested calls; a list holds millions. On a degenerate tree the recursive version crashes where the iterative one does not notice.
2. **Interviewers ask**, because iterative in-order and post-order reveal whether you understand the traversal or memorised three lines.

</details>

**18. Are the three iterative versions variations of one loop?**

<details><summary>Answer</summary>

No. Pre-order is easy, in-order needs a different skeleton, post-order needs a trick. That unevenness is the honest shape of the topic.

</details>

**19. Iterative pre-order: describe the loop.**

<details><summary>Answer</summary>

Push the root. Repeatedly pop a node, visit it, push its children — **right first**, because a stack returns the last thing pushed, so pushing right first makes left come out first.

</details>

**20. Why is iterative pre-order the easy one?**

<details><summary>Answer</summary>

The node is visited the moment you first reach it, so there is nothing to remember. A node on the stack simply means "not started yet".

</details>

**21. Why can't in-order use the same skeleton?**

<details><summary>Answer</summary>

The node must **not** be visited when you first reach it — its whole left subtree has to come out first. So you cannot finish with a node on arrival.

</details>

**22. Describe the iterative in-order loop.**

<details><summary>Answer</summary>

A `curr` pointer drills all the way down the left edge, stacking nodes as it passes. When there is no more left, pop the most recent node, visit it, and turn right.

</details>

**23. Why is the condition `while curr or stack` rather than `while stack`?**

<details><summary>Answer</summary>

There are two separate ways for work to remain: you are holding a node you have not descended into (`curr`), or nodes are parked on the stack awaiting a visit. The traversal ends only when **both** are empty.

</details>

**24. What does a node sitting on the in-order stack mean?**

<details><summary>Answer</summary>

*"I have gone past you on the way down, and I still owe you a visit."*

</details>

---

## D. Post-order, the awkward one

**25. Why is iterative post-order genuinely harder?**

<details><summary>Answer</summary>

A node is visited only after **both** subtrees are done, so on arriving back at a node from below you must know *which* child you returned from. The stack alone does not tell you that.

</details>

**26. Describe Option A (the reversal trick).**

<details><summary>Answer</summary>

Run a modified pre-order that visits `Root → Right → Left`, then reverse the final list. Reversed, that is `Left → Right → Root` — post-order.

</details>

**27. In Option A, which child is pushed first, and why is it the opposite of pre-order?**

<details><summary>Answer</summary>

**Left first**, so right is popped first, giving `Root → Right → Left` on the way in. Plain pre-order pushes right first.

</details>

**28. What is the serious catch in Option A?**

<details><summary>Answer</summary>

It produces the right **list** in the wrong **order of touching**. The nodes are actually visited root-first (`1, 3, 6, 2, 5, 4` on the lab tree); the reversal happens afterwards, to the list.

</details>

**29. When is Option A fine and when is it wrong?**

<details><summary>Answer</summary>

Fine when the work is **collecting values**. Wrong when the work **is** the visit — freeing memory, deleting nodes, closing files. You cannot reverse a `free()` that has already happened.

</details>

**30. Describe Option B.**

<details><summary>Answer</summary>

One stack plus a `last_visited` pointer. Drill left as in in-order; then **peek** at the top of the stack and ask whether its right subtree is already finished. If not, go right. If so, visit and pop.

</details>

**31. What is the key line in Option B, and what question does it ask?**

<details><summary>Answer</summary>

`last_visited != peek_node.right` — *have I already finished this node's right subtree?*

</details>

**32. How much of Option B is actually new?**

<details><summary>Answer</summary>

Almost none. It reuses the in-order skeleton exactly — same `while curr or stack`, same drill-down-left. **The only new idea is peeking instead of popping**, and popping only once the node is genuinely finished.

</details>

---

## E. Costs

**33. Time complexity of all three traversals?**

<details><summary>Answer</summary>

$O(n)$ — every node is handled a constant number of times.

</details>

**34. Space complexity, and in terms of what?**

<details><summary>Answer</summary>

$O(h)$ for the stack, where $h$ is the **height** — not $n$, and not $\log n$ unless the tree is balanced.

</details>

**35. Do the iterative versions use less memory than the recursive ones?**

<details><summary>Answer</summary>

No — the same amount, **in a place that is allowed to be much bigger**. That is the entire benefit.

</details>

**36. What is the worst-case space, and on what tree?**

<details><summary>Answer</summary>

$O(n)$, on a degenerate tree where $h = n$. That is exactly the case where the recursive version blows the call stack.

</details>

---

## F. Recall drill

**37. Given `preorder = [1,2,4,5,3]` and `inorder = [4,2,5,1,3]`, reconstruct the tree.**

<details><summary>Answer</summary>

Pre-order's first element is the root: `1`. Find `1` in in-order — everything left of it (`4,2,5`) is the left subtree, everything right (`3`) is the right. Recurse. You get the reference tree.

</details>

**38. Why is pre-order + in-order enough to reconstruct a tree, but pre-order + post-order is not?**

<details><summary>Answer</summary>

In-order is the only one that tells you **where the split is** — which nodes fall on each side of the root. Pre-order and post-order both identify the root but neither partitions the rest, so trees with single-child nodes become ambiguous.

</details>

**39. Which traversal order would you use to delete a tree, and why?**

<details><summary>Answer</summary>

**Post-order**, with a true post-order visit (Option B or recursion). You must free the children before the parent, because freeing the parent first loses the pointers to them.

</details>

**40. Summarise the topic in one sentence.**

<details><summary>Answer</summary>

Three orders are one algorithm with the visit line in three places — and going iterative just means writing down by hand the note the call stack was keeping for you.

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

- [[01-depth-first-traversals|Depth-First Traversals]] — the module
- [[02-level-order-traversal-qb|Level-Order Traversal — Question Bank]] — the breadth-first counterpart
- [[dsa/02-data-structures/07-stacks-and-queues|Stacks and Queues]] — why one order needs a stack and the other a queue

---
id: 562ce51e-f94a-4331-9dba-87b79ef261c3
---

# Module: Binary Trees (At Most Two Children)

A binary tree is a tree where each item has at most two children, called the left child and the right child. That small limit makes it easy to store and search. Many of the faster structures later in the course, like binary search trees and heaps, are binary trees with extra rules.

## Before you start
<!-- bite: f2c326fd-23a0-47a0-95b5-111129e4ca97 -->

- You know the tree vocabulary — root, parent, child, leaf, subtree, height, depth — from [[01-trees|trees]].
- You can trace a recursive function.

**After this lesson you will be able to:**

1. Define a binary tree and write the node class it is built from.
2. Name and recognise the five standard shapes: **full, complete, perfect, degenerate** and **balanced**.
3. Implement a check for each shape, and say which property each one guarantees.
4. Explain why **complete** binary trees can be stored in a flat array with no pointers.

**Study route:** read the shapes, then the implementations, then the array-storage section at the end.

---

## What a binary tree is
<!-- bite: 7b04359a-a06e-42e1-89d8-3a4d6af20bfa -->

A **binary tree** is a tree in which every node has **at most two** children. They are named the **left child** and the **right child**, and the distinction matters — swapping them gives a different tree, even with the same values present.

That is the whole definition. There is no rule about the values, no ordering requirement and no balance requirement. Those come later: ordering is what makes a [[03-binary-search-trees|binary search tree]], and balance is what makes it fast.


A **Binary Tree** is the most widely used variation of a tree. The rule is simple: **Every node can have AT MOST two children**, conventionally named `left` and `right`.

## The node
<!-- bite: c2a61513-df39-4044-898f-cbb65b2f2015 -->
```python
class TreeNode:
    """Represents a single node in a Binary Tree."""
    def __init__(self, val=0, left=None, right=None):
        self.val = val        # The value stored in this node
        self.left = left      # Reference to left child (TreeNode or None)
        self.right = right    # Reference to right child (TreeNode or None)
```

## The five shapes
<!-- bite: 5cbaea0b-cec7-48d4-87ad-b74514bee286 -->

Understanding these shapes is critical because a tree's shape directly dictates its performance ($O(\log n)$ vs $O(n)$).

#### 1. Full (Proper) Binary Tree
Every node has **either 0 or 2 children**. No node has only 1 child.
```text
       1
      / \
     2   3
    / \
   4   5
```
*Where it's used*: Arithmetic expression trees (e.g. `(4 + 5) * 3`), where operators (`+`, `*`) take 2 operands, and numbers take 0.

#### 2. Complete Binary Tree
Every level is completely filled, except possibly the last level, which is filled **strictly from left to right**.
```text
       1
      / \
     2   3
    / \  /
   4  5 6
```
*Where it's used*: **Heaps** and Priority Queues! Because there are no gaps, a complete binary tree can be stored efficiently in a flat Array without using pointers.

#### 3. Perfect Binary Tree
All internal nodes have 2 children, and **all leaves are at the exact same depth**.
```text
       1
      / \
     2   3
    / \ / \
   4  5 6  7
```
*Formula*: A perfect binary tree of height $h$ has total nodes $n = 2^{h+1} - 1$. For height 2, $n = 2^3 - 1 = 7$ nodes.

#### 4. Balanced Binary Tree
A tree where the height of the left and right subtrees of *every node* differs by at most 1.
```text
       1
      / \
     2   3
    /
   4
```
*Why it matters*: Keeps tree height bounded to $O(\log n)$, guaranteeing fast searches.

#### 5. Degenerate (Pathological) Binary Tree
Every node has only 1 child. The tree degrades into a single straight line.
```text
   1
    \
     2
      \
       3
        \
         4
```
*Why it's dangerous*: Structurally identical to a **Linked List**. Height becomes $n-1$, and operations slow down from $O(\log n)$ to $O(n)$.

---

## Implementing the shape checks
<!-- bite: e8c2f839-99de-43fc-8961-9bc9136dd904 -->

Each shape is a property you can test for. These are written to be read rather than run — there is no lab here, because each one is short enough to follow by eye, and the point is the **definition made precise**, not a measurement.

All of them assume the node class above.

### Full binary tree

A node is full if it has **either zero or two** children — never exactly one.

```python
def is_full(node):
    """Every node has 0 or 2 children, never 1."""
    if node is None:
        return True                      # an empty tree is vacuously full
    if (node.left is None) != (node.right is None):
        return False                     # exactly one child: not full
    return is_full(node.left) and is_full(node.right)
```

### Perfect binary tree

Every internal node has two children **and** every leaf sits at the same depth. The neat way to check it is by the numbers: a perfect tree of height $h$ has exactly $2^{h+1} - 1$ nodes, and no other shape does.

```python
def height(node):
    """Edges on the longest downward path. An empty tree is -1 by convention,
    so a single node comes out as 0."""
    if node is None:
        return -1
    return 1 + max(height(node.left), height(node.right))


def count_nodes(node):
    if node is None:
        return 0
    return 1 + count_nodes(node.left) + count_nodes(node.right)


def is_perfect(node):
    """A perfect tree of height h has exactly 2^(h+1) - 1 nodes."""
    h = height(node)
    return count_nodes(node) == (2 ** (h + 1)) - 1
```

### Complete binary tree

Every level is full except possibly the last, and the last fills strictly **left to right**. The clean check uses a level-order walk: once you have seen a gap, you must never see another node.

```python
from collections import deque


def is_complete(root):
    """Level-order walk. After the first missing child, everything must be missing."""
    if root is None:
        return True
    queue = deque([root])
    seen_gap = False
    while queue:
        node = queue.popleft()
        if node is None:
            seen_gap = True              # from here on, only gaps are allowed
        else:
            if seen_gap:
                return False             # a real node AFTER a gap: not complete
            queue.append(node.left)
            queue.append(node.right)
    return True
```

### Balanced binary tree

For every node, the heights of its two subtrees differ by at most one. The naive version recomputes heights and costs $O(n^2)$; this one returns the height and a sentinel together, so it is one pass and $O(n)$.

```python
def is_balanced(root):
    """True if every node's subtrees differ in height by at most 1.

    The helper returns -2 as a sentinel meaning 'already unbalanced below here',
    so the whole check is a single pass rather than height() called repeatedly."""
    def check(node):
        if node is None:
            return -1
        left = check(node.left)
        if left == -2:
            return -2
        right = check(node.right)
        if right == -2:
            return -2
        if abs(left - right) > 1:
            return -2
        return 1 + max(left, right)

    return check(root) != -2
```

### Degenerate binary tree

Every node has at most one child, so the tree is a [[04-linked-lists|linked list]] wearing a tree's clothes.

```python
def is_degenerate(node):
    """Every node has at most one child."""
    if node is None:
        return True
    if node.left is not None and node.right is not None:
        return False
    return is_degenerate(node.left) and is_degenerate(node.right)
```

## Why complete trees can live in an array
<!-- bite: b32fc05d-6502-4db7-b65e-af7620601413 -->

This is the most useful consequence of any of these shapes, and it is why [[07-heaps|heaps]] are built on complete trees.

Because a complete tree has no gaps except at the end, you can number the nodes level by level, left to right, and store them in a flat array at exactly those positions. The relationships then become arithmetic:

1. The **left child** of the node at index $i$ is at index $2i + 1$.
2. The **right child** is at index $2i + 2$.
3. The **parent** is at index $\lfloor (i-1)/2 \rfloor$.

```text
        A(0)                array:  [A, B, C, D, E, F]
       /    \               index:   0  1  2  3  4  5
    B(1)    C(2)
   /   \    /               left child of B (index 1) is at 2(1)+1 = 3 -> D
 D(3) E(4) F(5)             parent of E (index 4) is at (4-1)//2 = 1 -> B
```

**No pointers are stored at all.** That saves the memory two references per node would cost, and it puts the whole tree in one contiguous block, so walking it is cache-friendly in a way a pointer-based tree never is.

The catch is that it only works while the tree stays complete. Put a gap in the middle and the arithmetic breaks, because every later position shifts. That is exactly why a heap keeps itself complete by construction — inserting always adds at the next free array slot and removing always takes the last one — while a binary search tree, whose shape is dictated by the order keys arrive in, cannot be stored this way without wasting most of the array.

## Common pitfalls and traps
<!-- bite: bc3f7f72-616a-4831-884e-2d1aaad6e7d2 -->

- **Confusing full with complete.** Full is about the *number* of children — 0 or 2. Complete is about *where the gaps are* — only at the end of the last level. A tree can be either one without being the other.
- **Assuming "binary tree" implies ordering.** It does not. Ordering is the extra rule that makes a [[03-binary-search-trees|binary search tree]]. A heap and an expression tree are both binary and neither is sorted.
- **Treating left and right as interchangeable.** They are not. Two trees holding the same values in mirrored positions are different trees, and an in-order traversal will show it.
- **Using the naive balance check.** Calling `height()` from inside a recursive balance check recomputes the same subtree heights over and over, costing $O(n^2)$. The sentinel version above is $O(n)$.
- **Forgetting the empty-tree convention.** Here `height(None)` is $-1$, so a single node has height $0$. Some books use $0$ for empty and $1$ for a single node. Neither is wrong, but mixing the two produces off-by-one errors everywhere.

## Check your understanding
<!-- bite: 8f6ae170-7459-409e-933c-1540651e1c0a -->

Try each one before you open the answer.

1. <!-- q: exact id="87e2d9ad" answer="15" -->
   How many nodes does a perfect binary tree of height 3 have? (A single node has height 0.)

   <details><summary>Answer</summary>

   15. A perfect tree of height h has 2^(h+1) − 1 nodes, and 2⁴ − 1 = 15: 1 + 2 + 4 + 8 across the four levels.

   </details>

2. <!-- q: gap id="8b9a99f9" answers="yes;no" -->
   Fill in the gaps with yes or no. Is every perfect binary tree also complete? ___. Is every complete binary tree also perfect? ___.

   <details><summary>Answer</summary>

   Yes, then no. A perfect tree has every level full, which meets the complete rule. A complete tree may have a partly filled last level, which a perfect tree may not.

   </details>

3. <!-- q: mcq id="93c0bbb1" -->
   A binary tree has root 1 with children 2 and 3. Node 3 has children 6 and 7. Nodes 2, 6 and 7 have no children. Which shapes does it have? Choose all that apply.

   - [x] Full
   - [ ] Complete
   - [ ] Perfect
   - [x] Balanced

   <details><summary>Answer</summary>

   Full (every node has 0 or 2 children) and balanced (subtree heights differ by at most 1 everywhere). It is not complete: the last level has nodes under 3 while the left side, under 2, is empty.

   </details>

4. <!-- q: mcq id="1dba6473" -->
   Why can a heap be stored in a flat array with no pointers, while a general binary search tree usually cannot?

   - [ ] Heaps hold only numbers
   - [x] A heap is always kept complete, so there are no gaps and index arithmetic finds every child and parent
   - [ ] Binary search trees are too large for arrays
   - [ ] Heaps are sorted

   <details><summary>Answer</summary>

   A heap always adds at the next free slot and removes from the last one, so it stays complete. A binary search tree's shape follows the order keys arrive in, so gaps appear anywhere and most of the array would sit empty.

   </details>

5. <!-- q: mcq id="19e0e307" -->
   Keys 1, 2, 3, 4, 5 are inserted in that order into a binary search tree, so each new key becomes the right child of the last. What shape does it have, and what does that cost?

   - [ ] Perfect, so searches cost O(log n)
   - [x] Degenerate, so searches cost O(n), like a linked list
   - [ ] Complete, so it fits in an array
   - [ ] Full, so every node has two children

   <details><summary>Answer</summary>

   Every node has only one child, so the tree is a straight line of height n − 1. Searching it is walking a linked list, O(n).

   </details>

6. <!-- q: open id="e2910e6b" -->
   What is the difference between a full binary tree and a complete binary tree?

   <details><summary>Answer</summary>

   Full is about how many children each node has: always 0 or 2, never 1. Complete is about where the gaps are: every level is filled except possibly the last, which fills from the left. A tree can be either without being the other.

   </details>

## Check your understanding: worked problems
<!-- bite: 9ae16f14-1f1e-4e96-b22a-2669a7ce07bb -->

Work each one out on paper first, then type your answer.

1. <!-- q: gap id="95682cc8" answers="27;28;6" -->
   Fill in the gaps. A complete binary tree is stored in an array starting at index 0. The node at index 13 has its left child at index ___, its right child at index ___, and its parent at index ___.

   <details><summary>Answer</summary>

   Left child 2(13) + 1 = 27, right child 2(13) + 2 = 28, parent ⌊(13 − 1)/2⌋ = 6.

   </details>

2. <!-- q: gap id="197ea624" answers="D;F;G" -->
   Fill in the gaps. A complete binary tree is stored in the array [A, B, C, D, E, F, G, H, I, J] (A at index 0). The parent of I is ___. The children of C are ___ and ___.

   <details><summary>Answer</summary>

   I is at index 8, so its parent is at ⌊7/2⌋ = 3, which is D. C is at index 2, so its children are at 5 and 6: F and G.

   </details>

3. <!-- q: exact id="0eb54ae4" answer="31" -->
   How many nodes does a perfect binary tree of height 4 have? (A single node has height 0.)

   <details><summary>Answer</summary>

   31. 2^(4+1) − 1 = 32 − 1 = 31, which is 1 + 2 + 4 + 8 + 16 across five levels.

   </details>

4. <!-- q: gap id="601d043f" answers="4;19" -->
   Fill in the gaps. A binary tree holds 20 nodes. Its smallest possible height is ___ (when it is as bushy as possible) and its largest possible height is ___ (when it is degenerate). A single node has height 0.

   <details><summary>Answer</summary>

   4 and 19. A perfect tree of height 3 holds only 15 nodes, so 20 nodes need height 4 (⌊log₂ 20⌋ = 4). A degenerate tree is a straight line of 20 nodes with 19 edges.

   </details>

## Before moving on
<!-- bite: 43fd0d9f-5352-4715-b88d-a57a6e22d415 -->

You can define a binary tree, name and check all five shapes, and explain array storage.

**Recap:** a binary tree allows at most two children, named left and right, and which is which matters; **full** means 0 or 2 children everywhere; **perfect** means full *and* every leaf at the same depth, with exactly $2^{h+1}-1$ nodes; **complete** means every level full except the last, which fills left to right; **balanced** means subtree heights differ by at most one at every node; **degenerate** means at most one child everywhere, which is a linked list. A complete tree stores in a flat array with children at $2i+1$ and $2i+2$ and parent at $\lfloor (i-1)/2 \rfloor$.

**Next:** [[03-binary-search-trees|Binary Search Trees]] — what happens when you add an ordering rule.

## Related
<!-- bite: b7ab2615-f836-46f8-9395-1e5afdac2e86 -->

- [[01-trees|Trees]] — the vocabulary, and the other kinds of tree
- [[03-binary-search-trees|Binary Search Trees]] — the next lesson
- [[07-heaps|Heaps]] — built on a complete binary tree, stored in an array
- [[04-traversal/index|Traversal]] — how to visit every node

## About this lesson
<!-- bite: 61dea08b-4bd5-4164-bd47-6dd7ca96f1e2 -->

**Level:** Intermediate. **Covers:** the tree this course is built on, and the five shapes worth naming.

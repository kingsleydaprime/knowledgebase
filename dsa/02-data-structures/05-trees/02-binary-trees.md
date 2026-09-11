# Module: Binary Trees (At Most Two Children)

**[Intermediate]** — the tree this course is built on, and the five shapes worth naming.

## Before you start

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

A **binary tree** is a tree in which every node has **at most two** children. They are named the **left child** and the **right child**, and the distinction matters — swapping them gives a different tree, even with the same values present.

That is the whole definition. There is no rule about the values, no ordering requirement and no balance requirement. Those come later: ordering is what makes a [[03-binary-search-trees|binary search tree]], and balance is what makes it fast.


A **Binary Tree** is the most widely used variation of a tree. The rule is simple: **Every node can have AT MOST two children**, conventionally named `left` and `right`.

## The node
```python
class TreeNode:
    """Represents a single node in a Binary Tree."""
    def __init__(self, val=0, left=None, right=None):
        self.val = val        # The value stored in this node
        self.left = left      # Reference to left child (TreeNode or None)
        self.right = right    # Reference to right child (TreeNode or None)
```

## The five shapes

Understanding these shapes is critical because a tree's shape directly dictates its performance ($O(\log n)$ vs $O(n)$).

#### 1. Full (Proper) Binary Tree
Every node has **either 0 or 2 children**. No node has only 1 child.
```
       1
      / \
     2   3
    / \
   4   5
```
*Where it's used*: Arithmetic expression trees (e.g. `(4 + 5) * 3`), where operators (`+`, `*`) take 2 operands, and numbers take 0.

#### 2. Complete Binary Tree
Every level is completely filled, except possibly the last level, which is filled **strictly from left to right**.
```
       1
      / \
     2   3
    / \  /
   4  5 6
```
*Where it's used*: **Heaps** and Priority Queues! Because there are no gaps, a complete binary tree can be stored efficiently in a flat Array without using pointers.

#### 3. Perfect Binary Tree
All internal nodes have 2 children, and **all leaves are at the exact same depth**.
```
       1
      / \
     2   3
    / \ / \
   4  5 6  7
```
*Formula*: A perfect binary tree of height $h$ has total nodes $n = 2^{h+1} - 1$. For height 2, $n = 2^3 - 1 = 7$ nodes.

#### 4. Balanced Binary Tree
A tree where the height of the left and right subtrees of *every node* differs by at most 1.
```
       1
      / \
     2   3
    /
   4
```
*Why it matters*: Keeps tree height bounded to $O(\log n)$, guaranteeing fast searches.

#### 5. Degenerate (Pathological) Binary Tree
Every node has only 1 child. The tree degrades into a single straight line.
```
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

This is the most useful consequence of any of these shapes, and it is why [[08-heaps|heaps]] are built on complete trees.

Because a complete tree has no gaps except at the end, you can number the nodes level by level, left to right, and store them in a flat array at exactly those positions. The relationships then become arithmetic:

1. The **left child** of the node at index $i$ is at index $2i + 1$.
2. The **right child** is at index $2i + 2$.
3. The **parent** is at index $\lfloor (i-1)/2 \rfloor$.

```
        A(0)                array:  [A, B, C, D, E, F]
       /    \               index:   0  1  2  3  4  5
    B(1)    C(2)
   /   \    /               left child of B (index 1) is at 2(1)+1 = 3 -> D
 D(3) E(4) F(5)             parent of E (index 4) is at (4-1)//2 = 1 -> B
```

**No pointers are stored at all.** That saves the memory two references per node would cost, and it puts the whole tree in one contiguous block, so walking it is cache-friendly in a way a pointer-based tree never is.

The catch is that it only works while the tree stays complete. Put a gap in the middle and the arithmetic breaks, because every later position shifts. That is exactly why a heap keeps itself complete by construction — inserting always adds at the next free array slot and removing always takes the last one — while a binary search tree, whose shape is dictated by the order keys arrive in, cannot be stored this way without wasting most of the array.

## Common pitfalls and traps

- **Confusing full with complete.** Full is about the *number* of children — 0 or 2. Complete is about *where the gaps are* — only at the end of the last level. A tree can be either one without being the other.
- **Assuming "binary tree" implies ordering.** It does not. Ordering is the extra rule that makes a [[03-binary-search-trees|binary search tree]]. A heap and an expression tree are both binary and neither is sorted.
- **Treating left and right as interchangeable.** They are not. Two trees holding the same values in mirrored positions are different trees, and an in-order traversal will show it.
- **Using the naive balance check.** Calling `height()` from inside a recursive balance check recomputes the same subtree heights over and over, costing $O(n^2)$. The sentinel version above is $O(n)$.
- **Forgetting the empty-tree convention.** Here `height(None)` is $-1$, so a single node has height $0$. Some books use $0$ for empty and $1$ for a single node. Neither is wrong, but mixing the two produces off-by-one errors everywhere.

## Check your understanding

1. How many nodes does a perfect binary tree of height 3 have?
2. Is a perfect tree always complete? Is a complete tree always perfect?
3. Give a tree that is full but not complete.
4. Why can a heap be stored in an array, while a general binary search tree usually cannot?
5. A node sits at index 10 in an array-stored complete tree. Where are its children and its parent?

<details><summary>Answers — open only after an attempt</summary>

1. $2^{3+1} - 1 = 15$ nodes.
2. **Yes** to the first: a perfect tree has every level full, which satisfies completeness. **No** to the second: a complete tree may have a partly-filled last level, which a perfect tree may not.
3. A root with two children, where the left child has two children of its own and the right child has none. Every node has 0 or 2 children, so it is full. But the last level has nodes on the left and nothing under the right child while the level above is not full, so it is not complete.
4. Because a heap is kept **complete** by construction — insertions go at the next free array slot and removals take the last one, so there are never gaps in the middle. A binary search tree's shape is dictated by the order its keys arrive in, so gaps appear in arbitrary places and the index arithmetic would leave most of the array empty.
5. Children at $2(10)+1 = 21$ and $2(10)+2 = 22$. Parent at $\lfloor (10-1)/2 \rfloor = \lfloor 4.5 \rfloor = 4$.
</details>

## Before moving on

You can define a binary tree, name and check all five shapes, and explain array storage.

**Recap:** a binary tree allows at most two children, named left and right, and which is which matters; **full** means 0 or 2 children everywhere; **perfect** means full *and* every leaf at the same depth, with exactly $2^{h+1}-1$ nodes; **complete** means every level full except the last, which fills left to right; **balanced** means subtree heights differ by at most one at every node; **degenerate** means at most one child everywhere, which is a linked list. A complete tree stores in a flat array with children at $2i+1$ and $2i+2$ and parent at $\lfloor (i-1)/2 \rfloor$.

**Next:** [[03-binary-search-trees|Binary Search Trees]] — what happens when you add an ordering rule.

## Related

- [[01-trees|Trees]] — the vocabulary, and the other kinds of tree
- [[03-binary-search-trees|Binary Search Trees]] — the next lesson
- [[08-heaps|Heaps]] — built on a complete binary tree, stored in an array
- [[04-traversal/index|Traversal]] — how to visit every node

# Trees

A tree is a hierarchical structure: one root node, and every other node has exactly one parent, forming branches with no cycles. It's what you get when you take a [[04-linked-lists|linked list]] and let each node point to more than one "next" — a linked list is really just a tree where every node has at most one child.

## Terminology

- **Root** — the top node, no parent.
- **Parent / child** — direct connection one level apart.
- **Leaf** — a node with no children.
- **Height** of a node — the number of edges on the longest path down to a leaf.
- **Depth** of a node — the number of edges from the root down to that node.
- **Subtree** — any node plus all its descendants, which is itself a valid tree (this is why almost every tree algorithm is naturally recursive).

## Binary trees

The most common special case: every node has **at most two children**, conventionally called `left` and `right`.

```python
class TreeNode:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None
```

```
           8
         /   \
        3     10
       / \      \
      1   6      14
         / \     /
        4   7  13
```

## Binary Search Trees (BSTs)

A binary tree with one extra rule: for every node, everything in its left subtree is smaller, everything in its right subtree is larger. That single invariant is what makes search fast — at each node you know which half to discard, same idea as [[05-searching|binary search]] on a sorted array, just expressed as a pointer structure instead of an index range.

```python
def bst_search(node, target):
    if node is None or node.value == target:
        return node
    if target < node.value:
        return bst_search(node.left, target)
    return bst_search(node.right, target)
```

## Complexity — and the catch

| Operation | Balanced BST | Skewed (worst case) |
|---|---|---|
| Search | O(log n) | O(n) |
| Insert | O(log n) | O(n) |
| Delete | O(log n) | O(n) |

The O(log n) figure assumes the tree is roughly **balanced** — height proportional to log n. If you insert already-sorted data into a plain BST one at a time, it degenerates into what's structurally a linked list (every node has only a right child, say), and every operation becomes O(n). This is exactly why self-balancing trees exist (AVL trees, Red-Black trees) — they perform extra rotation work on insert/delete specifically to keep height at O(log n) no matter what order data arrives in. Worth knowing they exist; the rebalancing mechanics themselves are a deeper rabbit hole than this note needs.

## Traversal

Visiting every node in a tree is its own topic with several standard orders (preorder, inorder, postorder, level-order) — covered in [[02-traversal|traversal]] since the same idea generalizes to graphs too.

## Gotchas

- **"Balanced" is not automatic.** A plain BST with no rebalancing logic can silently become O(n) if you're unlucky (or unlucky input, e.g. sorted data) about insertion order.
- Recursive tree code is natural but has a real cost: very deep trees (or a degenerate, list-like tree) can blow the call stack — something to watch for on unbalanced or adversarial input.
- Inorder traversal of a BST always yields values in sorted order — a fact that's easy to forget but shows up constantly as the "trick" in tree problems.
- Don't confuse a **complete** binary tree (all levels full except possibly the last, filled left to right — this is the shape a heap is built on) with a **balanced** binary tree (height is just bounded at O(log n)) — every complete tree is balanced, but not every balanced tree is complete.

## Related
- [[02-traversal|traversal]]
- [[05-searching|searching]] — binary search is the array version of what a BST does with pointers
- [[06-graphs|graphs]] — a tree is a connected, acyclic graph

# Lowest Common Ancestor of a BST

**LeetCode 235** · Trees · concept: [[01-trees|trees]]

## Problem

In a **binary search tree**, find the lowest common ancestor (LCA) of two nodes `p` and `q`.

## Approach — walk down using the BST ordering (optimal)

The BST property makes this easy: at each node, if **both** `p` and `q` are greater, the LCA is in the right subtree; if both are smaller, go left. The moment they **split** (one on each side, or one *is* the current node), the current node is the LCA.

```python
def lowestCommonAncestor(root, p, q):
    node = root
    while node:
        if p.val > node.val and q.val > node.val:
            node = node.right           # both larger -> go right
        elif p.val < node.val and q.val < node.val:
            node = node.left            # both smaller -> go left
        else:
            return node                 # split point (or equals node) = LCA
```

**Time O(h), space O(1)** — a single root-to-LCA descent, no recursion needed.

## Why the split point is the LCA

If `p` and `q` fall on opposite sides of a node (or one equals it), that node is the deepest node with both in its subtree — any deeper and you'd lose one of them. The BST ordering tells you which way to descend without exploring subtrees. (For a general binary tree with no ordering, LCA needs a full DFS instead — a harder O(n) problem.)

## Key insight

**In a BST, comparisons replace search — the ordering tells you which direction each target lies.** LCA reduces to "descend until the paths to `p` and `q` diverge," achievable in O(h) with O(1) space precisely because a BST is sorted by structure.

## Related
- concept: [[01-trees|trees]] (BST property)
- prev: [[051-subtree-of-another-tree|Subtree of Another Tree]] · next: [[053-binary-tree-level-order-traversal|Binary Tree Level Order Traversal]]

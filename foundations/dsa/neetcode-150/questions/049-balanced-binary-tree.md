# Balanced Binary Tree

**LeetCode 110** · Trees · concept: [[11-dfs-pattern|dfs-pattern]]

## Problem

Return `true` if the tree is **height-balanced** — for every node, the heights of its two subtrees differ by at most 1.

## Approach — height DFS that signals imbalance with −1 (optimal)

The naive version calls a separate `height()` at every node → O(n²). The trick: make one DFS return the height **or** a sentinel `−1` meaning "a subtree below is already unbalanced," short-circuiting upward.

```python
def isBalanced(root):
    def height(node):
        if not node:
            return 0
        l = height(node.left)
        if l == -1: return -1                 # left subtree unbalanced -> propagate
        r = height(node.right)
        if r == -1: return -1
        if abs(l - r) > 1:
            return -1                         # imbalance detected here
        return 1 + max(l, r)                  # balanced -> normal height
    return height(root) != -1
```

**Time O(n), space O(h).**

## Why the −1 sentinel matters

Computing height and checking balance in the *same* pass — and using `−1` to abort early — turns O(n²) into O(n). Each node is visited once; the moment any subtree is unbalanced, `−1` rides all the way to the root without further work. Overloading the return value (height *or* failure flag) is the key idea.

## Key insight

**Merge the check into the aggregation, and use a sentinel return to short-circuit.** Same dual-purpose DFS as [[048-diameter-of-binary-tree|Diameter]], but here the "extra" carried upward is a validity flag rather than a running max.

## Related
- concept: [[11-dfs-pattern|dfs-pattern]], [[01-trees|trees]]
- prev: [[048-diameter-of-binary-tree|Diameter of Binary Tree]] · next: [[050-same-tree|Same Tree]]

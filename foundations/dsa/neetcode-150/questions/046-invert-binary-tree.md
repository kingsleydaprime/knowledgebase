# Invert Binary Tree

**LeetCode 226** · Trees · concept: [[01-trees|trees]]

## Problem

Invert a binary tree — mirror it so every node's left and right children swap.

```
    4              4
  2   7    ->    7   2
 1 3 6 9        9 6 3 1
```

## Approach — recursive swap (optimal)

Swap the current node's children, then recurse into both. The whole solution is three lines because the tree's structure *is* the recursion.

```python
def invertTree(root):
    if not root:
        return None
    root.left, root.right = invertTree(root.right), invertTree(root.left)
    return root
```

**Time O(n)** (visit each node once), **space O(h)** for the recursion stack (h = height; O(log n) balanced, O(n) skewed).

An iterative BFS/DFS with a queue/stack does the same, swapping children as you pop — useful if recursion depth is a concern.

## Key insight

**Most binary-tree problems are "do something at this node, then recurse into both subtrees."** Invert is the minimal example of that shape — the base case (`None`) plus a per-node action plus two recursive calls. Internalize this skeleton; nearly every tree problem below reuses it.

## Related
- concept: [[01-trees|trees]], [[02-dfs|dfs]]
- next: [[047-maximum-depth-of-binary-tree|Maximum Depth of Binary Tree]]

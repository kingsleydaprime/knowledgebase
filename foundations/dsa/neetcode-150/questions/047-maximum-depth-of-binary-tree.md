# Maximum Depth of Binary Tree

**LeetCode 104** · Trees · concept: [[01-trees|trees]]

## Problem

Return the maximum depth (number of nodes on the longest root-to-leaf path).

```
    3
  9   20        -> 3
     15  7
```

## Approach — recursion (optimal)

A tree's depth is 1 (for the root) plus the depth of its deeper subtree.

```python
def maxDepth(root):
    if not root:
        return 0
    return 1 + max(maxDepth(root.left), maxDepth(root.right))
```

**Time O(n), space O(h).**

## Alternatives

- **Iterative DFS** with an explicit stack of `(node, depth)` pairs.
- **BFS level-order** ([[03-bfs|BFS]]): count the levels as you drain the queue one level at a time — the depth is the number of levels.

All three are O(n); the recursion is just the shortest.

## Key insight

**Tree height obeys `height(node) = 1 + max(height(children))`** — a bottom-up aggregation. This "combine children's results into the parent's answer" recursion is the backbone of Diameter, Balanced, and Max Path Sum; depth is its simplest instance.

## Related
- concept: [[01-trees|trees]], [[03-bfs|bfs]]
- prev: [[046-invert-binary-tree|Invert Binary Tree]] · next: [[048-diameter-of-binary-tree|Diameter of Binary Tree]]

# Count Good Nodes in Binary Tree

**LeetCode 1448** · Trees · concept: [[11-dfs-pattern|dfs-pattern]]

## Problem

A node is **good** if no node on the path from the root to it has a greater value. Count the good nodes.

```
    3
  1   4        good: 3, 4, 5, 3  ->  4
 3   1 5
```

## Approach — DFS carrying the max-on-path (optimal)

Pass the **maximum value seen so far on the path** down the recursion. A node is good iff its value ≥ that max; then recurse with an updated max.

```python
def goodNodes(root):
    def dfs(node, path_max):
        if not node:
            return 0
        good = 1 if node.val >= path_max else 0
        new_max = max(path_max, node.val)
        return good + dfs(node.left, new_max) + dfs(node.right, new_max)
    return dfs(root, root.val)
```

**Time O(n), space O(h).**

## Top-down state vs bottom-up results

Unlike Diameter/Balanced (which return values **up**), this threads state **down**: each node's "goodness" depends on the ancestors above it, so the running max flows from parent to child. The count then bubbles back up as a sum. Recognizing which direction the needed information flows — down from ancestors, or up from descendants — is the core DFS design decision.

## Key insight

**When a node's answer depends on its ancestors, pass an accumulator *down* the recursion.** Here it's the path maximum; the same top-down-state pattern handles path sums, depth tracking, and "valid range" checks like [[056-validate-binary-search-tree|Validate BST]].

## Related
- concept: [[11-dfs-pattern|dfs-pattern]]
- prev: [[054-binary-tree-right-side-view|Right Side View]] · next: [[056-validate-binary-search-tree|Validate Binary Search Tree]]

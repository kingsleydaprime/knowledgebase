# Diameter of Binary Tree

**LeetCode 543** · Trees · concept: [[11-dfs-pattern|dfs-pattern]]

## Problem

Return the length (in edges) of the longest path between **any** two nodes. The path need not pass through the root.

## The insight — height computation with a side effect

At each node, the longest path *through* that node is `leftHeight + rightHeight` (edges). So compute heights bottom-up as usual, but while doing it, update a global best with `left + right` at every node. The answer is the max over all nodes.

```python
def diameterOfBinaryTree(root):
    best = 0
    def height(node):
        nonlocal best
        if not node:
            return 0
        l = height(node.left)
        r = height(node.right)
        best = max(best, l + r)          # longest path through this node (edges)
        return 1 + max(l, r)             # height returned to the parent
    height(root)
    return best
```

**Time O(n), space O(h).**

## Why one traversal suffices

The diameter passes through *some* node as its highest point; at that node it equals left height + right height. By checking `l + r` at **every** node during a single height computation, you consider every candidate apex. Computing height separately per node would be O(n²) — folding the update into the height recursion is the optimization.

## Key insight

**"Longest/best path in a tree" → one DFS that returns a value upward *and* updates a global answer.** The function returns the *height/arm* usable by the parent, while a `nonlocal` best captures the *through-node* quantity. This dual-purpose DFS is the pattern for Balanced, Max Path Sum, and the whole [[11-dfs-pattern|DFS-on-trees]] family.

## Related
- concept: [[11-dfs-pattern|dfs-pattern]], [[01-trees|trees]]
- prev: [[047-maximum-depth-of-binary-tree|Maximum Depth]] · next: [[049-balanced-binary-tree|Balanced Binary Tree]]

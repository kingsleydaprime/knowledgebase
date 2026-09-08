# Validate Binary Search Tree

**LeetCode 98** · Trees · concept: [[11-dfs-pattern|dfs-pattern]]

## Problem

Return `true` if a binary tree is a valid BST: every node's value is greater than **all** nodes in its left subtree and less than **all** in its right subtree.

## The trap

Checking only `left.val < node.val < right.val` locally is **wrong** — it misses violations deeper down. A node in the far-right subtree of a left child could still exceed the ancestor it must stay below. Validity is a *range* constraint inherited from all ancestors, not a parent-child comparison.

## Approach — DFS carrying (min, max) bounds (optimal)

Thread an open interval `(low, high)` down the tree. Each node must lie strictly inside it; going left tightens the upper bound to the node's value, going right tightens the lower bound.

```python
def isValidBST(root):
    def valid(node, low, high):
        if not node:
            return True
        if not (low < node.val < high):
            return False
        return (valid(node.left, low, node.val) and       # left: cap the max at node.val
                valid(node.right, node.val, high))         # right: raise the min to node.val
    return valid(root, float("-inf"), float("inf"))
```

**Time O(n), space O(h).**

## Alternative — in-order traversal must be sorted

A BST's [[02-traversal|in-order traversal]] yields strictly increasing values. So walk in-order and verify each value exceeds the previous — an equally valid O(n) approach, and a neat use of the in-order property.

## Key insight

**BST validity is a range constraint that propagates from ancestors — carry (min, max) bounds down the DFS.** The naive local check fails precisely because the constraint is global to the path. This is the [[055-count-good-nodes-in-binary-tree|top-down-state]] pattern with an interval instead of a single max.

## Related
- concept: [[11-dfs-pattern|dfs-pattern]], [[02-traversal|traversal]]
- prev: [[055-count-good-nodes-in-binary-tree|Count Good Nodes]] · next: [[057-kth-smallest-element-in-a-bst|Kth Smallest Element in a BST]]

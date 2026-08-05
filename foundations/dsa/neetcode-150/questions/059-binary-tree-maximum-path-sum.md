# Binary Tree Maximum Path Sum

**LeetCode 124** · Trees · concept: [[11-dfs-pattern|dfs-pattern]]

## Problem

A path is any sequence of connected nodes (need not pass through the root). Return the maximum sum of node values along any path.

```
   -10
   9  20        ->  42   (15 -> 20 -> 7)
     15  7
```

## Approach — DFS returning the best "downward arm" + global max (optimal)

Two different quantities per node, and mixing them up is the classic mistake:

1. **Returned upward:** the best path that goes *down* one side only — `node.val + max(leftArm, rightArm, 0)`. A parent can only extend through *one* child.
2. **Used to update the global answer:** the best path with this node as the **peak** — `node.val + leftArm + rightArm` (both arms joined here). This path can't extend to a parent, so it's only for the answer, never returned.

```python
def maxPathSum(root):
    best = float("-inf")
    def dfs(node):
        nonlocal best
        if not node:
            return 0
        left  = max(dfs(node.left), 0)     # drop negative arms
        right = max(dfs(node.right), 0)
        best = max(best, node.val + left + right)   # path peaking here
        return node.val + max(left, right)          # extendable arm for the parent
    dfs(root)
    return best
```

**Time O(n), space O(h).**

## The two crucial subtleties

- **Clamp negative arms to 0** — a subtree that only subtracts should be dropped, not included.
- **Return one arm, but score with both** — a path through a node uses both children (the "peak"), yet a node handed *up* to its parent can only contribute one side (else it wouldn't be a simple path). Conflating these two is the bug that makes this problem hard.

## Key insight

**Distinguish "answer at this node" (both arms) from "value returned to the parent" (one arm).** It's the most refined form of the dual-purpose DFS from [[048-diameter-of-binary-tree|Diameter]] — Diameter counts edges, this sums values, but the shape is identical.

## Related
- concept: [[11-dfs-pattern|dfs-pattern]]
- relative: [[048-diameter-of-binary-tree|Diameter of Binary Tree]]
- prev: [[058-construct-binary-tree-from-preorder-and-inorder-traversal|Construct Tree]] · next: [[060-serialize-and-deserialize-binary-tree|Serialize and Deserialize Binary Tree]]

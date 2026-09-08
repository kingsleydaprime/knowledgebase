# Same Tree

**LeetCode 100** · Trees · concept: [[01-trees|trees]]

## Problem

Return `true` if two binary trees are identical in **structure and values**.

## Approach — parallel recursion (optimal)

Walk both trees in lockstep: same node must be both-null or both-present with equal values and matching subtrees.

```python
def isSameTree(p, q):
    if not p and not q:
        return True                  # both empty here -> match
    if not p or not q or p.val != q.val:
        return False                 # one empty, or values differ -> mismatch
    return isSameTree(p.left, q.left) and isSameTree(p.right, q.right)
```

**Time O(n), space O(h).**

## The base cases carry the logic

Three conditions cover everything: both null (match), exactly one null or unequal values (mismatch), otherwise recurse on both child pairs. The `and` means any single mismatch anywhere collapses the whole result to `False`.

## Key insight

**Compare two trees by recursing on both simultaneously.** This "parallel DFS over a pair of structures" is the reusable primitive — it's the subroutine called at every node of [[051-subtree-of-another-tree|Subtree of Another Tree]] and mirrors the structure of symmetric-tree checks.

## Related
- concept: [[01-trees|trees]], [[02-dfs|dfs]]
- prev: [[049-balanced-binary-tree|Balanced Binary Tree]] · next: [[051-subtree-of-another-tree|Subtree of Another Tree]]

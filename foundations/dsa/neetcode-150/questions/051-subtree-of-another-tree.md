# Subtree of Another Tree

**LeetCode 572** · Trees · concept: [[01-trees|trees]]

## Problem

Return `true` if `subRoot` appears as a subtree of `root` (a node in `root` whose entire subtree equals `subRoot`).

## Approach — "same tree" tried at every node (optimal)

At each node of `root`, ask "is the tree rooted *here* identical to `subRoot`?" using [[050-same-tree|Same Tree]]. If any node matches, done.

```python
def isSubtree(root, subRoot):
    if not subRoot:
        return True
    if not root:
        return False
    if isSameTree(root, subRoot):        # match rooted at this node?
        return True
    return isSubtree(root.left, subRoot) or isSubtree(root.right, subRoot)

def isSameTree(p, q):
    if not p and not q: return True
    if not p or not q or p.val != q.val: return False
    return isSameTree(p.left, q.left) and isSameTree(p.right, q.right)
```

**Time O(m · n)** worst case (m = size of `root`, n = `subRoot`): each of m nodes may trigger an O(n) comparison. **Space O(h).**

## Faster alternative — serialize + substring

Serialize both trees to strings (with null markers and delimiters to avoid false matches), then check whether `subRoot`'s serialization is a **substring** of `root`'s. With KMP that's **O(m + n)**. Good to mention; the nested-recursion version is what's usually expected.

## Key insight

**"Does structure X appear inside structure Y?" → run an equality check anchored at every position of Y.** It composes [[050-same-tree|Same Tree]] (the anchored check) with a traversal (try every anchor) — the same shape as substring search on trees.

## Related
- concept: [[01-trees|trees]]
- builds on: [[050-same-tree|Same Tree]]
- prev: [[050-same-tree|Same Tree]] · next: [[052-lowest-common-ancestor-of-a-bst|Lowest Common Ancestor of a BST]]

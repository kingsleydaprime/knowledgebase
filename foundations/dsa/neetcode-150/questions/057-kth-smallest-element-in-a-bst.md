# Kth Smallest Element in a BST

**LeetCode 230** · Trees · concept: [[02-traversal|traversal]]

## Problem

Return the k-th smallest value in a BST (1-indexed).

## The key property — in-order gives sorted order

An **in-order traversal** of a BST (left → node → right) visits values in ascending order. So the k-th value emitted is the answer — stop as soon as you've counted k.

## Approach — iterative in-order with a stack (optimal)

An explicit stack lets you halt the instant the k-th node pops, without traversing the rest of the tree.

```python
def kthSmallest(root, k):
    stack = []
    curr = root
    while stack or curr:
        while curr:               # go as far left as possible
            stack.append(curr)
            curr = curr.left
        curr = stack.pop()        # visit in ascending order
        k -= 1
        if k == 0:
            return curr.val
        curr = curr.right         # then the right subtree
```

**Time O(h + k), space O(h)** — you only descend to the k-th element, not the whole tree.

## Why in-order and not a sort

Sorting all values is O(n log n) and ignores the structure. The BST already *encodes* sorted order in its shape; in-order traversal reads it out directly, and stopping at k avoids visiting the rest. (If the tree is modified frequently and you need many such queries, augmenting nodes with subtree sizes gives O(h) per query.)

## Key insight

**BST + "k-th smallest / sorted position" → in-order traversal, halted at k.** The whole trick is knowing that in-order = sorted for a BST; the iterative stack form is what lets you stop early instead of collecting everything.

## Related
- concept: [[02-traversal|traversal]], [[01-trees|trees]]
- prev: [[056-validate-binary-search-tree|Validate BST]] · next: [[058-construct-binary-tree-from-preorder-and-inorder-traversal|Construct Tree from Preorder & Inorder]]

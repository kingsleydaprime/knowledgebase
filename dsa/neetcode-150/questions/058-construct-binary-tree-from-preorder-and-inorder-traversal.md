# Construct Binary Tree from Preorder and Inorder Traversal

**LeetCode 105** · Trees · concept: [[02-traversal|traversal]]

## Problem

Rebuild a binary tree given its preorder and inorder traversals (values unique).

```
preorder = [3,9,20,15,7], inorder = [9,3,15,20,7]   ->   the tree
```

## The two facts that reconstruct the tree

- **Preorder** is `root, [left subtree], [right subtree]` — so `preorder[0]` is always the current **root**.
- **Inorder** is `[left subtree], root, [right subtree]` — so locating the root's value **in inorder** splits it into exactly the left and right subtrees.

Take the root from the front of preorder, find it in inorder to size the left subtree, and recurse on each side.

```python
def buildTree(preorder, inorder):
    idx = {v: i for i, v in enumerate(inorder)}    # value -> inorder index (O(1) splits)
    self_pre = [0]                                 # a moving pointer into preorder

    def build(lo, hi):                             # inorder bounds [lo, hi]
        if lo > hi:
            return None
        val = preorder[self_pre[0]]
        self_pre[0] += 1
        root = TreeNode(val)
        mid = idx[val]
        root.left  = build(lo, mid - 1)            # left subtree (consumed first in preorder)
        root.right = build(mid + 1, hi)
        return root

    return build(0, len(inorder) - 1)
```

**Time O(n), space O(n)** (the index map + recursion). The hash map makes each root-lookup O(1) instead of O(n), avoiding an O(n²) scan.

## The ordering that makes it work

Preorder is consumed strictly left to right — root, then the *entire* left subtree, then the right. So advancing a single pointer through preorder while recursing left-before-right hands each `build` call the correct next root. Inorder only supplies the split index.

## Key insight

**Preorder gives roots in order; inorder gives the left/right split.** Combining "which node is the root" (preorder) with "how big is each subtree" (inorder) uniquely rebuilds the tree. (Postorder + inorder works the same way, consuming postorder from the right.)

## Related
- concept: [[02-traversal|traversal]]
- prev: [[057-kth-smallest-element-in-a-bst|Kth Smallest in a BST]] · next: [[059-binary-tree-maximum-path-sum|Binary Tree Maximum Path Sum]]

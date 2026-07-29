# Pattern: Binary Tree Traversal

The mechanics of preorder/inorder/postorder are covered in [[02-traversal|traversal]] — this note is about *recognizing when each order is the right tool*, since that's the part that actually shows up as a decision in interview problems.

## Recognizing which order to reach for

- **Preorder** (root → left → right): use when you need to process/record a node **before** its children — e.g. building a path string from root to each leaf, since you need the ancestors already collected before you get to a leaf.
- **Inorder** (left → root → right): use when the tree is a BST and you need values in **sorted order** — e.g. finding the k-th smallest element.
- **Postorder** (left → right → root): use when a node's answer **depends on its children's answers first** — e.g. computing a max path sum through a subtree, which requires knowing the best path from each child before combining them at the parent.

## Example — preorder for root-to-leaf paths

```python
def binary_tree_paths(root):
    paths = []
    def dfs(node, path):
        if node is None:
            return
        path = path + [str(node.val)]
        if node.left is None and node.right is None:   # leaf
            paths.append("->".join(path))
            return
        dfs(node.left, path)
        dfs(node.right, path)
    dfs(root, [])
    return paths
```

This is preorder because `path` gets the current node appended *before* recursing into children — by the time you reach a leaf, `path` already holds the full chain of ancestors.

## Example — postorder for a value that depends on children

```python
def max_path_sum(root):
    best = float("-inf")
    def dfs(node):
        nonlocal best
        if node is None:
            return 0
        left_gain = max(dfs(node.left), 0)     # ignore negative contributions
        right_gain = max(dfs(node.right), 0)
        best = max(best, node.val + left_gain + right_gain)   # combine children *after* recursing
        return node.val + max(left_gain, right_gain)           # what this node can contribute upward
    dfs(root)
    return best
```

Postorder because both children's results (`left_gain`, `right_gain`) must be known before this node can compute anything.

## Complexity

O(n) — every node is visited exactly once regardless of the order.

## Practice problems
1. Binary Tree Paths (LeetCode #257) — preorder
2. Kth Smallest Element in a BST (LeetCode #230) — inorder
3. Binary Tree Maximum Path Sum (LeetCode #124) — postorder

## Related
- [[02-traversal|traversal]]
- [[01-trees|trees]]
- [[11-dfs-pattern|dfs-pattern]]

# Pattern: Binary Tree Traversal

**[Intermediate]** — A university-level introduction to the binary tree traversal pattern: what it is, why it exists, how it works, and how to implement it independently.

## Before you start

- You should understand binary trees. See [[01-trees|trees]] if needed.
- You should understand recursion. See [[languages/06-python/04-functions-and-scope|Python functions and scope]] if needed.

**What you will be able to do after this lesson:**

1. Define preorder, inorder, and postorder traversal and explain when each is the right tool.
2. Implement root-to-leaf path construction using preorder traversal.
3. Implement a value that depends on children's answers using postorder traversal.
4. Explain why inorder traversal of a BST gives sorted values.

**Study route:** read the motivation and mechanism first, trace the worked example by hand, then attempt the independent task before looking at the hints.

---

## 1. Why this pattern exists (real-world motivation)

Imagine you're building a file system browser. You need to display the directory structure as a tree. To build the display, you need to visit every directory and file in a specific order: you might want to list a directory before its contents (preorder), list contents before the directory summary (postorder), or list everything in alphabetical order (inorder for BSTs).

The mechanics of preorder/inorder/postorder are covered in [[02-traversal|traversal]] — this note is about _recognizing when each order is the right tool_, since that's the part that actually shows up as a decision in interview problems.

---

## 2. Definitions and terminology

| Term                  | Plain-English definition                                                | Example / analogy                                                 |
| --------------------- | ----------------------------------------------------------------------- | ----------------------------------------------------------------- |
| **Preorder**          | Process the current node before its children                            | List a directory before its contents                              |
| **Inorder**           | Process the left subtree, then the current node, then the right subtree | List BST values in sorted order                                   |
| **Postorder**         | Process the children before the current node                            | Compute a directory's size after computing all subdirectory sizes |
| **Root-to-leaf path** | A path from the root node to a leaf node                                | A file path from the root directory to a file                     |

---

## 3. How it works — step by step

### Preorder (root → left → right)

Use when you need to process/record a node **before** its children — e.g. building a path string from root to each leaf, since you need the ancestors already collected before you get to a leaf.

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

This is preorder because `path` gets the current node appended _before_ recursing into children — by the time you reach a leaf, `path` already holds the full chain of ancestors.

### Postorder (left → right → root)

Use when a node's answer **depends on its children's answers first** — e.g. computing a max path sum through a subtree, which requires knowing the best path from each child before combining them at the parent.

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

### Inorder (left → root → right)

Use when the tree is a BST and you need values in **sorted order** — e.g. finding the k-th smallest element. Inorder traversal of a BST visits nodes in ascending order because all values in the left subtree are less than the root, and all values in the right subtree are greater.

---

## 4. Implementation — complete runnable example

**Runnable example:** save as `binary_tree_traversal_lab.py` and run `python3 binary_tree_traversal_lab.py`. It uses only Python's standard library and creates no external files.

```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def preorder(root):
    """Preorder traversal: root -> left -> right."""
    if not root:
        return []
    result = []
    def dfs(node):
        if not node:
            return
        result.append(node.val)    # process root
        dfs(node.left)             # traverse left
        dfs(node.right)            # traverse right
    dfs(root)
    return result


def inorder(root):
    """Inorder traversal: left -> root -> right."""
    if not root:
        return []
    result = []
    def dfs(node):
        if not node:
            return
        dfs(node.left)             # traverse left
        result.append(node.val)    # process root
        dfs(node.right)            # traverse right
    dfs(root)
    return result


def postorder(root):
    """Postorder traversal: left -> right -> root."""
    if not root:
        return []
    result = []
    def dfs(node):
        if not node:
            return
        dfs(node.left)             # traverse left
        dfs(node.right)            # traverse right
        result.append(node.val)    # process root
    dfs(root)
    return result


def binary_tree_paths(root):
    """Build all root-to-leaf paths."""
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


if __name__ == "__main__":
    # Build a sample tree:
    #       1
    #      / \
    #     2   3
    #    / \
    #   4   5
    root = TreeNode(1)
    root.left = TreeNode(2)
    root.right = TreeNode(3)
    root.left.left = TreeNode(4)
    root.left.right = TreeNode(5)

    print("Preorder:", preorder(root))
    print("Inorder:", inorder(root))
    print("Postorder:", postorder(root))
    print("Binary tree paths:", binary_tree_paths(root))

    assert preorder(root) == [1, 2, 4, 5, 3]
    assert inorder(root) == [4, 2, 5, 1, 3]
    assert postorder(root) == [4, 5, 2, 3, 1]
    assert binary_tree_paths(root) == ["1->2->4", "1->2->5", "1->3"]

    print("binary_tree_traversal_lab: passed")
```

Expected output:

```
Preorder: [1, 2, 4, 5, 3]
Inorder: [4, 2, 5, 1, 3]
Postorder: [4, 5, 2, 3, 1]
Binary tree paths: ['1->2->4', '1->2->5', '1->3']
binary_tree_traversal_lab: passed
```

---

## 5. Complexity

O(n) — every node is visited exactly once regardless of the order.

---

## 6. Tradeoffs and limitations

- **Preorder** is natural for copying a tree or building a path string.
- **Inorder** is natural for BSTs where you need sorted output.
- **Postorder** is natural when a node's answer depends on its children's answers.
- **Level-order** (BFS) is natural when you need to process nodes level by level.

---

## 7. Check your understanding (self-assessment)

Attempt these without the note, then compare your reasoning below.

1. **Question:** Given the tree above, trace through the preorder, inorder, and postorder traversals step by step.
2. **Question:** Why does inorder traversal of a BST give sorted values?
3. **Question:** When would you use postorder traversal instead of preorder?

### Answers — after your attempt

1. Preorder: 1, 2, 4, 5, 3 (root, left subtree, right subtree)
   Inorder: 4, 2, 5, 1, 3 (left subtree, root, right subtree)
   Postorder: 4, 5, 2, 3, 1 (left subtree, right subtree, root)
2. In a BST, all values in the left subtree are less than the root, and all values in the right subtree are greater. Inorder visits left subtree first, then root, then right subtree — so values come out in ascending order.
3. Use postorder when a node's answer depends on its children's answers first — e.g. computing a max path sum through a subtree, which requires knowing the best path from each child before combining them at the parent.

---

## 8. Practice — independent task

**Task:** Implement a function `max_depth(root)` that returns the maximum depth of a binary tree. Use postorder traversal. Test it with the following cases:

- `root = [3, 9, 20, null, null, 15, 7]` → expected `3`
- `root = [1, null, 2]` → expected `2`

**Done when:** your function returns the correct maximum depth for both test cases.

---

## 9. Related

- [[02-traversal|traversal]] — the mechanics of preorder/inorder/postorder
- [[01-trees|trees]] — the underlying data structure
- [[11-dfs-pattern|dfs-pattern]] — DFS as a problem-solving pattern
- [[10-binary-tree-traversal-pattern|binary-tree-traversal-pattern]] — this note

---

## 10. Further reading

The pattern appears in many contexts beyond LeetCode:

- **File system navigation:** Listing directory contents in different orders
- **Expression evaluation:** Building and evaluating expression trees
- **Compiler design:** Abstract syntax tree traversal
- **Game trees:** Minimax algorithm for game playing

The core idea — choosing the right traversal order based on when you need to process each node — is a fundamental algorithmic technique that appears whenever you need to visit all nodes in a tree.

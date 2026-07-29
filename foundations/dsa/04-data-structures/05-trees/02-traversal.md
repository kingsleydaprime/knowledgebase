# Traversal

Traversal just means visiting every element of a structure, systematically, exactly once. For a linear structure like an [[01-arrays|array]] or [[04-linked-lists|linked list]] this is trivial — start at one end, move to the next, stop when you run out. It only gets interesting once the structure branches: [[01-trees|trees]] and [[06-graphs|graphs]], where "the next element" is ambiguous because there can be multiple children or neighbors to choose from. This note is about the ordering conventions for trees; the graph-specific mechanics live in [[02-dfs|dfs]] and [[03-bfs|bfs]].

## Tree traversal orders

For a binary tree, there are four standard orders, and the difference between them is entirely about *when* you process the current node relative to its children.

```
        1
       / \
      2   3
     / \
    4   5
```

**Preorder** (node, then left, then right) — process the node before descending:

```python
def preorder(node, out):
    if node is None:
        return
    out.append(node.value)      # visit first
    preorder(node.left, out)
    preorder(node.right, out)
# 1, 2, 4, 5, 3
```

**Inorder** (left, node, right) — for a BST, this visits values in sorted order, which is the whole reason it's useful:

```python
def inorder(node, out):
    if node is None:
        return
    inorder(node.left, out)
    out.append(node.value)      # visit between the two subtrees
    inorder(node.right, out)
# 4, 2, 5, 1, 3
```

**Postorder** (left, right, node) — process children fully before the node itself; this is the order you need whenever a node depends on its children's results first (deleting a tree bottom-up, evaluating an expression tree):

```python
def postorder(node, out):
    if node is None:
        return
    postorder(node.left, out)
    postorder(node.right, out)
    out.append(node.value)      # visit last
# 4, 5, 2, 3, 1
```

**Level-order** (top to bottom, left to right within each level) — this one isn't naturally recursive; it needs a queue, which makes it structurally identical to [[03-bfs|bfs]] on a tree:

```python
from collections import deque

def level_order(root):
    if root is None:
        return []
    out, queue = [], deque([root])
    while queue:
        node = queue.popleft()
        out.append(node.value)
        if node.left:  queue.append(node.left)
        if node.right: queue.append(node.right)
    return out
# 1, 2, 3, 4, 5
```

## The pattern underneath all of them

Pre/in/postorder are all **depth-first** — they commit to one branch and go as deep as possible before backtracking. They only differ in *when* the current node gets recorded relative to that descent. Level-order is **breadth-first** — it processes everything at the current depth before moving deeper. This same pre/in/post-vs-level distinction generalizes directly to graphs as DFS vs BFS — a graph traversal is really the same idea with one addition: a `visited` set, because graphs (unlike trees) can have cycles.

## Gotchas

- Recursive traversal implicitly uses the call stack — see the space complexity note in [[01-algorithms|algorithms]]. A very deep or unbalanced tree can stack-overflow a naive recursive traversal; an iterative version with an explicit stack avoids this.
- Level-order needs a queue (FIFO), not a stack — using a stack there gives you a *different*, not-quite-DFS order, not level-order. This mix-up is the most common bug when implementing this from scratch under time pressure.
- Inorder-gives-sorted-order is a BST-only guarantee — it means nothing on a plain (non-BST) binary tree.

## Related
- [[01-trees|trees]]
- [[02-dfs|dfs]]
- [[03-bfs|bfs]]

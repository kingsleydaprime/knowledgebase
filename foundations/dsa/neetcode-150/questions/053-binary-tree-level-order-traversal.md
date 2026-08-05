# Binary Tree Level Order Traversal

**LeetCode 102** · Trees · concepts: [[03-bfs|bfs]], [[12-bfs-pattern|bfs-pattern]]

## Problem

Return the node values level by level, top to bottom, as a list of lists.

```
    3
  9   20        ->  [[3], [9, 20], [15, 7]]
     15  7
```

## Approach — BFS, one level per iteration (optimal)

Standard [[03-bfs|BFS]] with a queue, but capture the **queue's size at the start of each outer iteration** — that count is exactly the number of nodes on the current level, so you can drain precisely one level at a time.

```python
from collections import deque

def levelOrder(root):
    if not root:
        return []
    res, queue = [], deque([root])
    while queue:
        level = []
        for _ in range(len(queue)):        # snapshot: exactly this level's nodes
            node = queue.popleft()
            level.append(node.val)
            if node.left:  queue.append(node.left)
            if node.right: queue.append(node.right)
        res.append(level)
    return res
```

**Time O(n), space O(n)** (up to a full level in the queue).

## The `len(queue)` snapshot

Grabbing `len(queue)` *before* the inner loop freezes how many nodes belong to this level; children pushed during the loop belong to the *next* level and aren't processed until the next outer pass. This one line is what turns a flat BFS into a level-grouped one.

## Key insight

**Level-by-level processing → BFS with a per-level size snapshot.** This template powers Right Side View (take the last of each level), level averages, zigzag order, and any "do something per level" tree problem — the whole [[12-bfs-pattern|BFS pattern]] on trees.

## Related
- concepts: [[03-bfs|bfs]], [[12-bfs-pattern|bfs-pattern]], [[02-traversal|traversal]]
- prev: [[052-lowest-common-ancestor-of-a-bst|LCA of a BST]] · next: [[054-binary-tree-right-side-view|Binary Tree Right Side View]]

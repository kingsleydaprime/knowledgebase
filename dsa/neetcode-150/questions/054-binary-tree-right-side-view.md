# Binary Tree Right Side View

**LeetCode 199** · Trees · concept: [[12-bfs-pattern|bfs-pattern]]

## Problem

Return the values visible from the **right side** — the rightmost node of each level, top to bottom.

```
    1
  2   3       ->  [1, 3, 4]
   5    4
```

## Approach — level-order BFS, take the last of each level (optimal)

Reuse the [[053-binary-tree-level-order-traversal|level-order]] template; the rightmost node is simply the **last** one dequeued on each level.

```python
from collections import deque

def rightSideView(root):
    if not root:
        return []
    res, queue = [], deque([root])
    while queue:
        n = len(queue)
        for i in range(n):
            node = queue.popleft()
            if i == n - 1:                 # last node of this level = rightmost
                res.append(node.val)
            if node.left:  queue.append(node.left)
            if node.right: queue.append(node.right)
    return res
```

**Time O(n), space O(n).**

## Why "rightmost," not "right child"

The right view isn't the chain of right children — a deep left subtree can be visible if the right side is shorter (node 5 above would show if there were no node 4). Taking the last node *per level* correctly captures whatever is furthest right at each depth. A DFS that visits right-first and records the first node seen at each new depth works too.

## Key insight

**"What's visible from a side / per level" → level-order BFS, then pick the boundary node.** A direct specialization of the level-order template — the reusable move is "process per level, then select one node from each."

## Related
- concept: [[12-bfs-pattern|bfs-pattern]]
- builds on: [[053-binary-tree-level-order-traversal|Level Order Traversal]]
- prev: [[053-binary-tree-level-order-traversal|Level Order Traversal]] · next: [[055-count-good-nodes-in-binary-tree|Count Good Nodes]]

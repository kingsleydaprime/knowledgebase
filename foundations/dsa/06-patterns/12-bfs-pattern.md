# Pattern: BFS as a Problem-Solving Pattern

The mechanics — queue-based, level by level, why it guarantees shortest paths — are covered in [[03-bfs|bfs]]. This note is about recognizing the problem shape: **anything phrased as "minimum steps/levels/time to reach X"** in an unweighted setting is almost always BFS from the start state.

## When to reach for it

- **Level-order tree traversal** — process a tree level by level (see [[10-binary-tree-traversal-pattern|binary-tree-traversal-pattern]] for the DFS orders; this is the one order that isn't naturally recursive).
- **Multi-source spreading problems** — "rotting oranges," "shortest bridge" — start BFS from *all* initial sources simultaneously (push them all into the queue before the first pop), and the number of levels processed is the time/distance the spread takes.
- **Shortest transformation sequence** — "word ladder": each word is a node, an edge exists between words one letter apart, and the shortest path from start word to end word is exactly what BFS finds.

## Example — level-order traversal

```python
from collections import deque

def level_order(root):
    if root is None:
        return []
    result, queue = [], deque([root])
    while queue:
        level_size = len(queue)         # snapshot: exactly how many nodes are in this level
        level = []
        for _ in range(level_size):
            node = queue.popleft()
            level.append(node.val)
            if node.left:  queue.append(node.left)
            if node.right: queue.append(node.right)
        result.append(level)
    return result
```

The `level_size = len(queue)` snapshot is the key trick that turns plain BFS into *level-order* BFS — without it you'd process nodes but lose track of which level each one belonged to.

## Example — multi-source BFS ("Rotting Oranges")

```python
def oranges_rotting(grid):
    rows, cols = len(grid), len(grid[0])
    queue = deque()
    fresh = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 2:
                queue.append((r, c))        # every rotten orange starts in the queue at once
            elif grid[r][c] == 1:
                fresh += 1

    minutes = 0
    directions = [(0,1),(0,-1),(1,0),(-1,0)]
    while queue and fresh:
        minutes += 1
        for _ in range(len(queue)):         # process one full level = one minute
            r, c = queue.popleft()
            for dr, dc in directions:
                nr, nc = r+dr, c+dc
                if 0<=nr<rows and 0<=nc<cols and grid[nr][nc]==1:
                    grid[nr][nc] = 2
                    fresh -= 1
                    queue.append((nr, nc))
    return minutes if fresh == 0 else -1
```

All initial rotten oranges seed the queue *before* the first level runs — this is what makes it "multi-source": BFS naturally handles multiple simultaneous starting points the same way it handles one.

## Complexity

O(V + E), or O(rows × cols) on a grid — same as plain BFS.

## Practice problems

All of these are written up in the [[foundations/dsa/neetcode-150/README|NeetCode 150]]:

1. [[053-binary-tree-level-order-traversal|Binary Tree Level Order Traversal]] (LeetCode #102)
2. [[054-binary-tree-right-side-view|Binary Tree Right Side View]] (LeetCode #199) — level order where you keep only the last node of each level
3. [[085-rotting-oranges|Rotting Oranges]] (LeetCode #994) — multi-source BFS
4. [[086-walls-and-gates|Walls and Gates]] (LeetCode #286) — multi-source BFS on a grid, seeding the queue with every gate at once
5. [[092-word-ladder|Word Ladder]] (LeetCode #127) — shortest transformation sequence over an implicit graph

## Related
- [[03-bfs|bfs]]
- [[13-matrix-traversal|matrix-traversal]]
- [[10-binary-tree-traversal-pattern|binary-tree-traversal-pattern]]

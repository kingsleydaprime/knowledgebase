# Rotting Oranges

**LeetCode 994** · Graphs · concepts: [[03-bfs|bfs]], [[12-bfs-pattern|bfs-pattern]]

## Problem

In a grid, `2` = rotten, `1` = fresh, `0` = empty. Each minute, a rotten orange rots its 4-directional fresh neighbors. Return the minutes until none are fresh, or `-1` if some can never rot.

## Approach — multi-source BFS by level (optimal)

Rot spreads one ring per minute from **all** rotten oranges simultaneously — that's BFS where the "minute" is the BFS level. Seed the queue with **every** initial rotten cell, then expand level by level, counting minutes.

```python
from collections import deque

def orangesRotting(grid):
    rows, cols = len(grid), len(grid[0])
    queue = deque()
    fresh = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 2:
                queue.append((r, c))       # all initial sources
            elif grid[r][c] == 1:
                fresh += 1

    minutes = 0
    while queue and fresh:
        minutes += 1
        for _ in range(len(queue)):        # process one minute's worth
            r, c = queue.popleft()
            for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):
                nr, nc = r+dr, c+dc
                if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 1:
                    grid[nr][nc] = 2
                    fresh -= 1
                    queue.append((nr, nc))
    return minutes if fresh == 0 else -1    # leftover fresh -> unreachable
```

**Time O(rows · cols), space O(rows · cols).**

## Multi-source BFS + the level snapshot

Seeding the queue with all rotten oranges makes them spread **in parallel** — the first time a fresh cell is reached is the earliest possible minute. The `len(queue)` snapshot (as in [[053-binary-tree-level-order-traversal|Level Order]]) processes exactly one minute per outer iteration. The final `fresh` count detects unreachable oranges → `-1`.

## Key insight

**Simultaneous spread from many sources, measuring time/distance → multi-source BFS (all sources in the initial queue), counting levels.** BFS gives shortest distance, and multi-source parallelizes it — the template for "fire/infection/flood spreading" and nearest-source problems.

## Related
- concepts: [[03-bfs|bfs]], [[12-bfs-pattern|bfs-pattern]]
- relative: [[086-walls-and-gates|Walls and Gates]] (same multi-source BFS)
- prev: [[084-surrounded-regions|Surrounded Regions]] · next: [[086-walls-and-gates|Walls and Gates]]

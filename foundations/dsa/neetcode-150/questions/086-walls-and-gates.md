# Walls and Gates

**LeetCode 286** · Graphs · concepts: [[03-bfs|bfs]], [[12-bfs-pattern|bfs-pattern]]

## Problem

A grid with `-1` (wall), `0` (gate), and `INF` (empty room). Fill each room with the distance to its **nearest** gate (leave `INF` if unreachable).

## Approach — multi-source BFS from all gates (optimal)

The nearest-gate distance is a shortest-path-on-unweighted-grid problem. Seed the BFS queue with **every gate at once**; expand outward, and the first time BFS reaches a room is—by BFS's level order—its shortest distance to *some* gate.

```python
from collections import deque

def wallsAndGates(rooms):
    rows, cols = len(rooms), len(rooms[0])
    INF = 2**31 - 1
    queue = deque()
    for r in range(rows):
        for c in range(cols):
            if rooms[r][c] == 0:
                queue.append((r, c))       # all gates are sources

    while queue:
        r, c = queue.popleft()
        for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):
            nr, nc = r+dr, c+dc
            if (0 <= nr < rows and 0 <= nc < cols
                    and rooms[nr][nc] == INF):     # unvisited empty room
                rooms[nr][nc] = rooms[r][c] + 1    # one step further from a gate
                queue.append((nr, nc))
```

**Time O(rows · cols), space O(rows · cols).**

## Why multi-source beats per-gate BFS

Running BFS from each gate separately and taking the min is O(gates · mn). Seeding *all* gates into one queue floods outward together, so the first arrival at each room is automatically the nearest gate — one O(mn) pass. Writing the distance only when a room is still `INF` doubles as the visited check.

## Key insight

**"Distance to the nearest of many sources" → single multi-source BFS from all sources at once.** Identical machinery to [[085-rotting-oranges|Rotting Oranges]] — seed all sources, let the wavefronts meet, and each cell's first visit is its nearest-source distance.

## Related
- concepts: [[03-bfs|bfs]], [[12-bfs-pattern|bfs-pattern]]
- relative: [[085-rotting-oranges|Rotting Oranges]]
- prev: [[085-rotting-oranges|Rotting Oranges]] · next: [[087-course-schedule|Course Schedule]]

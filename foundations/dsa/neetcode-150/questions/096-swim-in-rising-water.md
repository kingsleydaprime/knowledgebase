# Swim in Rising Water

**LeetCode 778** · Advanced Graphs · concept: [[06-dijkstra|dijkstra]]

## Problem

In an `n × n` grid of elevations, water level rises over time; at time `t` you can be on any cell with elevation ≤ `t`. Return the least time to travel from top-left to bottom-right, moving 4-directionally.

## The idea — minimize the maximum elevation on a path

You want the path whose **highest cell is as low as possible** (that peak determines when you can finish). This is a "minimax path" — a [[06-dijkstra|Dijkstra]] variant where a path's cost is the **max** elevation along it, not the sum.

```python
import heapq

def swimInWater(grid):
    n = len(grid)
    heap = [(grid[0][0], 0, 0)]            # (max elevation so far, r, c)
    visited = set()
    while heap:
        t, r, c = heapq.heappop(heap)
        if (r, c) in visited:
            continue
        if (r, c) == (n-1, n-1):
            return t                       # first arrival = minimal peak
        visited.add((r, c))
        for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):
            nr, nc = r+dr, c+dc
            if 0 <= nr < n and 0 <= nc < n and (nr, nc) not in visited:
                heapq.heappush(heap, (max(t, grid[nr][nc]), nr, nc))   # cost = running max
```

**Time O(n² log n), space O(n²).**

## Dijkstra with a "max" cost function

The only change from standard Dijkstra is the edge relaxation: instead of `dist + weight`, the path cost is `max(dist, cellElevation)`. The min-heap then always expands the reachable cell with the lowest peak-so-far, and the first time it reaches the goal, that peak is minimal. (A [[09-modified-binary-search|binary search on t]] + flood-fill feasibility check is an alternative framing.)

## Key insight

**"Minimize the maximum along a path" → Dijkstra with a max-based cost.** Recognizing that the objective is a bottleneck (peak) rather than a sum, and that Dijkstra's greedy expansion still works with `max` in place of `+`, is the leap.

## Related
- concept: [[06-dijkstra|dijkstra]]; alt: [[09-modified-binary-search|binary search on the answer]]
- prev: [[095-network-delay-time|Network Delay Time]] · next: [[097-alien-dictionary|Alien Dictionary]]

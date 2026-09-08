# Max Area of Island

**LeetCode 695** · Graphs · concept: [[13-matrix-traversal|matrix-traversal]]

## Problem

Return the area (cell count) of the largest island in a 0/1 grid.

## Approach — flood fill returning area (optimal)

Identical to [[080-number-of-islands|Number of Islands]], except each flood fill **returns the size** of its region instead of just marking it, and you track the maximum.

```python
def maxAreaOfIsland(grid):
    rows, cols = len(grid), len(grid[0])
    def dfs(r, c):
        if (r < 0 or r >= rows or c < 0 or c >= cols
                or grid[r][c] == 0):
            return 0
        grid[r][c] = 0                     # mark visited
        return 1 + dfs(r+1,c) + dfs(r-1,c) + dfs(r,c+1) + dfs(r,c-1)

    best = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 1:
                best = max(best, dfs(r, c))
    return best
```

**Time O(rows · cols), space O(rows · cols).**

## The one change from counting

The DFS returns `1 + (areas of the four neighbors)` — a bottom-up sum, the same aggregation shape as [[047-maximum-depth-of-binary-tree|tree depth]]. Marking visited (`grid[r][c] = 0`) ensures each cell is counted exactly once.

## Key insight

**When a flood fill needs a *quantity* per region (area, sum, perimeter), have the traversal return it and aggregate up.** Region-counting and region-measuring are the same traversal with different return values — a small but frequently-needed variation.

## Related
- concept: [[13-matrix-traversal|matrix-traversal]]
- builds on: [[080-number-of-islands|Number of Islands]]
- prev: [[081-clone-graph|Clone Graph]] · next: [[083-pacific-atlantic-water-flow|Pacific Atlantic Water Flow]]

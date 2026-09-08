# Number of Islands

**LeetCode 200** · Graphs · concepts: [[13-matrix-traversal|matrix-traversal]], [[06-graphs|graphs]]

## Problem

Given a grid of `"1"` (land) and `"0"` (water), count the islands (groups of land connected 4-directionally).

## Approach — flood fill each unvisited land cell (optimal)

Scan every cell; when you hit unvisited land, that's a **new island** — flood-fill (DFS or BFS) the entire connected region, marking it visited so it isn't recounted. The number of flood fills you launch is the island count.

```python
def numIslands(grid):
    rows, cols = len(grid), len(grid[0])
    def dfs(r, c):
        if (r < 0 or r >= rows or c < 0 or c >= cols
                or grid[r][c] != "1"):
            return
        grid[r][c] = "0"                   # sink it (mark visited)
        dfs(r+1, c); dfs(r-1, c); dfs(r, c+1); dfs(r, c-1)

    count = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == "1":
                dfs(r, c)                  # one full island
                count += 1
    return count
```

**Time O(rows · cols), space O(rows · cols)** worst-case recursion.

## A grid is a graph

Each cell is a node connected to its neighbors; "island" = connected component. Counting components is "loop over all nodes, start a fresh traversal from each unvisited one" — the disconnected-graph handling from [[06-graphs|graphs]]. Sinking cells to `"0"` is the visited-marking.

## Key insight

**Count connected regions on a grid → for each unvisited land cell, flood fill and increment.** The traversal marks a whole component in one shot, so the number of launches equals the number of components. The foundational grid-graph problem.

## Related
- concepts: [[13-matrix-traversal|matrix-traversal]], [[06-graphs|graphs]], [[02-dfs|dfs]]
- next: [[081-clone-graph|Clone Graph]]

# Pacific Atlantic Water Flow

**LeetCode 417** · Graphs · concept: [[13-matrix-traversal|matrix-traversal]]

## Problem

Water flows from a cell to neighbors of **equal or lower** height. The Pacific borders the top/left edges, the Atlantic the bottom/right. Return all cells from which water can reach **both** oceans.

## The trick — search *backward* from the oceans

Forward ("can this cell reach an ocean?") would run a search per cell — O((mn)²). Instead **reverse the flow**: start from each ocean's border cells and climb to neighbors of **equal or greater** height (water could have flowed *down* to here). Each ocean's traversal marks every cell that can reach it; the answer is the **intersection**.

```python
def pacificAtlantic(heights):
    rows, cols = len(heights), len(heights[0])
    pac, atl = set(), set()
    def dfs(r, c, visited, prev_height):
        if (r < 0 or r >= rows or c < 0 or c >= cols
                or (r, c) in visited or heights[r][c] < prev_height):
            return
        visited.add((r, c))
        for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):
            dfs(r+dr, c+dc, visited, heights[r][c])
    for c in range(cols):
        dfs(0, c, pac, heights[0][c]);            dfs(rows-1, c, atl, heights[rows-1][c])
    for r in range(rows):
        dfs(r, 0, pac, heights[r][0]);            dfs(r, cols-1, atl, heights[r][cols-1])
    return [[r, c] for r in range(rows) for c in range(cols)
            if (r, c) in pac and (r, c) in atl]
```

**Time O(rows · cols), space O(rows · cols).**

## Why reverse the direction

Reversing turns "does a path from X reach the ocean?" (one query per cell) into "which cells does the ocean reach?" (two traversals total). The climb condition (`heights[nei] ≥ heights[cur]`) is the flow condition run backward. Answering many "can reach the boundary" questions at once by flooding *from* the boundary is a reusable reframing.

## Key insight

**"Which cells can reach a target region?" → flood *from* the region, reversing the movement rule, then intersect.** Multi-source reverse BFS/DFS collapses per-cell searches into a couple of passes.

## Related
- concept: [[13-matrix-traversal|matrix-traversal]]
- prev: [[082-max-area-of-island|Max Area of Island]] · next: [[084-surrounded-regions|Surrounded Regions]]

# Longest Increasing Path in a Matrix

**LeetCode 329** · 2-D DP · concepts: [[15-dynamic-programming|dynamic-programming]], [[02-dfs|dfs]]

## Problem

Find the length of the longest **strictly increasing** path in a matrix, moving 4-directionally.

## Approach — DFS with memoization (top-down DP on a grid)

From each cell, the longest increasing path is `1 + max(paths from strictly-greater neighbors)`. Because the path must strictly increase, it can never cycle — so the grid is implicitly a **DAG**, and memoizing each cell's answer makes it O(mn).

```python
def longestIncreasingPath(matrix):
    rows, cols = len(matrix), len(matrix[0])
    memo = {}
    def dfs(r, c):
        if (r, c) in memo:
            return memo[(r, c)]
        best = 1                           # the cell itself
        for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):
            nr, nc = r+dr, c+dc
            if (0 <= nr < rows and 0 <= nc < cols
                    and matrix[nr][nc] > matrix[r][c]):   # strictly increasing
                best = max(best, 1 + dfs(nr, nc))
        memo[(r, c)] = best
        return best
    return max(dfs(r, c) for r in range(rows) for c in range(cols))
```

**Time O(m·n), space O(m·n).**

## Why memoization makes it linear

Without memo, overlapping paths recompute the same cells exponentially. Since strict increase forbids revisiting a cell within a path (no cycles → DAG), each cell's longest-path value is fixed and cached once. **No `visited` set is needed** — the strict-increase condition already prevents cycles, unlike ordinary grid DFS.

## Key insight

**Longest path on an implicit DAG (grid with a monotonic move rule) → DFS + memoization (top-down DP).** The strict-increase constraint is what turns a would-be exponential search into an O(cells) memoized DP and removes the need for cycle-guarding.

## Related
- concepts: [[15-dynamic-programming|dynamic-programming]], [[02-dfs|dfs]], [[13-matrix-traversal|matrix-traversal]]
- prev: [[116-interleaving-string|Interleaving String]] · next: [[118-distinct-subsequences|Distinct Subsequences]]

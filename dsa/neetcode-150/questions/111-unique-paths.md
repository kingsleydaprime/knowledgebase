# Unique Paths

**LeetCode 62** · 2-D DP · concept: [[15-dynamic-programming|dynamic-programming]]

## Problem

A robot at the top-left of an `m × n` grid moves only **right or down**. How many unique paths to the bottom-right?

## The recurrence

Each cell is reached from **above** or from the **left**, so the number of paths to `(r, c)` is the sum of paths to those two: `dp[r][c] = dp[r-1][c] + dp[r][c-1]`. The first row and column are all `1` (one straight-line path).

## Approach — 1-D rolling row (optimal space)

The full grid DP is O(m·n) space, but each row only needs the row above, so a single array suffices — `row[c] += row[c-1]` folds in the "from the left" term while `row[c]` already holds "from above."

```python
def uniquePaths(m, n):
    row = [1] * n                          # top row: one path to each cell
    for _ in range(1, m):
        for c in range(1, n):
            row[c] += row[c - 1]           # from above (old row[c]) + from left (row[c-1])
    return row[-1]
```

**Time O(m·n), space O(n).**

## The 2-D DP starting point

This is the simplest grid DP: state is `(row, col)`, and the answer combines a fixed set of neighbor cells (up + left). Once you can read a recurrence off "which adjacent cells lead here," most grid DP follows. (There's also a closed-form binomial `C(m+n-2, m-1)`, since every path is a fixed arrangement of moves.)

## Key insight

**Grid path-counting → `dp[r][c] = dp[r-1][c] + dp[r][c-1]`, reducible to one rolling row.** The template for 2-D DP where each state depends on a small window of neighbors — the foundation for the harder grid/sequence DPs.

## Related
- concept: [[15-dynamic-programming|dynamic-programming]]
- next: [[112-longest-common-subsequence|Longest Common Subsequence]]

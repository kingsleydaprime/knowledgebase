# Rotate Image

**LeetCode 48** · Math & Geometry · concept: [[14-math-and-geometry|math-and-geometry]]

## Problem

Rotate an `n × n` matrix 90° clockwise **in place** (no second matrix).

## Approach — transpose, then reverse each row (optimal)

The clean decomposition: a 90° clockwise rotation = **transpose** (mirror across the main diagonal) **then reverse each row**. Both steps are in-place swaps.

```python
def rotate(matrix):
    n = len(matrix)
    # transpose: swap matrix[i][j] with matrix[j][i]
    for i in range(n):
        for j in range(i + 1, n):          # upper triangle only
            matrix[i][j], matrix[j][i] = matrix[j][i], matrix[i][j]
    # reverse each row
    for row in matrix:
        row.reverse()
```

**Time O(n²), space O(1).**

## Why transpose + reverse = rotate

Transposing sends element `(i, j)` → `(j, i)`; reversing each row then sends `(j, i)` → `(j, n-1-i)`, which is exactly where a 90° clockwise rotation places the original `(i, j)`. Restricting the transpose loop to `j > i` (the upper triangle) avoids swapping every pair twice back to where it started.

## Key insight

**In-place matrix rotation → decompose the transform into simple whole-matrix operations (transpose + row reverse).** Rather than juggling four-way cyclic swaps, expressing the rotation as two easy passes is cleaner and less bug-prone — the theme of [[14-math-and-geometry|in-place matrix manipulation]].

## Related
- concept: [[14-math-and-geometry|math-and-geometry]]
- next: [[137-spiral-matrix|Spiral Matrix]]

# Spiral Matrix

**LeetCode 54** · Math & Geometry · concept: [[14-math-and-geometry|math-and-geometry]]

## Problem

Return all elements of a matrix in **spiral** order (right across the top, down the right, left across the bottom, up the left, inward).

```
[[1,2,3],[4,5,6],[7,8,9]]  ->  [1,2,3,6,9,8,7,4,5]
```

## Approach — four shrinking boundaries (optimal)

Track `top, bottom, left, right`. Peel one edge at a time and move that boundary inward, until the boundaries cross.

```python
def spiralOrder(matrix):
    res = []
    top, bottom = 0, len(matrix) - 1
    left, right = 0, len(matrix[0]) - 1
    while top <= bottom and left <= right:
        for c in range(left, right + 1):        # top row, L->R
            res.append(matrix[top][c])
        top += 1
        for r in range(top, bottom + 1):        # right col, T->B
            res.append(matrix[r][right])
        right -= 1
        if top <= bottom:                       # bottom row, R->L
            for c in range(right, left - 1, -1):
                res.append(matrix[bottom][c])
            bottom -= 1
        if left <= right:                       # left col, B->T
            for r in range(bottom, top - 1, -1):
                res.append(matrix[r][left])
            left += 1
    return res
```

**Time O(m·n), space O(1)** (excluding output).

## The re-check guards

After walking the top row and right column, the `if top <= bottom` and `if left <= right` guards prevent re-traversing a row/column when the remaining region is a single line (odd dimensions, or a thin rectangle). Skipping these guards double-adds elements — the classic spiral bug.

## Key insight

**Spiral/layered traversal → four boundaries that shrink after each edge, with guards for the single-line remainder.** The mechanics are simple; the *edge cases* (non-square grids, the final row/column) are the whole challenge — a lesson in careful boundary management.

## Related
- concept: [[14-math-and-geometry|math-and-geometry]]
- prev: [[136-rotate-image|Rotate Image]] · next: [[138-set-matrix-zeroes|Set Matrix Zeroes]]

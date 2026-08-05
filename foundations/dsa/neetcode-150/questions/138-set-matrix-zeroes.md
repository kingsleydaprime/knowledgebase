# Set Matrix Zeroes

**LeetCode 73** · Math & Geometry · concept: [[14-math-and-geometry|math-and-geometry]]

## Problem

If a cell is 0, set its entire row and column to 0 — **in place**, ideally O(1) extra space.

## The trap — do it in the wrong order

Zeroing rows/columns as you find zeros corrupts the grid: the new zeros trigger *more* rows/columns to be cleared. You must first **record** which rows and columns need zeroing, then apply.

## Approach — use the first row/column as markers (O(1) space)

Instead of O(m+n) marker arrays, store the flags **in the matrix's own first row and column**. Two extra booleans remember whether the first row / first column were themselves originally zero.

```python
def setZeroes(matrix):
    rows, cols = len(matrix), len(matrix[0])
    first_row_zero = any(matrix[0][c] == 0 for c in range(cols))
    first_col_zero = any(matrix[r][0] == 0 for r in range(rows))

    for r in range(1, rows):                # mark in row 0 / col 0
        for c in range(1, cols):
            if matrix[r][c] == 0:
                matrix[r][0] = 0
                matrix[0][c] = 0

    for r in range(1, rows):                # apply from the markers
        for c in range(1, cols):
            if matrix[r][0] == 0 or matrix[0][c] == 0:
                matrix[r][c] = 0

    if first_row_zero:                      # handle the marker row/col last
        for c in range(cols): matrix[0][c] = 0
    if first_col_zero:
        for r in range(rows): matrix[r][0] = 0
```

**Time O(m·n), space O(1).**

## Reusing the input as scratch space

The first row and column serve as the "which rows/cols to zero" registers — the matrix stores its own metadata. The two booleans are needed because those marker cells can't record their *own* original-zero status (they'd be overwritten). Record-then-apply, in the right order, is essential.

## Key insight

**O(1)-space in-place transforms → reuse part of the input as your bookkeeping.** Folding the marker arrays into row 0 / column 0 is the space-saving trick; the deeper lesson is separating the *detect* phase from the *mutate* phase so writes don't corrupt reads.

## Related
- concept: [[14-math-and-geometry|math-and-geometry]]
- prev: [[137-spiral-matrix|Spiral Matrix]] · next: [[139-happy-number|Happy Number]]

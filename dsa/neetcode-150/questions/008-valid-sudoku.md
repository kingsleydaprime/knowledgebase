# Valid Sudoku

**LeetCode 36** · Arrays & Hashing · concept: [[03-hash-maps|hash-maps]]

## Problem

Determine whether a partially-filled 9×9 Sudoku board is **valid** — no duplicate digit within any row, any column, or any 3×3 sub-box. Empty cells (`"."`) are ignored, and you only validate what's filled; you don't solve it.

## The idea — three families of "seen" sets

Validity is three independent no-duplicate constraints, one per structure. So track, for each filled cell, whether its digit has already appeared in its **row**, its **column**, or its **box** — each a hash set membership check ([[001-contains-duplicate|Contains Duplicate]], applied 27 times over).

The only trick is **indexing the 3×3 box**. The box a cell belongs to is `(row // 3, col // 3)` — integer division collapses each 3-wide band to a single index, giving box coordinates `(0..2, 0..2)`.

```python
from collections import defaultdict

def isValidSudoku(board):
    rows = defaultdict(set)
    cols = defaultdict(set)
    boxes = defaultdict(set)            # keyed by (r // 3, c // 3)

    for r in range(9):
        for c in range(9):
            val = board[r][c]
            if val == ".":
                continue
            box = (r // 3, c // 3)
            if val in rows[r] or val in cols[c] or val in boxes[box]:
                return False           # duplicate in some unit
            rows[r].add(val)
            cols[c].add(val)
            boxes[box].add(val)
    return True
```

## Why `(r // 3, c // 3)` is the whole puzzle

Cell `(4, 7)` sits in box `(1, 2)`; cell `(5, 8)` also maps to `(1, 2)` — same box, so they share a set. Floor-dividing the coordinate by the box size is the standard way to bucket a grid into blocks, and it's the one line people fumble. (An equivalent single-integer key is `(r // 3) * 3 + c // 3`.)

## Complexity

| | Time | Space |
|---|---|---|
| This solution | O(1) | O(1) |

The board is fixed at 9×9 = 81 cells, so it's technically constant — but the *shape* of the work is O(cells), and the sets hold at most 9 digits each. One pass, no re-scanning.

## Key insight

**Multiple simultaneous "no duplicates" constraints → one hash set per constraint unit.** Sudoku is [[001-contains-duplicate|Contains Duplicate]] run in parallel across 9 rows + 9 columns + 9 boxes. The reusable trick is the block index `coordinate // block_size`, which maps any grid cell to the block that contains it — useful anywhere a grid is partitioned into tiles.

## Related
- concept: [[03-hash-maps|hash-maps]]
- builds on: [[001-contains-duplicate|Contains Duplicate]] (set membership)
- prev: [[007-product-of-array-except-self|Product of Array Except Self]] · next: [[009-longest-consecutive-sequence|Longest Consecutive Sequence]]

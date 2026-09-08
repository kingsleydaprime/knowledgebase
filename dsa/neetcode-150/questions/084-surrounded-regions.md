# Surrounded Regions

**LeetCode 130** · Graphs · concept: [[13-matrix-traversal|matrix-traversal]]

## Problem

Capture regions of `"O"` fully surrounded by `"X"` (flip them to `"X"`). An `"O"` connected to the **border** is safe and stays.

## Approach — mark border-connected O's safe first (optimal)

Instead of testing each region for "is it surrounded?", invert: any `"O"` reachable from the **edge** can't be captured. Flood from every border `"O"`, marking those safe; then every remaining `"O"` is surrounded → flip it.

```python
def solve(board):
    if not board:
        return
    rows, cols = len(board), len(board[0])
    def dfs(r, c):
        if (r < 0 or r >= rows or c < 0 or c >= cols
                or board[r][c] != "O"):
            return
        board[r][c] = "S"                  # safe (border-connected)
        dfs(r+1,c); dfs(r-1,c); dfs(r,c+1); dfs(r,c-1)

    for r in range(rows):                  # launch from all border O's
        dfs(r, 0); dfs(r, cols - 1)
    for c in range(cols):
        dfs(0, c); dfs(rows - 1, c)

    for r in range(rows):
        for c in range(cols):
            if board[r][c] == "O":
                board[r][c] = "X"          # surrounded -> capture
            elif board[r][c] == "S":
                board[r][c] = "O"          # restore safe cells
```

**Time O(rows · cols), space O(rows · cols).**

## Invert the question

"Which regions are surrounded?" is awkward; "which regions touch the border?" is a simple flood from the edges. Mark the safe ones, then everything left is by definition captured. Reframing "surrounded" as "not border-connected" is the whole insight.

## Key insight

**Border-dependent region problems → flood from the border, mark the exceptions, then process the rest.** Rather than proving each region is enclosed, you find the ones that *aren't* and flip the remainder — the same reverse-from-the-boundary idea as [[083-pacific-atlantic-water-flow|Pacific Atlantic]].

## Related
- concept: [[13-matrix-traversal|matrix-traversal]]
- prev: [[083-pacific-atlantic-water-flow|Pacific Atlantic Water Flow]] · next: [[085-rotting-oranges|Rotting Oranges]]

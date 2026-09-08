# N-Queens

**LeetCode 51** · Backtracking · concept: [[14-backtracking|backtracking]]

## Problem

Place `n` queens on an `n × n` board so none attack each other; return all distinct solutions.

## Approach — place one queen per row, track attacked columns/diagonals (optimal)

Since each row holds exactly one queen, recurse **row by row**, trying each column. A placement is legal if its column and both diagonals are unused. Track three sets for O(1) conflict checks.

```python
def solveNQueens(n):
    res = []
    board = [["."] * n for _ in range(n)]
    cols = set()
    diag = set()          # r - c constant along a ↘ diagonal
    anti = set()          # r + c constant along a ↙ diagonal

    def backtrack(r):
        if r == n:
            res.append(["".join(row) for row in board])
            return
        for c in range(n):
            if c in cols or (r - c) in diag or (r + c) in anti:
                continue                  # attacked -> skip
            cols.add(c); diag.add(r - c); anti.add(r + c)
            board[r][c] = "Q"
            backtrack(r + 1)
            board[r][c] = "."             # undo
            cols.remove(c); diag.remove(r - c); anti.remove(r + c)
    backtrack(0)
    return res
```

**Time O(n!), space O(n²)** for the board.

## The diagonal encodings

The elegant part: cells on the same **↘ diagonal share `r − c`**, and cells on the same **↙ diagonal share `r + c`**. Those two constants turn "is this diagonal attacked?" into O(1) set lookups, replacing an O(n) scan. Placing one queen per row automatically handles the row constraint.

## Key insight

**Constraint-satisfaction placement → backtrack one unit (row) at a time, with O(1) conflict sets for each constraint dimension.** The `r−c` / `r+c` diagonal trick is the classic encoding of a geometric constraint into a hashable key — the technique that makes the pruning cheap.

## Related
- concept: [[14-backtracking|backtracking]]
- prev: [[078-letter-combinations-of-a-phone-number|Letter Combinations]] — end of Backtracking
- next category: Graphs

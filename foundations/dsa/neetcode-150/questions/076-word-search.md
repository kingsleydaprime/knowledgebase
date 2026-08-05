# Word Search

**LeetCode 79** · Backtracking · concepts: [[14-backtracking|backtracking]], [[13-matrix-traversal|matrix-traversal]]

## Problem

Given a character `board` and a `word`, return `true` if the word can be formed along a path of **adjacent** cells, each cell used at most once.

```
board = [["A","B","C","E"],
         ["S","F","C","S"],
         ["A","D","E","E"]], word = "ABCCED"  ->  true
```

## Approach — DFS backtracking on the grid (optimal)

From each cell, DFS matching the word character by character. Mark a used cell temporarily, recurse into its four neighbors, then **restore** it on the way back so other paths can reuse it.

```python
def exist(board, word):
    rows, cols = len(board), len(board[0])
    def dfs(r, c, i):
        if i == len(word):
            return True                    # matched all characters
        if (r < 0 or r >= rows or c < 0 or c >= cols
                or board[r][c] != word[i]):
            return False
        board[r][c] = "#"                  # mark visited (avoid reuse)
        found = (dfs(r+1, c, i+1) or dfs(r-1, c, i+1)
                 or dfs(r, c+1, i+1) or dfs(r, c-1, i+1))
        board[r][c] = word[i]              # restore (backtrack)
        return found
    for r in range(rows):
        for c in range(cols):
            if dfs(r, c, 0):
                return True
    return False
```

**Time O(rows · cols · 4^L), space O(L)** recursion (L = word length).

## Marking in place instead of a visited set

Overwriting `board[r][c] = "#"` during the recursion and restoring it after is the backtracking way to enforce "each cell once" without a separate `visited` structure — the *undo* step is what makes the same cell available to other branches. Forgetting to restore breaks all sibling paths.

## Key insight

**Path search on a grid with no-reuse → DFS + in-place mark/undo.** It fuses [[13-matrix-traversal|grid DFS]] with backtracking's choose/undo; the temporary marking is the reusable trick (and the seed of [[063-word-search-ii|Word Search II]]'s trie-guided version).

## Related
- concepts: [[14-backtracking|backtracking]], [[13-matrix-traversal|matrix-traversal]]
- leads to: [[063-word-search-ii|Word Search II]]
- prev: [[075-combination-sum-ii|Combination Sum II]] · next: [[077-palindrome-partitioning|Palindrome Partitioning]]

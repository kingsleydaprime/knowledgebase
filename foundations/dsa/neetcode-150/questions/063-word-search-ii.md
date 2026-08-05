# Word Search II

**LeetCode 212** · Tries · concepts: [[09-tries|tries]], [[14-backtracking|backtracking]]

## Problem

Given a character `board` and a list of `words`, return all words that can be formed by a path of **adjacent** cells (each cell used once per word).

## Why brute force fails

Running a separate grid DFS for each word is O(words × cells × 4^L) — hopeless when there are many words. The words share prefixes, and we should exploit that.

## Approach — build a trie of the words, DFS the grid through it (optimal)

Put **all words into one [[09-tries|trie]]**, then run a single [[14-backtracking|backtracking]] DFS from every cell, walking the board and the trie **in lockstep**: only continue into a cell if its character is a child of the current trie node. When you reach a node marking a word end, record that word. The trie prunes dead ends across *all* words at once.

```python
def findWords(board, words):
    root = {}
    for w in words:                          # build the trie
        node = root
        for ch in w:
            node = node.setdefault(ch, {})
        node["$"] = w                        # store the full word at its end node

    rows, cols = len(board), len(board[0])
    found = set()

    def dfs(r, c, node):
        ch = board[r][c]
        if ch not in node:
            return
        nxt = node[ch]
        if "$" in nxt:
            found.add(nxt["$"])              # complete word matched
        board[r][c] = "#"                    # mark visited
        for dr, dc in ((0,1),(0,-1),(1,0),(-1,0)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and board[nr][nc] != "#":
                dfs(nr, nc, nxt)
        board[r][c] = ch                     # undo (backtrack)

    for r in range(rows):
        for c in range(cols):
            dfs(r, c, root)
    return list(found)
```

**Time** roughly O(cells × 4^maxWordLen) but with heavy trie pruning; **space** O(total characters in words).

## Why the trie flips the complexity

Instead of "for each word, search the grid," it's "search the grid once, guided by all words simultaneously." At every cell the trie instantly says whether *any* remaining word can continue that way — so a dead prefix kills the branch for every word at once. Pruning matched words out of the trie further speeds repeated boards.

## Key insight

**Multi-pattern search on a grid → one trie of the patterns + a single backtracking DFS driven by it.** The trie turns "which of many words fits here?" into an O(1) child check, and backtracking (mark `#`, recurse, restore) explores paths without a separate visited set. The premier trie-meets-backtracking problem.

## Related
- concepts: [[09-tries|tries]], [[14-backtracking|backtracking]], [[13-matrix-traversal|matrix-traversal]]
- prev: [[062-design-add-and-search-words-data-structure|Design Add and Search Words]] — end of Tries
- next category: Heap / Priority Queue

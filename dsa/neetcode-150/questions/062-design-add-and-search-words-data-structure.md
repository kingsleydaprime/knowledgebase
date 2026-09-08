# Design Add and Search Words Data Structure

**LeetCode 211** · Tries · concepts: [[09-tries|tries]], [[02-dfs|dfs]]

## Problem

Support `addWord(word)` and `search(word)`, where `search` may contain `.` as a **wildcard** matching any single character.

```
addWord("bad"); addWord("dad")
search("pad") -> false ; search(".ad") -> true ; search("b..") -> true
```

## Approach — trie + branching DFS on `.` (optimal)

`addWord` is a plain [[061-implement-trie-prefix-tree|trie insert]]. `search` becomes a DFS: at a concrete character, follow just that child; at a `.`, recurse into **every** child.

```python
class WordDictionary:
    def __init__(self):
        self.root = {}                       # nested dicts; "$" marks a word end

    def addWord(self, word):
        node = self.root
        for ch in word:
            node = node.setdefault(ch, {})
        node["$"] = True

    def search(self, word):
        def dfs(node, i):
            if i == len(word):
                return "$" in node
            ch = word[i]
            if ch == ".":
                return any(dfs(child, i + 1)          # try every child
                           for k, child in node.items() if k != "$")
            return ch in node and dfs(node[ch], i + 1)
        return dfs(self.root, 0)
```

**Time:** `addWord` O(L); `search` O(L) with no wildcards, but up to **O(26^(number of dots) · path)** in the worst case (all dots) — the branching factor is the alphabet at each `.`.

## Why the wildcard forces DFS

A concrete character means one path; a `.` means the search **splits** into every possible next character. That branching is exactly a depth-first search over the trie — a single linear walk becomes a tree of walks. Concrete characters between dots prune hard, so realistic inputs stay fast.

## Key insight

**Wildcards turn a trie lookup into a DFS: fixed char → one branch, wildcard → all branches.** The trie provides the structure; DFS provides the "try all possibilities" at each unknown — a pairing that recurs whenever partial-match search meets a prefix structure.

## Related
- concepts: [[09-tries|tries]], [[02-dfs|dfs]]
- builds on: [[061-implement-trie-prefix-tree|Implement Trie]]
- prev: [[061-implement-trie-prefix-tree|Implement Trie]] · next: [[063-word-search-ii|Word Search II]]

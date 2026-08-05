# Word Ladder

**LeetCode 127** · Graphs · concepts: [[03-bfs|bfs]], [[12-bfs-pattern|bfs-pattern]]

## Problem

Given `beginWord`, `endWord`, and a `wordList`, return the length of the **shortest** transformation sequence changing one letter at a time, where every intermediate word is in the list (0 if impossible).

```
"hit" -> "hot" -> "dot" -> "dog" -> "cog"  ->  5
```

## The graph view — words are nodes, one-letter-changes are edges

Each word is a node; two words are adjacent if they differ by exactly one letter. "Shortest transformation" = **shortest path in an unweighted graph** = [[03-bfs|BFS]].

## Approach — BFS with wildcard adjacency (optimal)

Enumerating neighbors by comparing against all other words is O(N²). Instead, precompute **patterns**: `hot` → `*ot`, `h*t`, `ho*`. Words sharing a pattern differ by one letter, so a pattern → words map gives O(1) neighbor lookup.

```python
from collections import deque, defaultdict

def ladderLength(beginWord, endWord, wordList):
    words = set(wordList)
    if endWord not in words:
        return 0
    patterns = defaultdict(list)           # "*ot" -> ["hot","dot","lot",...]
    for w in words | {beginWord}:
        for i in range(len(w)):
            patterns[w[:i] + "*" + w[i+1:]].append(w)

    queue = deque([(beginWord, 1)])
    visited = {beginWord}
    while queue:
        word, steps = queue.popleft()
        if word == endWord:
            return steps
        for i in range(len(word)):
            for nei in patterns[word[:i] + "*" + word[i+1:]]:
                if nei not in visited:
                    visited.add(nei)
                    queue.append((nei, steps + 1))
    return 0
```

**Time O(N · L²) (L = word length), space O(N · L²).**

## Why BFS, and why patterns

BFS explores by distance, so the first time it reaches `endWord` is the shortest ladder — DFS could find a long path first. The wildcard pattern index replaces an O(N²) all-pairs neighbor scan with grouped O(1) lookups, the key optimization. (Bidirectional BFS from both ends is a further speedup.)

## Key insight

**"Fewest one-step transformations" → model states as graph nodes and run BFS.** The creative parts are *seeing* the implicit graph (words + one-letter edges) and building adjacency cheaply (wildcard patterns) rather than comparing all pairs.

## Related
- concepts: [[03-bfs|bfs]], [[12-bfs-pattern|bfs-pattern]]
- prev: [[091-graph-valid-tree|Graph Valid Tree]] — end of Graphs
- next category: Advanced Graphs

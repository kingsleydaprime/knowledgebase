# Alien Dictionary

**LeetCode 269** · Advanced Graphs · concept: [[11-topological-sort|topological-sort]]

## Problem

Given words sorted by an unknown alphabet's rules, derive a possible ordering of the letters. Return `""` if the ordering is invalid.

```
["wrt","wrf","er","ett","rftt"]  ->  "wertf"
```

## The idea — build precedence edges, then topologically sort

Adjacent words in a sorted list reveal **one** ordering fact: the first differing character gives `c1 → c2` (c1 comes before c2). Collect these edges over all adjacent pairs, then [[11-topological-sort|topologically sort]] the letters.

```python
from collections import defaultdict, deque

def alienOrder(words):
    graph = {c: set() for w in words for c in w}
    indegree = {c: 0 for c in graph}
    for a, b in zip(words, words[1:]):
        for x, y in zip(a, b):
            if x != y:
                if y not in graph[x]:
                    graph[x].add(y)
                    indegree[y] += 1
                break                      # only the FIRST diff gives an edge
        else:                              # no diff found...
            if len(a) > len(b):
                return ""                  # "abc" before "ab" is invalid ordering

    queue = deque(c for c in indegree if indegree[c] == 0)
    order = []
    while queue:
        c = queue.popleft()
        order.append(c)
        for nxt in graph[c]:
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                queue.append(nxt)
    return "".join(order) if len(order) == len(graph) else ""   # cycle -> invalid
```

**Time O(total characters), space O(1)** (alphabet-bounded).

## The two hard parts (not the sort)

1. **Only the first differing character** yields an edge — later characters tell you nothing about order once the first difference is fixed.
2. **The prefix trap** — if word A is longer than B but B is A's prefix (`"abc"` before `"ab"`), the input is inconsistent → `""`.

The topological sort itself is routine; correctly *building the graph* is where this problem lives.

## Key insight

**Turn ordering evidence into precedence edges, then topological-sort.** Alien Dictionary is the classic "extract a DAG from constraints, then order it" — the modeling (which pairs give which edges, and the invalid cases) is the challenge, not the sort.

## Related
- concept: [[11-topological-sort|topological-sort]]
- prev: [[096-swim-in-rising-water|Swim in Rising Water]] · next: [[098-cheapest-flights-within-k-stops|Cheapest Flights Within K Stops]]

# Reconstruct Itinerary

**LeetCode 332** · Advanced Graphs · concept: [[02-dfs|dfs]]

## Problem

Given airline tickets `[from, to]`, reconstruct the itinerary starting at `"JFK"`, using **every ticket exactly once**. If multiple valid itineraries exist, return the one with the smallest **lexical** order.

## The idea — Eulerian path via Hierholzer's algorithm

Using every edge exactly once is an **Eulerian path**. Hierholzer's algorithm builds it with a post-order DFS: sort each node's destinations lexically, greedily fly the smallest available edge, and **prepend** nodes to the route as the DFS *retreats* (a node is added only once it has no unused outgoing edges).

```python
from collections import defaultdict

def findItinerary(tickets):
    graph = defaultdict(list)
    for src, dst in sorted(tickets, reverse=True):   # reverse so pop() gives smallest
        graph[src].append(dst)

    route = []
    def dfs(airport):
        while graph[airport]:
            dfs(graph[airport].pop())    # fly the lexically smallest remaining edge
        route.append(airport)            # add on the way back (post-order)
    dfs("JFK")
    return route[::-1]                    # reverse the post-order
```

**Time O(E log E) (the sort), space O(E).**

## Why post-order, not a plain greedy path

A naive "always take the smallest edge" can strand you at a dead-end with tickets unused. Hierholzer's fixes this: a node is only committed to the route once *all* its edges are consumed, so a dead-end airport is appended first and ends up **last** after the final reverse. Appending on the DFS retreat is what guarantees every edge is used.

## Key insight

**"Use every edge exactly once" → Eulerian path via Hierholzer's post-order DFS.** The counterintuitive move — record nodes as the DFS unwinds, then reverse — handles dead-ends automatically, which greedy forward construction can't.

## Related
- concept: [[02-dfs|dfs]], [[06-graphs|graphs]]
- next: [[094-min-cost-to-connect-all-points|Min Cost to Connect All Points]]

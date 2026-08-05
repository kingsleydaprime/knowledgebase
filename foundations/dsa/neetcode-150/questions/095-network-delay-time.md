# Network Delay Time

**LeetCode 743** · Advanced Graphs · concept: [[06-dijkstra|dijkstra]]

## Problem

A signal starts at node `k` in a weighted **directed** graph. Return the time for **all** nodes to receive it (the max shortest-path distance), or `-1` if some node is unreachable.

## Approach — Dijkstra from the source (optimal)

Single-source shortest paths with non-negative weights → [[06-dijkstra|Dijkstra]]. Run it from `k`; the answer is the **maximum** of the shortest distances (the last node to hear the signal), or `-1` if any node is never reached.

```python
import heapq
from collections import defaultdict

def networkDelayTime(times, n, k):
    graph = defaultdict(list)
    for u, v, w in times:
        graph[u].append((v, w))

    dist = {}
    heap = [(0, k)]                        # (time so far, node)
    while heap:
        t, node = heapq.heappop(heap)
        if node in dist:
            continue                       # already finalized (lazy deletion)
        dist[node] = t
        for nei, w in graph[node]:
            if nei not in dist:
                heapq.heappush(heap, (t + w, nei))

    return max(dist.values()) if len(dist) == n else -1
```

**Time O(E log V), space O(V + E).**

## Why the max, and why Dijkstra

Dijkstra pops nodes in increasing distance, finalizing each shortest path the first time it's dequeued. "All nodes received it" means waiting for the **slowest** shortest path — hence `max`. Unreached nodes (dist size < n) mean the signal can't cover the network → `-1`.

## Key insight

**Single-source shortest paths, non-negative weights → Dijkstra (greedy + min-heap).** "Time for a signal to reach everyone" is a thin story over shortest-paths; the aggregate you report (max over nodes) is the only twist.

## Related
- concept: [[06-dijkstra|dijkstra]], [[08-heaps|heaps]]
- prev: [[094-min-cost-to-connect-all-points|Min Cost to Connect All Points]] · next: [[096-swim-in-rising-water|Swim in Rising Water]]

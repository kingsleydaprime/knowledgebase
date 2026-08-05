# Cheapest Flights Within K Stops

**LeetCode 787** · Advanced Graphs · concept: [[06-dijkstra|dijkstra]]

## Problem

Find the cheapest price from `src` to `dst` using **at most `k` stops** (k+1 edges), or `-1`.

## Why plain Dijkstra doesn't fit

Standard Dijkstra minimizes cost with no bound on edge count — but here a cheaper path using too many stops is invalid, and Dijkstra's "finalize on first pop" can lock in a path that violates the stop limit. The stop constraint is a second dimension.

## Approach — Bellman-Ford, bounded to k+1 relaxations (optimal)

Relax **all edges exactly `k+1` times**. After `i` rounds, `dist[v]` holds the cheapest cost to `v` using at most `i` edges. Using a **snapshot** of distances each round prevents an edge added this round from being reused within the same round (which would exceed the stop budget).

```python
def findCheapestPrice(n, flights, src, dst, k):
    dist = [float("inf")] * n
    dist[src] = 0
    for _ in range(k + 1):                 # at most k stops = k+1 edges
        snapshot = dist[:]                 # freeze this round's starting distances
        for u, v, w in flights:
            if dist[u] != float("inf") and dist[u] + w < snapshot[v]:
                snapshot[v] = dist[u] + w
        dist = snapshot
    return dist[dst] if dist[dst] != float("inf") else -1
```

**Time O(k · E), space O(n).**

## The snapshot is the whole trick

Relaxing against a **frozen copy** guarantees each round adds at most one edge to any path — so after `k+1` rounds, every distance uses ≤ k+1 edges. Relaxing in place would let a path grow by several edges in a single round, silently exceeding the stop limit. This bounded Bellman-Ford is the model answer.

## Key insight

**Shortest path with an edge-count (hop) constraint → Bellman-Ford bounded to that many rounds, relaxing against a per-round snapshot.** When a second constraint (stops) breaks Dijkstra's greedy finalization, Bellman-Ford's round structure naturally encodes "paths of ≤ i edges."

## Related
- concept: [[06-dijkstra|dijkstra]] (and Bellman-Ford as its constraint-friendly cousin)
- prev: [[097-alien-dictionary|Alien Dictionary]] — end of Advanced Graphs
- next category: 1-D Dynamic Programming

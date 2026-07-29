# Dijkstra's Algorithm

Dijkstra finds the shortest path from a source node to every other node in a **weighted** graph (non-negative weights only). It's [[03-bfs|BFS]] generalized: BFS finds shortest paths by hops because every edge "costs" the same one step; Dijkstra finds shortest paths by total weight, by always expanding whichever unvisited node currently has the smallest known distance instead of just whichever was discovered first.

## Why BFS isn't enough here

BFS's shortest-path guarantee relies on every edge having equal weight — the node distance in the queue mirrors number of hops exactly. The moment edges have different weights, "fewest hops" and "lowest total cost" stop being the same thing, and a plain queue can't tell you which frontier node is actually closest. Dijkstra swaps the queue for a **min-heap keyed by cumulative distance**, so the next node popped is always the genuinely closest unvisited one — the same "always take the smallest" logic as [[07-top-k-elements|a heap]], applied to distances instead of values.

## How it works

1. Set distance to the source as 0, everything else as infinity.
2. Push `(0, source)` onto a min-heap.
3. Pop the smallest-distance node. For each neighbor, compute `distance_to_node + edge_weight` — if that's smaller than the neighbor's currently known distance, update it (this update step is called **relaxation**) and push the neighbor with its new distance.
4. Repeat until the heap is empty.

```python
import heapq

def dijkstra(graph, source):
    # graph: {node: [(neighbor, weight), ...]}
    distances = {node: float("inf") for node in graph}
    distances[source] = 0
    heap = [(0, source)]

    while heap:
        dist, node = heapq.heappop(heap)
        if dist > distances[node]:
            continue                     # stale entry — a shorter path was already found
        for neighbor, weight in graph[node]:
            new_dist = dist + weight
            if new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                heapq.heappush(heap, (new_dist, neighbor))
    return distances
```

```
graph:              A --2-- B
                     \       \
                      6       3
                       \       \
                        C --1-- D

dijkstra(graph, "A"):
start: dist={A:0, B:inf, C:inf, D:inf}, heap=[(0,A)]
pop A(0): relax B -> 2, relax C -> 6      heap=[(2,B),(6,C)]
pop B(2): relax D -> 2+3=5                heap=[(5,D),(6,C)]
pop D(5): relax C -> 5+1=6 (not < 6, no update)
pop C(6): no better relaxations

final: {A:0, B:2, C:6, D:5}
```

## Why the `if dist > distances[node]: continue` line matters

A node can be pushed onto the heap multiple times, once per time a shorter path to it is discovered — the heap doesn't support "update the priority of an existing entry" directly, so old, now-stale `(distance, node)` pairs just sit in the heap alongside the newer, better one. By the time a stale entry is popped, `distances[node]` has already been improved past it, so this check is what makes it safe to just skip it rather than reprocessing a node with outdated distance information.

## Complexity

O((V + E) log V) with a binary heap — every edge can trigger a push (E log V), and every vertex is popped once (V log V). This is the same shape of bound as [[03-bfs|bfs]]'s O(V + E), with the extra log V factor coming directly from heap operations replacing plain queue operations.

## Gotchas

- **Negative edge weights break it.** Dijkstra's greedy assumption — once a node is popped, its distance is final — only holds if every future edge can only add non-negative distance. A negative edge could make a longer-looking path actually cheaper *after* a node's been finalized, which Dijkstra has no mechanism to revisit. Bellman-Ford handles negative weights (at O(V·E) cost) — worth its own note if that comes up, not covered here.
- Forgetting the stale-entry check (`if dist > distances[node]: continue`) doesn't produce wrong answers by itself (relaxation only ever improves distances), but it does waste work reprocessing a node's neighbors using an already-outdated distance.
- Dijkstra gives shortest distance to **every** reachable node from the source, not just one target — if you only need one target's distance, you can stop early the moment that target is popped, but the algorithm doesn't require knowing the target in advance.

## Related
- [[03-bfs|bfs]] — the unweighted special case
- [[07-top-k-elements|top-k-elements]] — same min-heap mechanics, different use
- [[06-graphs|graphs]]

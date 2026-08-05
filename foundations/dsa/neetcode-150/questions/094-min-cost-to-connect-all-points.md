# Min Cost to Connect All Points

**LeetCode 1584** · Advanced Graphs · concept: [[12-minimum-spanning-tree|minimum-spanning-tree]]

## Problem

Given points on a plane, connect them all with minimum total cost, where the cost between two points is their **Manhattan distance**. Return the minimum total.

## The reframing — minimum spanning tree

The points form a complete weighted graph (every pair connectable); the cheapest way to connect them all with no redundancy is the **[[12-minimum-spanning-tree|MST]]**.

## Approach — Prim's algorithm (heap)

Grow a tree from one point, each step adding the **cheapest edge to a point not yet in the tree**, using a [[08-heaps|min-heap]] of candidate edges. Prim's avoids materializing all O(n²) edges up front.

```python
import heapq

def minCostConnectPoints(points):
    n = len(points)
    visited = set()
    heap = [(0, 0)]                        # (cost, point index)
    total = 0
    while len(visited) < n:
        cost, i = heapq.heappop(heap)
        if i in visited:
            continue                       # stale entry (lazy deletion)
        visited.add(i)
        total += cost
        for j in range(n):                 # push edges to all unvisited points
            if j not in visited:
                d = abs(points[i][0]-points[j][0]) + abs(points[i][1]-points[j][1])
                heapq.heappush(heap, (d, j))
    return total
```

**Time O(n² log n), space O(n²).** Kruskal's (sort all edges + [[10-union-find|Union-Find]]) also works, at O(n² log n) for the edge sort.

## Prim's vs Kruskal's here

Prim's fits the dense complete graph — it grows outward without enumerating all n² edges at once. Kruskal's would sort all ~n²/2 edges then union greedily. Both are MST; the choice is representation, and both rely on the **cut property** (the cheapest edge crossing "in-tree vs out" is safe).

## Key insight

**"Connect everything as cheaply as possible" → minimum spanning tree** (Prim's with a heap, or Kruskal's with Union-Find). Spotting that "connect all points, minimize total" *is* an MST is the entire problem.

## Related
- concepts: [[12-minimum-spanning-tree|MST]], [[08-heaps|heaps]], [[10-union-find|union-find]]
- prev: [[093-reconstruct-itinerary|Reconstruct Itinerary]] · next: [[095-network-delay-time|Network Delay Time]]

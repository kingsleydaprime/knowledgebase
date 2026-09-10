# Module: Dijkstra's Algorithm (Weighted Shortest Path)

Welcome to the **Dijkstra's Algorithm** module. Dijkstra finds the shortest path from a starting source node to every other node in a **weighted graph with non-negative edge weights**.

While [[03-bfs|BFS]] finds shortest paths in terms of **number of hops** (unweighted edges), Dijkstra finds shortest paths in terms of **total cumulative cost/distance** (weighted edges).

---

## Before you start

- You know BFS and why it stops working on weighted graphs — [[03-bfs|breadth-first search]].
- You know what a min-heap gives you — [[08-heaps|heaps]].
- You know weighted-graph vocabulary — [[06-graphs/01-what-a-graph-is|what a graph is]].

**After this lesson you will be able to:**

1. Implement Dijkstra with a priority queue, and reconstruct the path.
2. Explain the **greedy invariant** that makes it correct — and the exact assumption it needs.
3. **Demonstrate it failing** on a graph with a negative edge, and say why the failure is structural rather than a bug.
4. Choose between Dijkstra, BFS, Bellman–Ford and A* from the graph's properties.

**Study route:** read 1–5, attempt the prediction in section 4, then run the lab. Block 3 breaks it on purpose.

---

## 1. Real-World Motivation & Physical Metaphors

Imagine planning a **GPS Driving Route**:

```
                       [ Highway: 100 miles, 65 mph (Cost: 90 mins) ]
  ( City A ) ---------------------------------------------------------> ( City B )
      |                                                                     ^
      +---> [ Local Road: 5 miles ] ---> ( Village C ) ---> [ Local Road: 5 miles ]
                                        (Cost: 15 mins)
```

- **BFS Strategy**: Picks the 1-hop direct highway route (100 miles, taking 90 minutes).
- **Dijkstra Strategy**: Evaluates total travel time (weight) and picks the 2-hop route through Village C (10 miles total, taking only 30 minutes).

### Production Applications:
1. **GPS Navigation (Google Maps / Waze)**: Calculating fastest driving routes considering speed limits and traffic delay weights.
2. **Network IP Routing (OSPF Protocol)**: Routing data packets across servers based on latency.
3. **Flight Booking Search**: Finding the cheapest flight combinations between airports.

---

## 2. Plain-English Terminology & Concept Table

| Term | Plain-English Definition | Example / Analogy |
| :--- | :--- | :--- |
| **Edge Weight** | The numeric cost (distance, time, fee) required to travel across an edge. | Toll road price or travel time. |
| **Relaxation** | Updating the shortest known distance to a node if a cheaper path is discovered. | Finding a shortcut road. |
| **Min-Heap (Priority Queue)** | Data structure that always pops the unvisited node with the smallest cumulative distance. | Always processing the closest node next. |
| **Stale Entry** | An outdated `(distance, node)` pair left in the heap after a shorter path to that node was found. | Old, expired route suggestion. |

---

## 3. Technical Deep Dive: Dijkstra's Algorithm

### Step-by-Step Mechanics
1. Initialize `distances[source] = 0` and `distances[node] = infinity` for all other nodes.
2. Push `(0, source)` into a **Min-Heap**.
3. Pop the node with the smallest distance `dist`. If `dist > distances[node]`, skip it (**Stale Entry**).
4. For each neighbor, calculate candidate distance: `new_dist = dist + weight`.
5. If `new_dist < distances[neighbor]`, update `distances[neighbor] = new_dist` (**Relaxation**) and push `(new_dist, neighbor)` into the min-heap.

---

### Python Code Implementation
```python
import heapq

def dijkstra(graph: dict, source: str) -> dict:
    """Finds the shortest distance from source to all nodes in a weighted graph.
    
    graph format: { 'A': [('B', 2), ('C', 5)], ... }
    """
    # 1. Initialize distance map with infinity
    distances = {node: float('inf') for node in graph}
    distances[source] = 0
    
    # 2. Min-heap stores tuples of (cumulative_distance, node)
    min_heap = [(0, source)]
    
    while min_heap:
        current_dist, current_node = heapq.heappop(min_heap)
        
        # Lazy Deletion / Stale Entry check:
        # If we already found a shorter path to current_node, skip processing!
        if current_dist > distances[current_node]:
            continue
            
        # 3. Relax edges to neighbors
        for neighbor, weight in graph[current_node]:
            new_dist = current_dist + weight
            
            if new_dist < distances[neighbor]:
                distances[neighbor] = new_dist  # Relaxation step
                heapq.heappush(min_heap, (new_dist, neighbor))
                
    return distances
```

---

## 4. Why Negative Edge Weights Break Dijkstra

> [!CAUTION]
> **Dijkstra FAILS on Negative Edge Weights!**
> Dijkstra makes a **Greedy Assumption**: Once a node is popped from the min-heap, its calculated distance is final and will never decrease. 
> 
> If negative edge weights exist, a longer path with 10 hops could suddenly become cheaper later if it contains a `-100` weight edge! For graphs with negative weights, use the **Bellman-Ford Algorithm** ($O(V \cdot E)$).

---

## 5. Time & Space Complexity Summary

| Metric | Complexity | Explanation |
| :--- | :--- | :--- |
| **Time Complexity** | **$O((V + E) \log V)$** | Every vertex ($V$) is popped from the heap, and every edge ($E$) can trigger a heap push ($O(\log V)$). |
| **Space Complexity** | **$O(V + E)$** | Graph adjacency list $O(V + E)$ plus heap storage $O(V)$. |

---

## Implementation — complete runnable example

**Runnable example:** save as `dijkstra_lab.py` in any empty directory and run `python3 dijkstra_lab.py`. Standard library only; writes no files.

```python
"""Dijkstra: the algorithm, the path, and the assumption it cannot do without."""
import heapq
from collections import defaultdict


def build(edges, directed=False):
    adj = defaultdict(list)
    for u, v, w in edges:
        adj[u].append((v, w))
        if not directed:
            adj[v].append((u, w))
        else:
            adj.setdefault(v, [])
    return adj


def dijkstra(adj, start):
    """Returns (distances, parents). Lazy deletion: stale heap entries are skipped."""
    dist = {start: 0}
    parent = {start: None}
    done = set()
    pq = [(0, start)]
    pops = 0
    while pq:
        d, v = heapq.heappop(pq)
        pops += 1
        if v in done:
            continue                     # a stale entry from before v was improved
        done.add(v)
        for w, weight in adj.get(v, []):
            if w in done:
                continue                 # FINALISED: Dijkstra never revises it.
            nd = d + weight
            if w not in dist or nd < dist[w]:
                dist[w] = nd
                parent[w] = v
                heapq.heappush(pq, (nd, w))
    return dist, parent, pops


def path_to(parent, goal):
    if goal not in parent:
        return None
    out = [goal]
    while parent[out[-1]] is not None:
        out.append(parent[out[-1]])
    return out[::-1]


def brute_force_shortest(adj, start, goal):
    """Every simple path, exhaustively. Correct, exponential, and a good oracle."""
    best = [None, float("inf")]

    def walk(v, seen, cost, path):
        if cost >= best[1]:
            return
        if v == goal:
            best[0], best[1] = list(path), cost
            return
        for w, weight in adj.get(v, []):
            if w not in seen:
                walk(w, seen | {w}, cost + weight, path + [w])

    walk(start, {start}, 0, [start])
    return best[0], best[1]


def bellman_ford(adj, start, vertices):
    """Handles negative edges, and detects a negative cycle. O(VE)."""
    dist = {v: float("inf") for v in vertices}
    dist[start] = 0
    for _ in range(len(vertices) - 1):
        for u in adj:
            for v, w in adj[u]:
                if dist[u] + w < dist[v]:
                    dist[v] = dist[u] + w
    for u in adj:                        # one more pass: any improvement means a negative cycle
        for v, w in adj[u]:
            if dist[u] + w < dist[v]:
                return None
    return dist


if __name__ == "__main__":
    G = build([("A", "B", 4), ("A", "C", 2), ("B", "C", 1), ("B", "D", 5),
               ("C", "D", 8), ("C", "E", 10), ("D", "E", 2), ("D", "F", 6),
               ("E", "F", 3)])

    print("Block 1 - shortest distances and the paths themselves")
    dist, parent, pops = dijkstra(G, "A")
    for v in sorted(dist):
        print(f"    A -> {v}: distance {dist[v]:2}   path {path_to(parent, v)}")
    assert dist["A"] == 0 and dist["C"] == 2 and dist["B"] == 3
    assert path_to(parent, "B") == ["A", "C", "B"]
    print("  note A->B is 3 via C, not the direct edge of weight 4 -")
    print("  a shortest path need not use the direct edge, or the fewest edges")

    print()
    print("Block 2 - checked against exhaustive search")
    for goal in sorted(dist):
        bpath, bcost = brute_force_shortest(G, "A", goal)
        print(f"    {goal}: dijkstra {dist[goal]:2}   brute force {bcost:2}   agree: {dist[goal] == bcost}")
        assert dist[goal] == bcost
    print("  every distance matches an exhaustive search over all simple paths")

    print()
    print("Block 3 - the assumption: NON-NEGATIVE weights")
    neg = build([("A", "B", 0), ("A", "C", 1), ("C", "B", -10)], directed=True)
    d_dij, _, _ = dijkstra(neg, "A")
    d_bf = bellman_ford(neg, "A", ["A", "B", "C"])
    print("  graph: A->B (0), A->C (1), C->B (-10)")
    print(f"    dijkstra says      A->B = {d_dij['B']}")
    print(f"    bellman-ford says  A->B = {d_bf['B']}")
    print(f"    truth: A->C->B costs 1 + (-10) = {1 + (-10)}")
    assert d_dij["B"] == 0 and d_bf["B"] == -9
    print("  Dijkstra is WRONG here, and not because of a coding error.")
    print("  It pops B first (distance 0) and FINALISES it. Only later does it reach")
    print("  C and find the -10 edge back to B - but B is already settled, and")
    print("  Dijkstra never revises a settled vertex. That refusal is the whole basis")
    print("  of its efficiency, and a negative edge is exactly what invalidates it:")
    print("  going further can now REDUCE the total, so 'closest first' stops working.")

    print()
    print("Block 4 - lazy deletion, and why the heap can exceed V entries")
    dist2, _, pops2 = dijkstra(G, "A")
    print(f"  graph has {len(G)} vertices; the heap was popped {pops2} times")
    print("  extra pops are STALE entries - a vertex whose distance improved after")
    print("  it was pushed. Skipping them with a 'done' set is simpler and faster")
    print("  than the decrease-key operation a textbook heap would need.")
    assert pops2 >= len(G)

    print()
    print("Block 5 - choosing the right tool")
    print("   situation                              use")
    rows = [("unweighted graph", "BFS - O(V+E), no heap needed"),
            ("non-negative weights", "Dijkstra - O((V+E) log V)"),
            ("any weights, need cycle detection", "Bellman-Ford - O(VE)"),
            ("one target, good heuristic available", "A* - Dijkstra with a priority bonus"),
            ("all pairs, dense graph", "Floyd-Warshall - O(V^3)")]
    for a, b in rows:
        print(f"   {a:38} {b}")
    unweighted = build([("A", "B", 1), ("B", "C", 1), ("A", "C", 1)])
    du, _, _ = dijkstra(unweighted, "A")
    print(f"  on an unweighted graph Dijkstra agrees with BFS: {dict(sorted(du.items()))}")
    assert du["C"] == 1
    print("  but BFS gets there without a heap, so use BFS when all weights are equal")

    print()
    print("dijkstra_lab: passed")
```

Expected output:

```
Block 1 - shortest distances and the paths themselves
    A -> A: distance  0   path ['A']
    A -> B: distance  3   path ['A', 'C', 'B']
    A -> C: distance  2   path ['A', 'C']
    A -> D: distance  8   path ['A', 'C', 'B', 'D']
    A -> E: distance 10   path ['A', 'C', 'B', 'D', 'E']
    A -> F: distance 13   path ['A', 'C', 'B', 'D', 'E', 'F']
  note A->B is 3 via C, not the direct edge of weight 4 -
  a shortest path need not use the direct edge, or the fewest edges

Block 2 - checked against exhaustive search
    A: dijkstra  0   brute force  0   agree: True
    B: dijkstra  3   brute force  3   agree: True
    C: dijkstra  2   brute force  2   agree: True
    D: dijkstra  8   brute force  8   agree: True
    E: dijkstra 10   brute force 10   agree: True
    F: dijkstra 13   brute force 13   agree: True
  every distance matches an exhaustive search over all simple paths

Block 3 - the assumption: NON-NEGATIVE weights
  graph: A->B (0), A->C (1), C->B (-10)
    dijkstra says      A->B = 0
    bellman-ford says  A->B = -9
    truth: A->C->B costs 1 + (-10) = -9
  Dijkstra is WRONG here, and not because of a coding error.
  It pops B first (distance 0) and FINALISES it. Only later does it reach
  C and find the -10 edge back to B - but B is already settled, and
  Dijkstra never revises a settled vertex. That refusal is the whole basis
  of its efficiency, and a negative edge is exactly what invalidates it:
  going further can now REDUCE the total, so 'closest first' stops working.

Block 4 - lazy deletion, and why the heap can exceed V entries
  graph has 6 vertices; the heap was popped 10 times
  extra pops are STALE entries - a vertex whose distance improved after
  it was pushed. Skipping them with a 'done' set is simpler and faster
  than the decrease-key operation a textbook heap would need.

Block 5 - choosing the right tool
   situation                              use
   unweighted graph                       BFS - O(V+E), no heap needed
   non-negative weights                   Dijkstra - O((V+E) log V)
   any weights, need cycle detection      Bellman-Ford - O(VE)
   one target, good heuristic available   A* - Dijkstra with a priority bonus
   all pairs, dense graph                 Floyd-Warshall - O(V^3)
  on an unweighted graph Dijkstra agrees with BFS: {'A': 0, 'B': 1, 'C': 1}
  but BFS gets there without a heap, so use BFS when all weights are equal

dijkstra_lab: passed
```

Block 3 is the lesson. Dijkstra returns $2$ where the true answer is $-4$, and no amount of debugging fixes it: the algorithm's correctness *rests* on the assumption that extending a path cannot make it cheaper.

## 6. Common Pitfalls & Traps

1. **Forgetting the Stale Entry Check**: Skipping `if current_dist > distances[current_node]: continue` will not cause incorrect answers, but it wastes massive CPU cycles re-exploring outdated graph paths.
2. **Negative Edge Weights**: Never use Dijkstra if edges can have negative values.
3. **Confusing Dijkstra with BFS**: BFS uses a simple Queue ($O(V+E)$ on unweighted graphs). Dijkstra uses a Min-Heap ($O((V+E)\log V)$ on weighted graphs).

---

## 7. Check Your Understanding (University Self-Assessment)

1. **Question**: What is the purpose of the edge relaxation step in Dijkstra's Algorithm?
   - <details><summary>Click for Answer</summary><b>Answer:</b> Edge relaxation checks if reaching a neighbor via the current node (<code>current_dist + weight</code>) is cheaper than the neighbor's previously recorded shortest distance. If so, the neighbor's recorded distance is updated.</details>

2. **Question**: Why does Dijkstra require a Min-Heap (Priority Queue) instead of a standard FIFO Queue?
   - <details><summary>Click for Answer</summary><b>Answer:</b> A FIFO queue explores nodes by hop count (BFS). A Min-Heap ensures that the node with the absolute smallest cumulative distance is always popped next, which is required for weighted graph shortest paths.</details>

3. **Question**: Can Dijkstra be used to find the shortest path on a graph with negative edge weights?
   - <details><summary>Click for Answer</summary><b>Answer:</b> <b>No!</b> Dijkstra assumes that adding edges can only increase cumulative path cost. Negative edges violate this greedy assumption. Use the <b>Bellman-Ford Algorithm</b> instead.</details>

---

## Practice — independent task

Implement **A\*** — Dijkstra guided by a heuristic — and measure what the guidance buys.

1. Take a grid with obstacles. Implement Dijkstra on it, then A\* using Manhattan distance as the heuristic $h$. The only change is the priority: $g + h$ instead of $g$.
2. Count **vertices expanded** by each. Report the ratio on several grids of increasing size.
3. **Test admissibility.** A heuristic is admissible if it never overestimates the true remaining cost. Verify Manhattan distance is admissible for 4-directional movement, then deliberately break it — multiply by 1.5 — and show A\* returning a **suboptimal path**. Report by how much.
4. Explain the trade in a comment: an inadmissible heuristic expands fewer nodes but loses the optimality guarantee. Say when that trade is worth making.
5. Then set $h = 0$ and confirm A\* becomes exactly Dijkstra — same expansions, same path. That is the cleanest way to see that A\* is a generalisation, not a different algorithm.

**Edge cases:** no path exists; start equals goal; a grid that is entirely obstacles except the endpoints; a heuristic that is admissible but not *consistent* (look up the difference and say which one A\* actually needs).

**Done when:** A\* and Dijkstra return the same path length on every solvable grid, your inadmissible version demonstrably returns a worse path, and $h=0$ reproduces Dijkstra exactly.

## Before moving on

You can implement Dijkstra with a heap, reconstruct paths, explain its greedy invariant, and demonstrate its failure on negative edges.

**Recap:** Dijkstra repeatedly finalises the closest unfinalised vertex; correct **only** for non-negative weights, because the greedy step assumes extending a path cannot reduce its cost; $O((V+E)\log V)$ with a binary heap; lazy deletion means the heap can hold more than $V$ entries and stale ones are skipped; use BFS when weights are equal, Bellman–Ford for negative weights or cycle detection, A* when you have a heuristic.

**Next:** [[11-topological-sort|Topological Sort]] — ordering a DAG, and the other thing DFS post-order is for.

## Related Modules
- [[03-bfs|Breadth-First Search (BFS)]] — Unweighted shortest paths ($O(V+E)$)
- [[08-heaps|Heaps & Priority Queues]] — Min-Heap mechanics powering Dijkstra
- [[06-graphs/index|Graphs]] — Weighted graph adjacency lists

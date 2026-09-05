# Module: Dijkstra's Algorithm (Weighted Shortest Path)

Welcome to the **Dijkstra's Algorithm** module. Dijkstra finds the shortest path from a starting source node to every other node in a **weighted graph with non-negative edge weights**.

While [[03-bfs|BFS]] finds shortest paths in terms of **number of hops** (unweighted edges), Dijkstra finds shortest paths in terms of **total cumulative cost/distance** (weighted edges).

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

## Related Modules
- [[03-bfs|Breadth-First Search (BFS)]] — Unweighted shortest paths ($O(V+E)$)
- [[08-heaps|Heaps & Priority Queues]] — Min-Heap mechanics powering Dijkstra
- [[06-graphs|Graphs]] — Weighted graph adjacency lists

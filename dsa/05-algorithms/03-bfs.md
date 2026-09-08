# Module: Breadth-First Search (BFS) (Level-by-Level & Shortest Path)

Welcome to the **Breadth-First Search (BFS)** module. BFS is a fundamental graph and tree traversal algorithm that explores nodes **level-by-level**, expanding outward in concentric rings from a starting vertex.

Where [[02-dfs|DFS]] dives deep down one branch before backtracking, BFS explores all immediate neighbors at distance $k$ before moving to any neighbor at distance $k+1$.

---

## 1. Real-World Motivation & Physical Metaphors

Imagine dropping a **pebble into a calm pond**:

```
 Level 0:              ( Start )
                          |
 Level 1:         ( Node A )  ( Node B )
                   /      \       |
 Level 2:   ( Node C ) ( Node D ) ( Node E )
```

1. Ripples expand outward in **concentric circles**.
2. First, the wave hits all points 1 meter away.
3. Then, it hits points 2 meters away, then 3 meters away.

### Why BFS Guarantees Shortest Path (Unweighted Graphs)
Because BFS explores every node at distance $k$ before touching distance $k+1$, **the very first time BFS reaches a target node, it is GUARANTEED to have arrived via the shortest possible path** (fewest edges)!

### Real-World Applications:
- **LinkedIn / Facebook Friend Degrees**: 1st-degree connections $\rightarrow$ 2nd-degree connections $\rightarrow$ 3rd-degree connections.
- **Shortest Path in Unweighted Mazes**: Minimum moves to solve a grid puzzle (e.g. Rotting Oranges, Word Ladder).
- **Web Crawlers**: Crawling pages at depth 1 before crawling linked pages at depth 2.

---

## 2. Plain-English Terminology & Concept Table

| Term | Plain-English Definition | Example / Analogy |
| :--- | :--- | :--- |
| **Breadth-First** | Expanding uniformly across all neighbors at the current level before going deeper. | Concentric water ripples expanding. |
| **Queue (FIFO)** | First-In, First-Out collection used to schedule nodes for exploration. | Supermarket line. |
| **Frontier** | The active set of nodes sitting in the queue waiting to be processed. | The expanding outer edge of the water wave. |
| **Unweighted Graph** | A graph where all edges have equal weight (cost = 1). | Simple grid mazes, friendship links. |

---

## 3. Technical Deep Dive: BFS Implementation

### Standard BFS Algorithm (Using `collections.deque`)

> [!IMPORTANT]
> **The Golden BFS Rule**: Always mark a node as `visited` **immediately when ENQUEUING it** into the queue, NOT when dequeuing it! Marking on enqueue prevents duplicate nodes from being added to the queue by multiple neighbors.

```python
from collections import deque

def bfs(graph: dict, start: str) -> list:
    """Traverses a graph level-by-level using a FIFO Queue."""
    visited = {start}          # Mark visited immediately at start
    queue = deque([start])     # FIFO Queue initialized with start node
    traversal_order = []
    
    while queue:
        node = queue.popleft() # Pop head node: FIFO behavior drives level-order!
        traversal_order.append(node)
        
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)   # Mark visited ON ENQUEUE!
                queue.append(neighbor)
                
    return traversal_order
```

---

## 4. Shortest Path Reconstruction in Unweighted Graphs

To reconstruct the exact shortest path from `start` to `target`, track each node's `parent` pointer during traversal:

```python
def shortest_path_bfs(graph: dict, start: str, target: str) -> list:
    """Finds the shortest path between start and target in an unweighted graph."""
    if start == target:
        return [start]
        
    visited = {start}
    queue = deque([start])
    parent = {start: None}  # Track predecessor node
    
    while queue:
        current = queue.popleft()
        
        if current == target:
            # Reconstruct path by walking backwards from target to start
            path = []
            while current is not None:
                path.append(current)
                current = parent[current]
            return path[::-1]  # Reverse to get start -> target
            
        for neighbor in graph[current]:
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = current
                queue.append(neighbor)
                
    return []  # No path exists
```

---

## 5. Time & Space Complexity Summary

| Metric | Complexity | Explanation |
| :--- | :--- | :--- |
| **Time Complexity** | **$O(V + E)$** | Every vertex ($V$) is enqueued once, and every edge ($E$) is examined once. |
| **Space Complexity (Auxiliary)** | **$O(V)$** | Space for `visited` set and `queue` (wide graphs store up to $O(V)$ nodes in queue). |

---

## 6. Common Pitfalls & Traps

1. **`list.pop(0)` Performance Trap**: Never write `queue.pop(0)` on a Python list! It takes $O(n)$ time to shift remaining elements, ruining BFS performance. Always use `collections.deque.popleft()` ($O(1)$).
2. **BFS on Weighted Graphs is WRONG**: BFS only finds shortest paths on **unweighted graphs** (or equal-cost edges). If edges have varying costs/distances, a path with 2 heavy edges can cost more than 3 light edges. Use **[[06-dijkstra|Dijkstra's Algorithm]]** for weighted graphs!
3. **Marking Visited on Dequeue**: If you mark `visited.add(node)` when *dequeuing* instead of *enqueuing*, multiple neighbors will enqueue duplicate copies of the same node, blowing up memory and runtime!

---

## 7. Check Your Understanding (University Self-Assessment)

1. **Question**: Why does BFS require a FIFO Queue while DFS uses a LIFO Stack?
   - <details><summary>Click for Answer</summary><b>Answer:</b> A <b>FIFO Queue</b> ensures that nodes are processed in the exact order they were discovered. All level <code>k</code> nodes are popped and processed before any level <code>k+1</code> nodes can be popped, driving level-by-level exploration.</details>

2. **Question**: You have a grid maze with edge costs equal to 1. Will BFS or DFS find the shortest route to the exit?
   - <details><summary>Click for Answer</summary><b>Answer:</b> <b>BFS</b> is guaranteed to find the shortest route. DFS explores deep paths first and might find a long, winding 50-step route before ever considering a direct 5-step route.</details>

3. **Question**: Why is marking nodes `visited` upon **enqueue** critical in BFS?
   - <details><summary>Click for Answer</summary><b>Answer:</b> If a node has multiple neighbors currently in the queue, delaying its <code>visited</code> mark until dequeue allows all neighbors to push duplicate entries of the same node into the queue, wasting memory and processing time.</details>

---

## Related Modules
- [[02-dfs|Depth-First Search (DFS)]] — Deep exploration traversal
- [[06-graphs|Graphs]] — Graph definitions and adjacency lists
- [[06-dijkstra|Dijkstra's Algorithm]] — Shortest path for weighted graphs
- [[07-stacks-and-queues|Stacks & Queues]] — Queue mechanics (`collections.deque`)

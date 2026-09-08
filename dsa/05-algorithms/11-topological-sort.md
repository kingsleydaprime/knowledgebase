# Module: Topological Sort (Dependency Ordering & Cycle Detection)

Welcome to the **Topological Sort** module. Topological sorting takes a **Directed Acyclic Graph (DAG)** and produces a flat, linear sequence of all vertices such that for every directed edge $u \to v$, node $u$ appears before node $v$ in the ordering.

It answers the universal question: *"Given a collection of tasks with prerequisites, in what valid sequence should I execute them so that every prerequisite is satisfied first?"*

---

## 1. Real-World Motivation & Physical Metaphors

Imagine **Getting Dressed in the Morning**:

```
 [ Underwear ] ---> [ Pants ] ---> [ Shoes ]
                       ^
                       |
                   [ Socks ]
```

- You cannot put on your **Shoes** before putting on your **Socks** and **Pants**.
- You cannot put on your **Pants** before putting on your **Underwear**.

Valid Topological Orderings:
1. `[Underwear, Socks, Pants, Shoes]`
2. `[Socks, Underwear, Pants, Shoes]`

Notice that a graph can have **multiple valid topological orderings**!

### Production Applications:
1. **Build Systems (Make, Bazel, Webpack)**: Compiling C++ files or JavaScript bundles in dependency order.
2. **Package Managers (npm, pip, cargo)**: Installing libraries after their required dependencies.
3. **University Course Registration**: Planning degree courses around prerequisite requirements (e.g. CS101 before CS201).
4. **Spreadsheet Engines (Excel)**: Recalculating cell formulas when a parent cell changes.

---

## 2. Plain-English Terminology & Concept Table

| Term | Plain-English Definition | Example / Analogy |
| :--- | :--- | :--- |
| **DAG** | Directed Acyclic Graph (directed edges with NO circular loops). | Prerequisites flowchart. |
| **In-Degree** | The number of incoming directed edges pointing into a node. | The number of uncompleted prerequisites a course has. |
| **Topological Order** | A linear list where every prerequisite node comes before its dependent nodes. | Valid daily task sequence. |
| **Cycle** | A circular path ($A \to B \to C \to A$) that makes topological ordering IMPOSSIBLE! | Circular reasoning deadlocks. |

---

## 3. Technical Deep Dive: Kahn's Algorithm (BFS In-Degree Method)

Kahn's Algorithm is the industry standard for Topological Sorting:

### Step-by-Step Mechanics
1. Calculate the **In-Degree** (number of incoming edges) for every vertex.
2. Push all vertices with `in_degree == 0` (nodes with zero prerequisites) into a **FIFO Queue**.
3. Pop a vertex `u` from the queue, append it to the `topological_order` list.
4. For every neighbor `v` of `u`, decrement its in-degree by 1 (`in_degree[v] -= 1`).
5. If `v`'s in-degree drops to 0, push `v` into the queue!
6. Repeat until the queue is empty.

> [!KEY-INSIGHT]
> **Cycle Detection Guarantee**: If `len(topological_order) < Total Nodes`, a **Cycle exists in the graph**! Circular dependencies prevent in-degrees from ever reaching 0.

---

### Python Code Implementation (Kahn's Algorithm)

```python
from collections import deque

def topological_sort(num_nodes: int, edges: list) -> list:
    """Performs topological sort using Kahn's Algorithm (BFS).
    
    edges format: list of tuples [(u, v)] meaning u MUST happen before v (u -> v).
    Returns a valid linear ordering list, or [] if a cycle exists!
    """
    # 1. Build adjacency list and calculate in-degrees
    graph = [[] for _ in range(num_nodes)]
    in_degree = [0] * num_nodes
    
    for u, v in edges:
        graph[u].append(v)
        in_degree[v] += 1
        
    # 2. Queue all nodes with 0 prerequisites (in_degree == 0)
    queue = deque([node for node in range(num_nodes) if in_degree[node] == 0])
    topological_order = []
    
    # 3. Process queue
    while queue:
        u = queue.popleft()
        topological_order.append(u)
        
        for v in graph[u]:
            in_degree[v] -= 1
            if in_degree[v] == 0:  # All prerequisites now satisfied!
                queue.append(v)
                
    # 4. Cycle check
    if len(topological_order) == num_nodes:
        return topological_order
    else:
        return []  # Return empty list: A cycle was detected!
```

---

## 4. Time & Space Complexity Summary

| Metric | Complexity | Explanation |
| :--- | :--- | :--- |
| **Time Complexity** | **$O(V + E)$** | Every vertex ($V$) is enqueued once, and every directed edge ($E$) is decremented once. |
| **Space Complexity** | **$O(V + E)$** | Graph adjacency list $O(V + E)$ plus in-degree array and queue $O(V)$. |

---

## 5. Common Pitfalls & Traps

1. **Graph Must Be Directed and Acyclic**: Calling Topological Sort on an **undirected graph** or a graph containing a **cycle** will fail. Always check `len(order) == num_nodes`.
2. **Flipping Edge Directions**: Reversing the direction of edges (`v -> u` instead of `u -> v`) will produce a reverse topological order. Be precise about dependency direction!
3. **Non-Unique Orders**: Never assert that a topological sort produces a single fixed output array. Multiple valid topological orderings often exist for the same graph.

---

## 6. Check Your Understanding (University Self-Assessment)

1. **Question**: What happens if you run Kahn's Topological Sort algorithm on a graph that contains a cycle?
   - <details><summary>Click for Answer</summary><b>Answer:</b> The nodes participating in the cycle will perpetually wait on each other and their in-degrees will never drop to 0. They will never be enqueued, causing the resulting <code>topological_order</code> list length to be <b>less than the total number of nodes</b> (detecting the cycle).</details>

2. **Question**: What is the definition of a node with an `in_degree` of 0?
   - <details><summary>Click for Answer</summary><b>Answer:</b> A node with an <code>in_degree</code> of 0 has zero incoming directed edges, meaning it has <b>no remaining uncompleted prerequisites</b> and can be executed immediately.</details>

3. **Question**: Can an undirected graph be topologically sorted?
   - <details><summary>Click for Answer</summary><b>Answer:</b> <b>No!</b> An undirected edge between A and B implies bidirectional dependency (A depends on B AND B depends on A), which forms a 2-node cycle.</details>

---

## Related Modules
- [[06-graphs|Graphs]] — Directed graphs and adjacency lists
- [[03-bfs|Breadth-First Search (BFS)]] — FIFO queue mechanics powering Kahn's algorithm
- [[02-dfs|Depth-First Search (DFS)]] — DFS post-order alternative for topological sort

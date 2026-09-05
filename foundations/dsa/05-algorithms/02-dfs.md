# Module: Depth-First Search (DFS) (Deep Exploration & Backtracking)

Welcome to the **Depth-First Search (DFS)** module. DFS is a fundamental graph and tree traversal algorithm that explores as far down a single branch as possible before **backtracking** to try alternative paths.

Where [[03-bfs|BFS]] spreads out evenly level-by-level like a pebble dropped in water, DFS charges headfirst down one path until it hits a dead end, then unwinds to explore unvisited branches.

---

## 1. Real-World Motivation & Physical Metaphors

Imagine a **Maze Explorer in a Dark Cave**:

```
[ Entrance A ] ---> [ Tunnel B ] ---> [ Dead End D ]
       |                  |
       |                  +---------> [ Exit E ]
       v
  [ Tunnel C ]
```

1. You walk down Tunnel B as deep as you can go until you hit Dead End D.
2. You **backtrack** to the last intersection (Tunnel B) and explore the other direction (Exit E).
3. Once all paths from Tunnel B are exhausted, you backtrack to Entrance A and explore Tunnel C.

In software, DFS powers **Puzzle Solvers (Sudoku, N-Queens)**, **Dependency Ordering (Build Systems)**, and **Cycle Detection in Graphs**.

---

## 2. Plain-English Terminology & Concept Table

| Term | Plain-English Definition | Example / Analogy |
| :--- | :--- | :--- |
| **Depth-First** | Committing to explore a branch to its maximum depth before backtracking. | Reading a book chapter-by-chapter rather than skimming page 1 of all books. |
| **Backtracking** | Unwinding execution back to the previous decision point when hitting a dead end. | Reversing steps at a maze dead-end. |
| **Call Stack (LIFO)** | The system stack that tracks active recursive function calls. | Function frames stacked in CPU memory. |
| **Visited Set** | A set tracking which vertices have already been explored to prevent infinite loops. | Marking explored cave walls with chalk. |

---

## 3. Technical Deep Dive: Recursive vs. Iterative DFS

DFS can be implemented using **Recursion** (implicit system call stack) or an **Explicit Stack** (LIFO queue).

### 1. Recursive DFS (The Natural Implementation)
```python
def dfs_recursive(graph: dict, node: str, visited: set = None) -> set:
    """Explores a graph recursively using the system call stack."""
    if visited is None:
        visited = set()
        
    visited.add(node)
    print("Visited Node:", node)
    
    for neighbor in graph[node]:
        if neighbor not in visited:
            dfs_recursive(graph, neighbor, visited)
            
    return visited
```

---

### 2. Iterative DFS (Using an Explicit LIFO Stack)
For extremely deep graphs (over 1,000 levels), recursion can trigger a `RecursionError` / Stack Overflow. The iterative version moves the call stack onto the heap using a list:

```python
def dfs_iterative(graph: dict, start: str) -> set:
    """Explores a graph iteratively using an explicit LIFO stack."""
    visited = set()
    stack = [start]  # LIFO Stack
    
    while stack:
        node = stack.pop()  # Pop top element: LIFO behavior drives depth-first search!
        if node in visited:
            continue
            
        visited.add(node)
        print("Visited Node:", node)
        
        for neighbor in graph[node]:
            if neighbor not in visited:
                stack.append(neighbor)
                
    return visited
```

---

## 4. Key Applications of DFS

1. **Detecting Cycles in Directed Graphs**: Tracking nodes currently in the active recursion call stack (`in_stack` set). Reaching a node already `in_stack` proves a **Cycle exists**.
2. **Topological Sort**: Running a postorder DFS on a Directed Acyclic Graph (DAG) orders tasks by dependencies.
3. **Connected Components**: Iterating through all vertices and calling DFS on unvisited nodes counts isolated graph clusters.

---

## 5. Time & Space Complexity Summary

| Metric | Complexity | Explanation |
| :--- | :--- | :--- |
| **Time Complexity** | **$O(V + E)$** | Every vertex ($V$) is visited once, and every edge ($E$) is examined once. |
| **Space Complexity (Auxiliary)** | **$O(V)$** | Space for `visited` set plus call stack depth $h \le V$ in worst-case linear graphs. |

---

## 6. Common Pitfalls & Traps

1. **Forgetting the `visited` Set**: On cyclic graphs, omitting a `visited` set causes infinite recursion loops.
2. **Recursion Limit Crash**: In Python, default maximum recursion depth is 1,000. For deep graphs, use `sys.setrecursionlimit()` or the **Iterative DFS** implementation.
3. **DFS Does NOT Find Shortest Paths**: DFS explores arbitrary deep paths first. It does **NOT** guarantee finding the shortest path on unweighted graphs! Use [[03-bfs|BFS]] for shortest paths.

---

## 7. Check Your Understanding (University Self-Assessment)

1. **Question**: Why does DFS fail to find the shortest path in an unweighted graph, while BFS succeeds?
   - <details><summary>Click for Answer</summary><b>Answer:</b> DFS charges down one deep branch completely before considering alternatives, meaning it might find a valid path that takes 10 hops before even considering a direct 1-hop path. BFS expands uniformly level-by-level, guaranteeing the first path found has the minimum number of edges.</details>

2. **Question**: What data structure powers iterative DFS under the hood?
   - <details><summary>Click for Answer</summary><b>Answer:</b> A <b>LIFO Stack</b> (Last-In, First-Out). Popping the most recently pushed neighbor forces the algorithm to explore deeper down the newest branch.</details>

3. **Question**: How do you modify DFS to count the number of connected components in an undirected graph?
   - <details><summary>Click for Answer</summary><b>Answer:</b> Loop through all vertices <code>v</code> in the graph. If <code>v</code> is not in <code>visited</code>, increment the component counter by 1 and call <code>dfs(v)</code> to mark all reachable nodes in that component.</details>

---

## Related Modules
- [[03-bfs|Breadth-First Search (BFS)]] — Level-by-level graph traversal
- [[06-graphs|Graphs]] — Graph representations and properties
- [[07-stacks-and-queues|Stacks & Queues]] — LIFO stack mechanics

# Module: Depth-First Search (DFS) (Deep Exploration & Backtracking)

Welcome to the **Depth-First Search (DFS)** module. DFS is a fundamental graph and tree traversal algorithm that explores as far down a single branch as possible before **backtracking** to try alternative paths.

Where [[03-bfs|BFS]] spreads out evenly level-by-level like a pebble dropped in water, DFS charges headfirst down one path until it hits a dead end, then unwinds to explore unvisited branches.

---

## Before you start

- You know what a graph is, and the difference between a path and a cycle — [[06-graphs/01-what-a-graph-is|what a graph is]], [[06-graphs/02-paths-cycles-and-connectivity|paths and connectivity]].
- You know how a stack behaves — [[07-stacks-and-queues|stacks and queues]].
- You can trace a recursive call — [[09-recursion-and-the-call-stack|recursion and the call stack]].

**After this lesson you will be able to:**

1. Implement DFS **recursively and iteratively**, and say what the explicit stack replaces.
2. Distinguish **pre-order** and **post-order** DFS, and name a problem that needs each.
3. Use DFS to count connected components and to detect a cycle, in both directed and undirected graphs.
4. Explain when the recursive form **fails in practice**, and demonstrate it.

**Study route:** read 1–5, attempt the prediction in section 4, then run the lab. Its last block breaks the recursive version on purpose.

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

## Implementation — complete runnable example

**Runnable example:** save as `dfs_lab.py` in any empty directory and run `python3 dfs_lab.py`. Standard library only; writes no files.

```python
"""DFS: recursive and iterative, pre/post-order, components, cycles, and depth."""
import sys
from collections import defaultdict


def build(edges, directed=False):
    adj = defaultdict(list)
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u) if not directed else adj.setdefault(v, [])
    return {k: sorted(vs) for k, vs in adj.items()}


def dfs_recursive(adj, start, seen=None, order=None):
    seen = set() if seen is None else seen
    order = [] if order is None else order
    seen.add(start)
    order.append(start)                      # PRE-order: record on arrival
    for w in adj.get(start, []):
        if w not in seen:
            dfs_recursive(adj, w, seen, order)
    return order


def dfs_postorder(adj, start, seen=None, order=None):
    seen = set() if seen is None else seen
    order = [] if order is None else order
    seen.add(start)
    for w in adj.get(start, []):
        if w not in seen:
            dfs_postorder(adj, w, seen, order)
    order.append(start)                      # POST-order: record on the way out
    return order


def dfs_iterative(adj, start):
    """The explicit stack replaces the call stack - same order, no recursion limit."""
    seen, order, stack = set(), [], [start]
    while stack:
        v = stack.pop()
        if v in seen:
            continue
        seen.add(v)
        order.append(v)
        for w in reversed(adj.get(v, [])):   # reversed, so the first neighbour pops first
            if w not in seen:
                stack.append(w)
    return order


def components(adj):
    seen, out = set(), []
    for v in sorted(adj):
        if v not in seen:
            comp = dfs_iterative(adj, v)
            seen.update(comp)
            out.append(sorted(comp))
    return out


def has_cycle_undirected(adj):
    seen = set()
    for start in sorted(adj):
        if start in seen:
            continue
        stack = [(start, None)]
        seen.add(start)
        while stack:
            v, parent = stack.pop()
            for w in adj[v]:
                if w == parent:              # the edge you arrived on is not a cycle
                    continue
                if w in seen:
                    return True
                seen.add(w)
                stack.append((w, v))
    return False


def has_cycle_directed(adj):
    """Three colours: 0 unvisited, 1 on the current path, 2 finished."""
    colour = defaultdict(int)

    def visit(v):
        colour[v] = 1
        for w in adj.get(v, []):
            if colour[w] == 1:               # a BACK edge: w is still on the path
                return True
            if colour[w] == 0 and visit(w):
                return True
        colour[v] = 2
        return False

    return any(colour[v] == 0 and visit(v) for v in sorted(adj))


if __name__ == "__main__":
    G = build([("A", "B"), ("A", "C"), ("B", "D"), ("C", "D"), ("D", "E")])
    print("Block 1 - recursive and iterative DFS give the same order")
    rec = dfs_recursive(G, "A")
    ite = dfs_iterative(G, "A")
    print(f"  recursive: {rec}")
    print(f"  iterative: {ite}")
    assert rec == ite
    print("  the explicit stack does exactly what the call stack was doing")
    print("  (note the 'reversed' when pushing: a stack reverses the order you push in)")

    print()
    print("Block 2 - pre-order vs post-order")
    print(f"  pre-order  (record on arrival):  {dfs_recursive(G, 'A')}")
    print(f"  post-order (record on exit):     {dfs_postorder(G, 'A')}")
    assert dfs_postorder(G, "A")[-1] == "A"
    print("  post-order finishes at the START vertex, because it is recorded last.")
    print("  That is why topological sort uses post-order: a vertex is only")
    print("  finished once everything it depends on is finished.")

    print()
    print("Block 3 - counting connected components")
    split = build([("A", "B"), ("B", "C"), ("D", "E"), ("F", "G"), ("G", "H")])
    comps = components(split)
    for i, c in enumerate(comps, 1):
        print(f"    component {i}: {c}")
    print(f"  {len(comps)} components - one DFS per unvisited vertex, O(V+E) total")
    assert len(comps) == 3

    print()
    print("Block 4 - cycle detection, and why directed needs three colours")
    cases_u = {"triangle": [("A", "B"), ("B", "C"), ("C", "A")],
               "path":     [("A", "B"), ("B", "C")],
               "tree":     [("A", "B"), ("A", "C"), ("B", "D")]}
    for name, es in cases_u.items():
        print(f"  undirected {name:9}: cycle = {has_cycle_undirected(build(es))}")
    assert has_cycle_undirected(build(cases_u["triangle"]))
    assert not has_cycle_undirected(build(cases_u["tree"]))

    cases_d = {"A->B->C->A (cycle)": [("A", "B"), ("B", "C"), ("C", "A")],
               "A->B, A->C, B->C ":  [("A", "B"), ("A", "C"), ("B", "C")]}
    for name, es in cases_d.items():
        print(f"  directed {name}: cycle = {has_cycle_directed(build(es, directed=True))}")
    assert has_cycle_directed(build(cases_d["A->B->C->A (cycle)"], directed=True))
    assert not has_cycle_directed(build(cases_d["A->B, A->C, B->C "], directed=True))
    print("  the second digraph has an UNDIRECTED cycle but no directed one -")
    print("  which is why 'already visited' is not enough for digraphs. You need")
    print("  'visited AND still on the current path', which is what colour 1 means.")

    print()
    print("Block 5 - where the recursive version breaks")
    print(f"  Python's recursion limit is {sys.getrecursionlimit():,}")
    long_path = build([(i, i + 1) for i in range(5000)])
    try:
        dfs_recursive(long_path, 0)
        print("  recursive DFS on a 5,000-vertex path: succeeded")
    except RecursionError:
        print("  recursive DFS on a 5,000-vertex path: RecursionError")
    order = dfs_iterative(long_path, 0)
    print(f"  iterative DFS on the same graph: visited {len(order):,} vertices, no problem")
    assert len(order) == 5001
    print("  a long path is not an exotic input - it is a linked list, a chain of")
    print("  dependencies, or a grid traversed in one direction. Prefer the iterative")
    print("  form for anything whose depth you do not control.")

    print()
    print("dfs_lab: passed")
```

Expected output:

```
Block 1 - recursive and iterative DFS give the same order
  recursive: ['A', 'B', 'D', 'C', 'E']
  iterative: ['A', 'B', 'D', 'C', 'E']
  the explicit stack does exactly what the call stack was doing
  (note the 'reversed' when pushing: a stack reverses the order you push in)

Block 2 - pre-order vs post-order
  pre-order  (record on arrival):  ['A', 'B', 'D', 'C', 'E']
  post-order (record on exit):     ['C', 'E', 'D', 'B', 'A']
  post-order finishes at the START vertex, because it is recorded last.
  That is why topological sort uses post-order: a vertex is only
  finished once everything it depends on is finished.

Block 3 - counting connected components
    component 1: ['A', 'B', 'C']
    component 2: ['D', 'E']
    component 3: ['F', 'G', 'H']
  3 components - one DFS per unvisited vertex, O(V+E) total

Block 4 - cycle detection, and why directed needs three colours
  undirected triangle : cycle = True
  undirected path     : cycle = False
  undirected tree     : cycle = False
  directed A->B->C->A (cycle): cycle = True
  directed A->B, A->C, B->C : cycle = False
  the second digraph has an UNDIRECTED cycle but no directed one -
  which is why 'already visited' is not enough for digraphs. You need
  'visited AND still on the current path', which is what colour 1 means.

Block 5 - where the recursive version breaks
  Python's recursion limit is 1,000
  recursive DFS on a 5,000-vertex path: RecursionError
  iterative DFS on the same graph: visited 5,001 vertices, no problem
  a long path is not an exotic input - it is a linked list, a chain of
  dependencies, or a grid traversed in one direction. Prefer the iterative
  form for anything whose depth you do not control.

dfs_lab: passed
```

Block 5 is the practical warning: the recursive form is clearer and fails on input you will actually meet.

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

## Practice — independent task

Implement `find_path(graph, start, goal)` returning an actual path, not just whether one exists — then extend it.

1. Return the list of vertices from `start` to `goal`, or `None`. Track a **parent map** during the search and walk it backwards at the end.
2. Do it both recursively and iteratively, and assert the two agree on the *set* of reachable vertices (the paths themselves may differ, and that is worth noticing).
3. **Find all paths**, not just one. Explain in a comment why this needs the visited set to be un-marked on the way back out — and why that makes it exponential.
4. Add a `max_depth` parameter that stops the search early. Use it to implement **iterative deepening**: run depth-limited DFS with the limit increasing from 1. Show that it finds the shortest path like BFS while using DFS's $O(d)$ memory.
5. Measure the cost of that trade: count vertices visited by iterative deepening versus plain BFS on the same graph, and report the ratio. It re-explores, and you should be able to say roughly by what factor.

**Edge cases:** `start == goal`; the goal unreachable; a graph with a cycle (your all-paths version must still terminate); a self-loop.

**Done when:** your path is verifiable — every consecutive pair is an edge — iterative deepening returns the same length as BFS, and you can state the re-exploration factor with a number you measured.

## Before moving on

You can implement DFS both ways, use pre- and post-order deliberately, detect cycles in both graph kinds, and say when recursion will fail.

**Recap:** DFS goes deep before wide, using a stack (explicit or the call stack); $O(V+E)$ time, $O(V)$ space; pre-order records on arrival, post-order on exit — and post-order is what topological sort needs; undirected cycle detection ignores the edge you arrived on, directed needs three colours to distinguish "finished" from "on the current path"; the recursive form dies on deep graphs.

**Next:** [[03-bfs|Breadth-First Search]] — the same traversal cost, a different order, and the one that gives shortest paths.

## Related Modules
- [[03-bfs|Breadth-First Search (BFS)]] — Level-by-level graph traversal
- [[06-graphs/index|Graphs]] — Graph representations and properties
- [[07-stacks-and-queues|Stacks & Queues]] — LIFO stack mechanics

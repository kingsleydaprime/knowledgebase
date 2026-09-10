# Module: Topological Sort (Dependency Ordering & Cycle Detection)

Welcome to the **Topological Sort** module. Topological sorting takes a **Directed Acyclic Graph (DAG)** and produces a flat, linear sequence of all vertices such that for every directed edge $u \to v$, node $u$ appears before node $v$ in the ordering.

It answers the universal question: *"Given a collection of tasks with prerequisites, in what valid sequence should I execute them so that every prerequisite is satisfied first?"*

---

## Before you start

- You know what a DAG is and how to detect one — [[06-graphs/02-paths-cycles-and-connectivity|paths and connectivity]].
- You know DFS post-order — [[02-dfs|depth-first search]].
- You know how a queue behaves — [[07-stacks-and-queues|stacks and queues]].

**After this lesson you will be able to:**

1. Implement topological sort **both ways** — Kahn's in-degree algorithm and the DFS post-order method.
2. Detect a cycle as a by-product, and report which vertices are involved.
3. Explain why the order is **not unique**, and enumerate all valid orders for a small DAG.
4. Recognise the problem shape in build systems, schedulers and dependency resolvers.

**Study route:** read 1–5, attempt the prediction in section 4, then run the lab.

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

## Implementation — complete runnable example

**Runnable example:** save as `toposort.py` in any empty directory and run `python3 toposort.py`. Standard library only; writes no files.

```python
"""Topological sort: Kahn's algorithm, the DFS method, and cycle reporting."""
from collections import defaultdict, deque
from itertools import permutations


def build(edges, vertices=None):
    adj = defaultdict(list)
    for v in (vertices or []):
        adj.setdefault(v, [])
    for u, v in edges:
        adj[u].append(v)
        adj.setdefault(v, [])
    return {k: sorted(vs) for k, vs in adj.items()}


def kahn(adj):
    """Repeatedly take a vertex with no remaining prerequisites."""
    indeg = {v: 0 for v in adj}
    for u in adj:
        for v in adj[u]:
            indeg[v] += 1
    q = deque(sorted(v for v in adj if indeg[v] == 0))
    order = []
    while q:
        v = q.popleft()
        order.append(v)
        for w in adj[v]:
            indeg[w] -= 1
            if indeg[w] == 0:
                q.append(w)
    if len(order) != len(adj):
        return None, [v for v in adj if indeg[v] > 0]   # the cycle's vertices
    return order, []


def dfs_topo(adj):
    """Post-order, reversed. A vertex is finished only after all its successors."""
    colour = {v: 0 for v in adj}
    order, cycle = [], []

    def visit(v, path):
        colour[v] = 1
        for w in adj[v]:
            if colour[w] == 1:
                cycle.extend(path[path.index(w):] + [w])
                return False
            if colour[w] == 0 and not visit(w, path + [w]):
                return False
        colour[v] = 2
        order.append(v)                  # recorded on the way OUT
        return True

    for v in sorted(adj):
        if colour[v] == 0 and not visit(v, [v]):
            return None, cycle
    return order[::-1], []


def is_valid_order(adj, order):
    pos = {v: i for i, v in enumerate(order)}
    return len(order) == len(adj) and all(pos[u] < pos[v] for u in adj for v in adj[u])


def all_valid_orders(adj):
    return [p for p in permutations(sorted(adj)) if is_valid_order(adj, list(p))]


if __name__ == "__main__":
    courses = build([("intro", "data-structures"), ("intro", "discrete-math"),
                     ("data-structures", "algorithms"), ("discrete-math", "algorithms"),
                     ("algorithms", "compilers")])

    print("Block 1 - both algorithms produce a valid order")
    k_order, _ = kahn(courses)
    d_order, _ = dfs_topo(courses)
    print(f"  Kahn:  {k_order}")
    print(f"  DFS:   {d_order}")
    assert is_valid_order(courses, k_order)
    assert is_valid_order(courses, d_order)
    print("  both valid; they differ because the order is not unique")

    print()
    print("Block 2 - the order is NOT unique")
    small = build([("a", "c"), ("b", "c"), ("c", "d")])
    orders = all_valid_orders(small)
    print(f"  graph: a->c, b->c, c->d")
    print(f"  all valid orders: {[''.join(o) for o in orders]}")
    assert len(orders) == 2
    print("  a and b are independent, so either may come first. Any algorithm")
    print("  returns ONE of these; asserting a specific one is a broken test.")

    print()
    print("Block 3 - a cycle makes it impossible, and both methods say so")
    cyclic = build([("a", "b"), ("b", "c"), ("c", "a"), ("c", "d")])
    k_res, k_cycle = kahn(cyclic)
    d_res, d_cycle = dfs_topo(cyclic)
    print(f"  Kahn returns {k_res}, vertices stuck in a cycle: {sorted(k_cycle)}")
    print(f"  DFS returns  {d_res}, cycle found: {d_cycle}")
    assert k_res is None and d_res is None
    assert set(k_cycle) >= {"a", "b", "c"}
    print("  Kahn detects it by finishing with fewer vertices than it started with:")
    print("  anything still holding a positive in-degree is waiting on a cycle.")
    print("  DFS detects it by meeting a vertex still on the current path.")

    print()
    print("Block 4 - Kahn's invariant, step by step")
    indeg = {v: 0 for v in courses}
    for u in courses:
        for v in courses[u]:
            indeg[v] += 1
    print(f"  initial in-degrees: {dict(sorted(indeg.items()))}")
    q = deque(sorted(v for v in courses if indeg[v] == 0))
    step = 0
    while q:
        step += 1
        v = q.popleft()
        ready = []
        for w in courses[v]:
            indeg[w] -= 1
            if indeg[w] == 0:
                q.append(w)
                ready.append(w)
        print(f"    step {step}: take {v:16} -> unlocked {ready if ready else '-'}")
    print("  the invariant: the queue holds exactly the vertices whose prerequisites")
    print("  are all already placed. That is what makes the output valid by construction.")

    print()
    print("Block 5 - the shape in the wild")
    build_graph = build([("config.h", "main.o"), ("config.h", "util.o"),
                         ("util.h", "util.o"), ("main.o", "app"), ("util.o", "app")])
    order, _ = kahn(build_graph)
    print(f"  a tiny build dependency graph: {order}")
    assert order.index("main.o") < order.index("app")
    assert order.index("config.h") < order.index("main.o")
    print("  every .o comes after its headers, and the binary comes last.")
    print("  This is make, cargo, npm, a CI pipeline, a spreadsheet recalculation,")
    print("  and course prerequisites - the same algorithm each time.")

    print()
    print("toposort: passed")
```

Expected output:

```
Block 1 - both algorithms produce a valid order
  Kahn:  ['intro', 'data-structures', 'discrete-math', 'algorithms', 'compilers']
  DFS:   ['intro', 'discrete-math', 'data-structures', 'algorithms', 'compilers']
  both valid; they differ because the order is not unique

Block 2 - the order is NOT unique
  graph: a->c, b->c, c->d
  all valid orders: ['abcd', 'bacd']
  a and b are independent, so either may come first. Any algorithm
  returns ONE of these; asserting a specific one is a broken test.

Block 3 - a cycle makes it impossible, and both methods say so
  Kahn returns None, vertices stuck in a cycle: ['a', 'b', 'c', 'd']
  DFS returns  None, cycle found: ['a', 'b', 'c', 'a']
  Kahn detects it by finishing with fewer vertices than it started with:
  anything still holding a positive in-degree is waiting on a cycle.
  DFS detects it by meeting a vertex still on the current path.

Block 4 - Kahn's invariant, step by step
  initial in-degrees: {'algorithms': 2, 'compilers': 1, 'data-structures': 1, 'discrete-math': 1, 'intro': 0}
    step 1: take intro            -> unlocked ['data-structures', 'discrete-math']
    step 2: take data-structures  -> unlocked -
    step 3: take discrete-math    -> unlocked ['algorithms']
    step 4: take algorithms       -> unlocked ['compilers']
    step 5: take compilers        -> unlocked -
  the invariant: the queue holds exactly the vertices whose prerequisites
  are all already placed. That is what makes the output valid by construction.

Block 5 - the shape in the wild
  a tiny build dependency graph: ['config.h', 'util.h', 'main.o', 'util.o', 'app']
  every .o comes after its headers, and the binary comes last.
  This is make, cargo, npm, a CI pipeline, a spreadsheet recalculation,
  and course prerequisites - the same algorithm each time.

toposort: passed
```

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

## Practice — independent task

Implement `resolve(packages)` — a dependency resolver that reports **useful** errors.

1. Input is a dict mapping each package to its dependencies. Return a valid install order, or a structured error.
2. **On a cycle, report the actual cycle** — the list of packages forming it, in order — not just "a cycle exists". This is what makes an error message useful, and it is the part most implementations skip.
3. On a missing dependency, report which package required it.
4. Add **deterministic tie-breaking**: when several packages are ready, take them alphabetically. Assert the output is identical across runs — an unstable order makes builds unreproducible, which is a real problem, not a cosmetic one.
5. Then implement **parallel scheduling**: instead of a flat list, return *waves* — sets of packages installable simultaneously. Wave $k$ is everything whose dependencies are all in earlier waves. Report the number of waves and the maximum wave width, and explain what those two numbers mean for a build farm.

**Edge cases:** a package depending on itself; two packages depending on each other; an empty input; a package with no dependencies and no dependents.

**Done when:** your cycle report names the actual cycle members in order, repeated runs give byte-identical output, and your wave count matches the longest dependency chain — which it must, and you should be able to say why.

## Before moving on

You can implement both algorithms, detect and report cycles, and explain why the order is not unique.

**Recap:** a topological order exists **iff** the graph is a DAG; Kahn's repeatedly removes a zero in-degree vertex and detects a cycle by finishing short; the DFS method takes post-order and reverses it, detecting a cycle via a vertex still on the current path; both are $O(V+E)$; the order is generally **not unique**, so never assert one specific answer; the number of parallel waves equals the longest dependency chain.

**Next:** [[12-minimum-spanning-tree|Minimum Spanning Tree]] — connecting everything at least total cost.

## Related Modules
- [[06-graphs/index|Graphs]] — Directed graphs and adjacency lists
- [[03-bfs|Breadth-First Search (BFS)]] — FIFO queue mechanics powering Kahn's algorithm
- [[02-dfs|Depth-First Search (DFS)]] — DFS post-order alternative for topological sort

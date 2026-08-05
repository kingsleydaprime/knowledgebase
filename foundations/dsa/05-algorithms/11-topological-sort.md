# Topological Sort

A topological sort is a linear ordering of the nodes of a **directed acyclic graph** (DAG) such that for every edge `u → v`, `u` comes before `v`. It answers "given a pile of tasks with dependencies, in what order can I do them so every prerequisite is finished before the thing that needs it?" — course schedules, build systems, package installs, spreadsheet recalculation, anything with a "must happen before" relation.

## Why it needs a DAG

Two conditions are non-negotiable:

- **Directed** — the edges *are* the "before/after" relation; an undirected edge has no direction to respect.
- **Acyclic** — if `a → b → c → a`, then a must precede b must precede c must precede a, which is impossible. **A cycle means no valid ordering exists.** So every topological-sort algorithm doubles as a **cycle detector**: if it can't place all the nodes, the graph has a cycle.

A DAG generally has *many* valid topological orders (any ordering consistent with the dependencies), not a unique one.

## Two algorithms

### Kahn's algorithm (BFS on in-degrees)

Intuition: a node with **no remaining prerequisites** (in-degree 0) can go next. Emit it, "remove" it (which decrements its neighbors' in-degrees), and repeat.

```python
from collections import deque

def topo_sort(num_nodes, edges):           # edges: list of (u -> v)
    graph = [[] for _ in range(num_nodes)]
    indegree = [0] * num_nodes
    for u, v in edges:
        graph[u].append(v)
        indegree[v] += 1

    queue = deque(n for n in range(num_nodes) if indegree[n] == 0)
    order = []
    while queue:
        node = queue.popleft()
        order.append(node)
        for nxt in graph[node]:
            indegree[nxt] -= 1
            if indegree[nxt] == 0:         # all prerequisites now satisfied
                queue.append(nxt)

    return order if len(order) == num_nodes else []   # [] => a cycle exists
```

The cycle check is elegant: if a cycle exists, its nodes never reach in-degree 0 (they perpetually wait on each other), so they're never emitted, and `len(order) < num_nodes`.

### DFS + post-order (reverse finishing times)

Run [[02-dfs|DFS]]; a node is appended to the output **after** all its descendants are fully explored (post-order). Reverse that list. Intuition: a node finishes *after* everything it depends on, so reverse-finishing-order puts dependencies first. Cycle detection needs a three-color state (unvisited / in-progress / done) — hitting an **in-progress** node means a back edge, i.e. a cycle.

```python
def topo_sort_dfs(num_nodes, graph):
    WHITE, GRAY, BLACK = 0, 1, 2
    color = [WHITE] * num_nodes
    order = []
    def dfs(u):
        color[u] = GRAY                    # in-progress
        for v in graph[u]:
            if color[v] == GRAY: return False   # back edge -> cycle
            if color[v] == WHITE and not dfs(v): return False
        color[u] = BLACK
        order.append(u)                    # post-order
        return True
    for u in range(num_nodes):
        if color[u] == WHITE and not dfs(u):
            return []                      # cycle
    return order[::-1]                     # reverse post-order
```

### Which to use

Both are O(V + E) time, O(V) space. **Kahn's is usually the interview default** — it's iterative (no recursion depth worry), and the in-degree-0 idea is easy to explain and extends naturally to "is there a *unique* order?" (yes iff the queue never holds more than one node) and lexicographically-smallest order (use a heap instead of a plain queue). Reach for the DFS form when you're already doing a DFS for other reasons.

## Complexity

| | Time | Space |
|---|---|---|
| Kahn's (BFS) | O(V + E) | O(V) |
| DFS post-order | O(V + E) | O(V) recursion + color |

You visit each node once and each edge once — the same linear bound as any graph traversal.

## Canonical problems (NeetCode Graphs / Advanced Graphs)

- **Course Schedule** — "can you finish all courses?" is exactly "does this prerequisite graph have a valid topological order?" → run Kahn's, return whether all nodes were emitted (i.e. no cycle).
- **Course Schedule II** — same, but *return the order* (the `order` list itself).
- **Alien Dictionary** — derive `u → v` edges by comparing adjacent words to find character precedence, then topologically sort the alphabet. The hard part is *building* the graph correctly (including the "prefix comes first" invalid case); the sort is then routine.

## Gotchas

- **Not a DAG → no ordering.** Always handle the cycle case; half these problems are secretly "detect a cycle."
- **The order isn't unique** — any valid ordering is correct unless the problem asks for the lexicographically smallest (then use a min-heap in Kahn's).
- **Build the in-degree/adjacency from the right edge direction** — flipping `u → v` silently produces a reversed, wrong order.
- In the DFS form, **"visited" isn't enough** — you need the three-color (in-progress vs done) distinction to catch cycles; a plain `visited` set can't tell a back edge from a cross edge.

## Related
- [[06-graphs|Graphs]] — DAGs, in-degree, adjacency representation
- [[02-dfs|DFS]] / [[03-bfs|BFS]] — the two traversal engines underneath
- [[10-greedy-algorithms|Greedy]] — Kahn's "take any ready node" is a greedy choice that's provably safe on a DAG
- [[../06-patterns/12-bfs-pattern|BFS pattern]] — Kahn's is BFS over a dependency graph

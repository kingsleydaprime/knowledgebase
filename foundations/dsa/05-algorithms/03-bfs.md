# Breadth-First Search (BFS)

BFS explores a graph level by level — it fully processes everything at the current distance from the start before moving one step further out. Where [[02-dfs|DFS]] commits to one path and backtracks, BFS spreads out evenly in every direction at once. That property is what makes it the right tool the moment "shortest path" enters the problem.

## How it works

The mechanism is a **queue** (FIFO) instead of a stack — that single data-structure swap is the entire difference between BFS and iterative DFS.

```python
from collections import deque

def bfs(graph, start):
    visited = {start}
    queue = deque([start])
    order = []
    while queue:
        node = queue.popleft()       # FIFO — this is what makes it breadth-first
        order.append(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    return order
```

Note that here, nodes are marked `visited` at the moment they're **added to the queue**, not when they're popped — this is the opposite of the DFS convention and it matters: without it, the same node could be queued multiple times by different neighbors before it's ever processed.

```
Graph:            BFS from A:
  A - B - D        level 0: A
  |   |             level 1: B, C
  C   E             level 2: D, E, F
  |
  F
```

## Why it finds shortest paths (unweighted graphs)

Because BFS finishes an entire "ring" of nodes at distance `k` from the start before touching any node at distance `k+1`, the *first* time it reaches any given node is guaranteed to be via a shortest path — there's no way a node at distance `k+1` gets discovered before all distance-`k` nodes have been. Track a `distance` (or `parent`) map alongside the traversal and you get shortest-path distances (and the actual path, via parent pointers) for free.

```python
def shortest_path(graph, start, end):
    visited = {start}
    queue = deque([(start, [start])])
    while queue:
        node, path = queue.popleft()
        if node == end:
            return path
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    return None   # no path exists
```

This guarantee **only holds for unweighted graphs** (or graphs where every edge has equal weight) — if edges have different costs, "fewest edges" and "lowest total cost" stop being the same thing, and you need Dijkstra's algorithm instead.

## Complexity

O(V + E), same reasoning as DFS — every vertex is enqueued once, every edge is examined once. Space is O(V) for the queue and visited set in the worst case (a "wide" graph can have most of its vertices sitting in the queue at once, unlike DFS where the stack depth is bounded by path length).

## What BFS is actually good for

- **Shortest path in an unweighted graph** — the main reason to reach for it.
- **Level-order traversal of a tree** — see [[02-traversal|traversal]]; a tree is just a graph, so this is the same algorithm.
- Anything phrased as "minimum number of steps/moves to reach X" — a very common LeetCode framing (word ladder, minimum knight moves, rotting oranges) that's secretly "run BFS from the start state."

## Gotchas

- **Using `list.pop(0)` instead of `collections.deque` in Python** — `list.pop(0)` is O(n) because every remaining element has to shift down one index, which silently turns your "O(V+E) BFS" into something much worse. Always use `deque` (O(1) popleft) for the queue.
- Marking visited on **enqueue**, not on dequeue, is required to avoid duplicate work — this is the opposite convention from the typical DFS write-up, and mixing them up is an easy mistake when switching between the two.
- BFS uses more memory than DFS on wide graphs (many nodes at the same level) since the whole frontier sits in the queue at once — DFS's memory footprint is bounded by depth instead.

## Related
- [[02-dfs|dfs]]
- [[06-graphs|graphs]]
- [[02-traversal|traversal]]

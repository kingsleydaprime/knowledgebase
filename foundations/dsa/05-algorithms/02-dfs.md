# Depth-First Search (DFS)

DFS explores as far down one branch as possible before backtracking. Given a choice of which neighbor/child to visit next, it always picks one and commits fully to that path before ever trying the alternatives. On a tree this is exactly [[02-traversal|preorder/inorder/postorder]] traversal; on a [[06-graphs|graph]] it's the same idea with one addition — a `visited` set, because a graph can have cycles a tree can't.

## How it works

**Recursive** (uses the call stack implicitly):

```python
def dfs(graph, node, visited=None):
    if visited is None:
        visited = set()
    visited.add(node)
    print(node)                      # process node
    for neighbor in graph[node]:
        if neighbor not in visited:
            dfs(graph, neighbor, visited)
    return visited
```

**Iterative** (uses an explicit stack — useful when recursion depth is a concern):

```python
def dfs_iterative(graph, start):
    visited = set()
    stack = [start]
    while stack:
        node = stack.pop()           # LIFO — this is what makes it depth-first
        if node in visited:
            continue
        visited.add(node)
        print(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                stack.append(neighbor)
    return visited
```

The recursive and iterative versions aren't just stylistic alternatives — the recursive version literally uses the call stack as its stack; the iterative version makes that stack explicit. That's *why* an iterative rewrite is possible at all, and it's a useful thing to notice for any recursive algorithm.

```
Graph:            DFS from A (visiting alphabetically when tied):
  A - B - D        A -> B -> D
  |   |
  C   E            (backtrack to B) -> E
  |                (backtrack to A) -> C
  F
```

## Complexity

O(V + E) — every vertex is visited once (V), and every edge is examined once when scanning a node's neighbor list (E). Space is O(V) for the `visited` set, plus O(V) worst case for the recursion/stack depth on a highly unbalanced graph.

## What DFS is actually good for

- **Cycle detection** — if you reach a node that's already in the current recursion path (not just visited overall), there's a cycle.
- **Topological sort** — run DFS, append each node to the front of the result as it *finishes* (postorder-style), which works because a node's dependencies must finish before it does.
- **Connected components / path existence** — "is there a path from A to B" or "how many separate clusters exist" both fall out of running DFS and seeing what it reaches.
- **Maze / puzzle solving** — DFS naturally explores one full path before giving up on it and trying another, which is exactly backtracking.

## Gotchas

- **Forgetting the `visited` set** is the single most common DFS bug — on a graph with a cycle, it turns into an infinite loop instead of an error, which makes it harder to notice than a crash.
- Marking a node visited *when you pop/enter it* vs *when you push it* matters for correctness in the iterative version — pushing without marking-on-push can let the same node get added to the stack multiple times before it's ever processed (harmless for correctness here since the `visited` check on pop catches it, but wasteful).
- Recursive DFS on a deep or adversarial graph can hit the language's recursion limit (Python's default is 1000) — the iterative version has no such ceiling beyond available memory.
- DFS does **not** guarantee the shortest path in an unweighted graph — it just finds *a* path. If you need shortest path on unweighted edges, that's [[03-bfs|bfs]], not DFS.

## Related
- [[03-bfs|bfs]]
- [[06-graphs|graphs]]
- [[02-traversal|traversal]]

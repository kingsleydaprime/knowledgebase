# Module: Breadth-First Search (BFS) (Level-by-Level & Shortest Path)

Welcome to the **Breadth-First Search (BFS)** module. BFS is a fundamental graph and tree traversal algorithm that explores nodes **level-by-level**, expanding outward in concentric rings from a starting vertex.

Where [[02-dfs|DFS]] dives deep down one branch before backtracking, BFS explores all immediate neighbors at distance $k$ before moving to any neighbor at distance $k+1$.

---

## Before you start

- You know DFS and what it does *not* guarantee — [[02-dfs|depth-first search]].
- You know how a queue behaves — [[07-stacks-and-queues|stacks and queues]].
- You know graph connectivity vocabulary — [[06-graphs/02-paths-cycles-and-connectivity|paths and connectivity]].

**After this lesson you will be able to:**

1. Implement BFS, and **prove to yourself** that it returns shortest paths on unweighted graphs by comparing against DFS.
2. Reconstruct the path itself, not just its length.
3. Implement **multi-source** BFS, and say which problems need it.
4. Say precisely why BFS stops giving shortest paths the moment edges have weights.

**Study route:** read 1–5, attempt the prediction in section 4, then run the lab. Block 2 is the shortest-path guarantee, measured.

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

## Implementation — complete runnable example

**Runnable example:** save as `bfs_lab.py` in any empty directory and run `python3 bfs_lab.py`. Standard library only; writes no files.

```python
"""BFS: levels, shortest paths, multi-source, and where the guarantee ends."""
from collections import defaultdict, deque


def build(edges, directed=False):
    adj = defaultdict(list)
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u) if not directed else adj.setdefault(v, [])
    return {k: sorted(vs) for k, vs in adj.items()}


def bfs_levels(adj, start):
    """Return {vertex: distance in edges}, and the vertices grouped by level."""
    dist = {start: 0}
    levels = [[start]]
    q = deque([start])
    while q:
        v = q.popleft()
        for w in adj.get(v, []):
            if w not in dist:
                dist[w] = dist[v] + 1
                while len(levels) <= dist[w]:
                    levels.append([])
                levels[dist[w]].append(w)
                q.append(w)
    return dist, levels


def bfs_path(adj, start, goal):
    """The path itself, via a parent map."""
    if start == goal:
        return [start]
    parent = {start: None}
    q = deque([start])
    while q:
        v = q.popleft()
        for w in adj.get(v, []):
            if w not in parent:
                parent[w] = v
                if w == goal:
                    path = [goal]
                    while parent[path[-1]] is not None:
                        path.append(parent[path[-1]])
                    return path[::-1]
                q.append(w)
    return None


def dfs_path(adj, start, goal, seen=None):
    """DFS finds A path, with no claim about its length."""
    seen = seen or {start}
    if start == goal:
        return [start]
    for w in adj.get(start, []):
        if w not in seen:
            seen.add(w)
            sub = dfs_path(adj, w, goal, seen)
            if sub:
                return [start] + sub
    return None


def multi_source_bfs(adj, sources):
    """Every source starts at distance 0, all in the queue at once."""
    dist = {s: 0 for s in sources}
    q = deque(sources)
    while q:
        v = q.popleft()
        for w in adj.get(v, []):
            if w not in dist:
                dist[w] = dist[v] + 1
                q.append(w)
    return dist


def path_weight(path, weights):
    return sum(weights[tuple(sorted((a, b)))] for a, b in zip(path, path[1:]))


if __name__ == "__main__":
    G = build([("A", "B"), ("A", "C"), ("B", "D"), ("C", "D"),
               ("D", "E"), ("C", "F"), ("F", "E")])

    print("Block 1 - BFS explores by level")
    dist, levels = bfs_levels(G, "A")
    for i, lvl in enumerate(levels):
        print(f"    level {i}: {sorted(lvl)}")
    print(f"  distances from A: {dict(sorted(dist.items()))}")
    assert dist["A"] == 0 and dist["B"] == 1 and dist["E"] == 3

    print()
    print("Block 2 - BFS gives the SHORTEST path; DFS gives A path")
    print("   start  goal   BFS path            len   DFS path                  len")
    for start, goal in [("A", "E"), ("A", "D"), ("B", "F")]:
        bp = bfs_path(G, start, goal)
        dp = dfs_path(G, start, goal)
        print(f"     {start}     {goal}    {str(bp):20}{len(bp)-1:4}   {str(dp):24}{len(dp)-1:4}")
        assert len(bp) <= len(dp), "BFS is never longer"
    bp, dp = bfs_path(G, "A", "E"), dfs_path(G, "A", "E")
    assert len(bp) < len(dp), "on this graph DFS is strictly worse"
    print("  BFS is never longer, and here it is strictly shorter.")
    print("  The reason: BFS finishes every vertex at distance k before starting")
    print("  any at distance k+1, so the first time it reaches the goal is the closest.")

    print()
    print("Block 3 - multi-source BFS: every source starts at zero")
    grid_edges = []
    R, C = 4, 5
    for r in range(R):
        for c in range(C):
            if r + 1 < R: grid_edges.append(((r, c), (r + 1, c)))
            if c + 1 < C: grid_edges.append(((r, c), (r, c + 1)))
    grid = build(grid_edges)
    single = bfs_levels(grid, (0, 0))[0]
    multi = multi_source_bfs(grid, [(0, 0), (3, 4)])
    print("   distance from (0,0) alone      distance from EITHER corner")
    for r in range(R):
        row1 = " ".join(f"{single[(r,c)]:2}" for c in range(C))
        row2 = " ".join(f"{multi[(r,c)]:2}" for c in range(C))
        print(f"     {row1}              {row2}")
    assert multi[(3, 4)] == 0 and single[(3, 4)] == 7
    print("  one queue, two starting points, one pass - not two separate searches.")
    print("  This is how 'nearest exit', 'rotting oranges' and 'walls and gates' work.")

    print()
    print("Block 4 - where the guarantee ends: weighted edges")
    weights = {("A", "B"): 1, ("A", "C"): 1, ("B", "D"): 1, ("C", "D"): 1,
               ("D", "E"): 50, ("C", "F"): 1, ("E", "F"): 1}
    bp = bfs_path(G, "A", "E")
    alt = ["A", "C", "F", "E"]
    print(f"  BFS path      {bp}  -> {len(bp)-1} edges, total weight {path_weight(bp, weights)}")
    print(f"  alternative   {alt}  -> {len(alt)-1} edges, total weight {path_weight(alt, weights)}")
    assert path_weight(alt, weights) < path_weight(bp, weights)
    print("  Both paths have the SAME edge count, and BFS returned the heavier one -")
    print("  it had no reason to prefer either, because it never looks at weight.")
    print("  BFS minimises edge COUNT. When edges have differing costs that is")
    print("  the wrong objective, and you need Dijkstra.")

    print()
    print("Block 5 - BFS vs DFS memory on a wide graph")
    wide = build([("root", f"child{i}") for i in range(1000)])
    d, lv = bfs_levels(wide, "root")
    print(f"  a star with 1,000 leaves: BFS level 1 holds {len(lv[1]):,} vertices at once")
    print(f"  DFS on the same graph never holds more than 2 on its stack")
    print("  BFS memory is the widest LEVEL; DFS memory is the DEEPEST PATH.")
    print("  Wide-and-shallow favours DFS; deep-and-narrow favours BFS.")
    assert len(lv[1]) == 1000

    print()
    print("bfs_lab: passed")
```

Expected output:

```
Block 1 - BFS explores by level
    level 0: ['A']
    level 1: ['B', 'C']
    level 2: ['D', 'F']
    level 3: ['E']
  distances from A: {'A': 0, 'B': 1, 'C': 1, 'D': 2, 'E': 3, 'F': 2}

Block 2 - BFS gives the SHORTEST path; DFS gives A path
   start  goal   BFS path            len   DFS path                  len
     A     E    ['A', 'B', 'D', 'E']   3   ['A', 'B', 'D', 'C', 'F', 'E']   5
     A     D    ['A', 'B', 'D']        2   ['A', 'B', 'D']            2
     B     F    ['B', 'A', 'C', 'F']   3   ['B', 'A', 'C', 'D', 'E', 'F']   5
  BFS is never longer, and here it is strictly shorter.
  The reason: BFS finishes every vertex at distance k before starting
  any at distance k+1, so the first time it reaches the goal is the closest.

Block 3 - multi-source BFS: every source starts at zero
   distance from (0,0) alone      distance from EITHER corner
      0  1  2  3  4               0  1  2  3  3
      1  2  3  4  5               1  2  3  3  2
      2  3  4  5  6               2  3  3  2  1
      3  4  5  6  7               3  3  2  1  0
  one queue, two starting points, one pass - not two separate searches.
  This is how 'nearest exit', 'rotting oranges' and 'walls and gates' work.

Block 4 - where the guarantee ends: weighted edges
  BFS path      ['A', 'B', 'D', 'E']  -> 3 edges, total weight 52
  alternative   ['A', 'C', 'F', 'E']  -> 3 edges, total weight 3
  Both paths have the SAME edge count, and BFS returned the heavier one -
  it had no reason to prefer either, because it never looks at weight.
  BFS minimises edge COUNT. When edges have differing costs that is
  the wrong objective, and you need Dijkstra.

Block 5 - BFS vs DFS memory on a wide graph
  a star with 1,000 leaves: BFS level 1 holds 1,000 vertices at once
  DFS on the same graph never holds more than 2 on its stack
  BFS memory is the widest LEVEL; DFS memory is the DEEPEST PATH.
  Wide-and-shallow favours DFS; deep-and-narrow favours BFS.

bfs_lab: passed
```

Block 4 is the one to remember. BFS is not "the shortest path algorithm" — it is the **fewest edges** algorithm, and those coincide only when every edge costs the same.

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

## Practice — independent task

Implement `word_ladder(begin, end, wordlist)` — the shortest chain of one-letter changes from one word to another.

1. The graph is **implicit**: never build it. Generate neighbours by trying each position with each letter and keeping those in the word list.
2. Return the actual chain, not just its length, using a parent map.
3. **Measure the naive neighbour cost.** Comparing against every word is $O(N \cdot L)$ per expansion. Replace it with the wildcard-bucket trick: pre-index words by patterns like `h*t`. Report the speed-up in neighbour lookups for a list of a few thousand words.
4. Implement **bidirectional BFS** — search from both ends and stop when the frontiers meet. Count vertices expanded by each method.
5. Explain the improvement with numbers: if the branching factor is $b$ and the answer is at depth $d$, one-directional BFS expands about $b^d$ and bidirectional about $2b^{d/2}$. Confirm the ratio you actually observe, and say whether it matches.

**Edge cases:** `end` not in the word list (no ladder exists); `begin == end`; words of differing lengths; an empty word list.

**Done when:** your ladder is verifiable — every consecutive pair differs in exactly one position and every word is in the list — bidirectional BFS returns the same length as plain BFS, and your step-5 ratio is backed by counts you measured.

## Before moving on

You can implement BFS, reconstruct paths, use multi-source BFS, and state exactly where the shortest-path guarantee stops.

**Recap:** BFS uses a **queue** and explores level by level; $O(V+E)$ time; memory is the widest level, where DFS's is the deepest path; the first time BFS reaches a vertex is via the fewest edges, which is why it gives shortest paths on **unweighted** graphs only; multi-source BFS seeds the queue with every source at distance 0; with weighted edges, use [[06-dijkstra|Dijkstra]].

**Next:** [[04-sorting/index|Sorting]], then [[05-searching|Searching]] — or jump straight to [[06-dijkstra|Dijkstra]], which is BFS with a priority queue.

## Related Modules
- [[02-dfs|Depth-First Search (DFS)]] — Deep exploration traversal
- [[06-graphs/index|Graphs]] — Graph definitions and adjacency lists
- [[06-dijkstra|Dijkstra's Algorithm]] — Shortest path for weighted graphs
- [[07-stacks-and-queues|Stacks & Queues]] — Queue mechanics (`collections.deque`)

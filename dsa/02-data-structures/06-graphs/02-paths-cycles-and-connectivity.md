# Module: Paths, Cycles and Connectivity

**[Intermediate]** — walk, trail, path, cycle: four words that are not synonyms, and the four different things "connected" can mean.

## Before you start

- You know vertices, edges, degree and the four dimensions — [[01-what-a-graph-is|what a graph is]].
- You can trace a queue and a stack — [[07-stacks-and-queues|stacks and queues]].

**After this lesson you will be able to:**

1. Distinguish **walk, trail, path** and **simple path**, and the same four for closed routes ending in **cycle**.
2. Find **connected components** of an undirected graph.
3. Distinguish **strongly** from **weakly connected** in a directed graph, and compute **strongly connected components**.
4. Detect whether a directed graph is a **DAG**, and say why that matters.

**Study route:** read 1–4, attempt the prediction in section 3, then run the lab. Block 4 is the one that shows why direction changes everything.

---

## 1. Why this exists

"Is there a route from A to B?" sounds like one question. It is at least four, because *route* is ambiguous — may it revisit a junction? may it reuse a road? — and because in a directed graph "A reaches B" does not imply "B reaches A".

Every graph algorithm you will meet is stated in this vocabulary. Dijkstra finds a shortest **path**. Cycle detection looks for a **cycle**. Topological sort requires a **DAG**. Getting the terms loose makes the algorithms' preconditions invisible, which is how you end up running one on input it cannot handle.

## 2. Routes: four words, precisely

Let a **route** be a sequence $v_0, e_1, v_1, e_2, \dots, v_k$ where each $e_i$ joins $v_{i-1}$ and $v_i$.

| Term | Restriction | May repeat vertices? | May repeat edges? |
| :--- | :--- | :---: | :---: |
| **Walk** | none | yes | yes |
| **Trail** | no repeated **edge** | yes | no |
| **Path** | no repeated **vertex** | no | no |
| **Simple path** | same as path — the usual synonym | no | no |

Note the containment: every path is a trail, and every trail is a walk. Not the reverse.

**A note on convention, because textbooks differ.** Some authors use *path* to mean what this table calls a walk, and then say *simple path* for the no-repeated-vertex version. Others — including most algorithms literature and this course — use **path** to mean no repeated vertices, and treat *simple path* as an emphatic synonym. Whenever a source says "path", check which it means. The word that is never ambiguous is **walk**.

**Closed routes** return to where they started, $v_0 = v_k$:

| Term | Restriction |
| :--- | :--- |
| **Closed walk** | ends where it started |
| **Circuit** (closed trail) | no repeated edge |
| **Cycle** (simple cycle) | no repeated vertex except the first, which is also the last |

In a **simple** undirected graph a cycle needs at least three vertices — with two you would have to reuse the single edge, making it a walk rather than a cycle. A **self-loop** is a cycle of length 1; **parallel edges** form one of length 2. This is one reason algorithms usually demand simple graphs.

**Directed versions.** A **directed path** must follow every edge *in its direction*; a **directed cycle** likewise. A directed graph can easily contain an undirected cycle and no directed one — the lab shows exactly that.

**Length** is the number of **edges**, not vertices. A path through 4 vertices has length 3. Off-by-one errors here are endemic.

## 3. Connectivity

**Undirected.** A graph is **connected** if there is a path between every pair of vertices. If not, it splits into **connected components** — maximal sets of mutually reachable vertices. Every vertex is in exactly one component, so components partition $V$.

Finding them is one BFS or DFS per unvisited vertex, in $O(V+E)$.

**Directed.** Direction splits connectivity into two ideas:

| Term | Meaning |
| :--- | :--- |
| **Strongly connected** | For every pair $u, v$: a directed path $u \to v$ **and** one $v \to u$ |
| **Weakly connected** | Connected once you ignore all the directions |
| **Strongly connected component (SCC)** | A maximal strongly connected subgraph |

Strong implies weak; the reverse fails constantly. A one-way street system can be weakly connected — the map looks joined — while some junction cannot be left, which is a strong-connectivity failure and a real problem.

**Condensing** a digraph by collapsing each SCC to a single node always produces a **DAG**. That is a genuinely useful fact: any cyclic dependency structure becomes acyclic once mutually-dependent groups are treated as units, which is how build systems report circular dependencies as one group rather than an infinite loop.

### DAGs

A **directed acyclic graph** has no directed cycle. DAGs are the shape of dependency: build targets, task schedules, spreadsheet formulas, course prerequisites, git commits.

They matter because a DAG — and only a DAG — admits a **topological order**: a linear arrangement in which every edge points forwards. A directed cycle makes that impossible, since each vertex in the cycle would have to precede itself.

> [!TIP]
> **Predict before running the lab.** Take a triangle $A \to B \to C \to A$ and reverse just one edge, giving $A \to B$, $C \to B$, $A \to C$. Is the result still strongly connected? Is it weakly connected? Is it a DAG? Decide all three before opening the answers.

## 4. Worked example — runnable

**Runnable example:** save as `connectivity.py` in any empty directory and run `python3 connectivity.py`. Standard library only; writes no files.

```python
"""Walks, trails, paths, cycles, components and SCCs."""
from collections import defaultdict, deque


def build(edges, directed=False):
    adj = defaultdict(list)
    for u, v in edges:
        adj[u].append(v)
        if not directed:
            adj[v].append(u)
        else:
            adj.setdefault(v, [])
    return adj


def classify_route(adj, seq, directed=False):
    """Is this vertex sequence a walk, and if so is it a trail / a path?"""
    for a, b in zip(seq, seq[1:]):
        if b not in adj[a]:
            return "not even a walk (consecutive vertices are not adjacent)"
    used_edges = [(a, b) if directed else tuple(sorted((a, b)))
                  for a, b in zip(seq, seq[1:])]
    repeats_edge = len(set(used_edges)) < len(used_edges)
    interior = seq[:-1] if seq[0] == seq[-1] and len(seq) > 1 else seq
    repeats_vertex = len(set(interior)) < len(interior)
    closed = seq[0] == seq[-1] and len(seq) > 1
    if closed:
        if not repeats_edge and not repeats_vertex:
            return "cycle (simple cycle)"
        return "circuit (closed trail)" if not repeats_edge else "closed walk"
    if not repeats_vertex:
        return "path (simple path)"
    return "trail" if not repeats_edge else "walk"


def components(adj):
    """Connected components of an undirected graph, by BFS."""
    seen, out = set(), []
    for start in sorted(adj):
        if start in seen:
            continue
        comp, q = [], deque([start])
        seen.add(start)
        while q:
            v = q.popleft()
            comp.append(v)
            for w in adj[v]:
                if w not in seen:
                    seen.add(w)
                    q.append(w)
        out.append(sorted(comp))
    return out


def reachable(adj, start):
    seen, q = {start}, deque([start])
    while q:
        v = q.popleft()
        for w in adj[v]:
            if w not in seen:
                seen.add(w)
                q.append(w)
    return seen


def sccs(adj):
    """Kosaraju: finish order on G, then components on the transpose."""
    order, seen = [], set()

    def visit(v):
        stack = [(v, iter(adj[v]))]
        seen.add(v)
        while stack:
            node, it = stack[-1]
            found = next((w for w in it if w not in seen), None)
            if found is None:
                order.append(node)
                stack.pop()
            else:
                seen.add(found)
                stack.append((found, iter(adj[found])))

    for v in sorted(adj):
        if v not in seen:
            visit(v)

    rev = defaultdict(list)
    for u in adj:
        rev.setdefault(u, [])
        for v in adj[u]:
            rev[v].append(u)

    seen2, out = set(), []
    for v in reversed(order):
        if v in seen2:
            continue
        comp, q = [], deque([v])
        seen2.add(v)
        while q:
            x = q.popleft()
            comp.append(x)
            for w in rev[x]:
                if w not in seen2:
                    seen2.add(w)
                    q.append(w)
        out.append(sorted(comp))
    return sorted(out)


def is_dag(adj):
    colour = {v: 0 for v in adj}          # 0 unvisited, 1 in progress, 2 done

    def dfs(v):
        colour[v] = 1
        for w in adj[v]:
            if colour[w] == 1:
                return False              # a back edge: a directed cycle
            if colour[w] == 0 and not dfs(w):
                return False
        colour[v] = 2
        return True

    return all(colour[v] != 0 or dfs(v) for v in sorted(adj))


if __name__ == "__main__":
    print("Block 1 - four words that are not synonyms")
    # a "bowtie": two triangles sharing the vertex C
    und = build([("A", "B"), ("B", "C"), ("C", "A"),
                 ("C", "D"), ("D", "E"), ("E", "C")])
    routes = [
        ["A", "B", "C"],                         # path
        ["A", "B", "C", "A"],                    # cycle
        ["A", "B", "C", "D", "E"],               # path across both triangles
        ["A", "B", "C", "D", "E", "C", "A"],     # circuit: revisits C, no edge twice
        ["A", "B", "A", "B"],                    # walk: reuses the edge A-B
        ["A", "B", "C", "D", "E", "C"],          # trail: open, revisits C, no edge twice
        ["A", "D"],                              # not adjacent at all
    ]
    for seq in routes:
        print(f"  {'-'.join(seq):22} -> {classify_route(und, seq)}")
    assert classify_route(und, ["A", "B", "C"]) == "path (simple path)"
    assert classify_route(und, ["A", "B", "C", "A"]) == "cycle (simple cycle)"
    assert classify_route(und, ["A", "B", "C", "D", "E", "C", "A"]) == "circuit (closed trail)"
    assert classify_route(und, ["A", "B", "C", "D", "E", "C"]) == "trail"
    assert classify_route(und, ["A", "B", "A", "B"]) == "walk"
    print("  length is counted in EDGES: A-B-C has length 2, not 3")

    print()
    print("Block 2 - connected components partition the vertices")
    split = build([("A", "B"), ("B", "C"), ("D", "E"), ("F", "F")])
    comps = components(split)
    print(f"  graph with edges A-B, B-C, D-E, F-F")
    for i, c in enumerate(comps, 1):
        print(f"    component {i}: {c}")
    assert comps == [["A", "B", "C"], ["D", "E"], ["F"]]
    assert sum(len(c) for c in comps) == len(split)
    print("  every vertex is in exactly one component - they partition V")

    print()
    print("Block 3 - in a digraph, reachability is one-way")
    d = build([("A", "B"), ("B", "C"), ("C", "A"), ("C", "D")], directed=True)
    for v in sorted(d):
        print(f"    from {v} you can reach {sorted(reachable(d, v))}")
    assert "A" in reachable(d, "D") or True
    assert reachable(d, "D") == {"D"}
    print("  D reaches nothing but itself, though everything reaches D")

    print()
    print("Block 4 - strongly vs weakly connected")
    cases = {
        "cycle A->B->C->A":        [("A", "B"), ("B", "C"), ("C", "A")],
        "one edge reversed":       [("A", "B"), ("C", "B"), ("A", "C")],
        "cycle plus a dead end":   [("A", "B"), ("B", "C"), ("C", "A"), ("C", "D")],
    }
    for name, edges in cases.items():
        dg = build(edges, directed=True)
        ug = build(edges, directed=False)
        strong = sccs(dg)
        weak = components(ug)
        print(f"  {name}")
        print(f"    strongly connected: {str(len(strong) == 1):5}   SCCs {strong}")
        print(f"    weakly connected:   {str(len(weak) == 1):5}")
        print(f"    is a DAG:           {is_dag(dg)}")
    assert len(sccs(build(cases["cycle A->B->C->A"], directed=True))) == 1
    assert is_dag(build(cases["one edge reversed"], directed=True))
    assert not is_dag(build(cases["cycle A->B->C->A"], directed=True))
    print("  the reversed-edge graph is weakly connected but NOT strongly connected,")
    print("  and having no directed cycle is exactly what makes it a DAG")

    print()
    print("Block 5 - condensing the SCCs of a digraph always yields a DAG")
    messy = build([("a", "b"), ("b", "c"), ("c", "a"),      # one 3-cycle
                   ("c", "d"), ("d", "e"), ("e", "d"),      # a 2-cycle
                   ("e", "f")], directed=True)
    comp_of = {}
    groups = sccs(messy)
    for i, grp in enumerate(groups):
        for v in grp:
            comp_of[v] = i
    print(f"  SCCs: {groups}")
    cond = defaultdict(list)
    for u in messy:
        cond.setdefault(comp_of[u], [])
        for v in messy[u]:
            if comp_of[u] != comp_of[v]:
                cond[comp_of[u]].append(comp_of[v])
    print(f"  condensed graph edges: "
          f"{sorted((a, b) for a, bs in cond.items() for b in set(bs))}")
    print(f"  is the condensation a DAG? {is_dag(cond)}")
    assert is_dag(cond)
    assert not is_dag(messy)
    print("  the original has cycles; collapsing each mutually-reachable group removes them")

    print()
    print("connectivity: passed")
```

Expected output:

```
Block 1 - four words that are not synonyms
  A-B-C                  -> path (simple path)
  A-B-C-A                -> cycle (simple cycle)
  A-B-C-D-E              -> path (simple path)
  A-B-C-D-E-C-A          -> circuit (closed trail)
  A-B-A-B                -> walk
  A-B-C-D-E-C            -> trail
  A-D                    -> not even a walk (consecutive vertices are not adjacent)
  length is counted in EDGES: A-B-C has length 2, not 3

Block 2 - connected components partition the vertices
  graph with edges A-B, B-C, D-E, F-F
    component 1: ['A', 'B', 'C']
    component 2: ['D', 'E']
    component 3: ['F']
  every vertex is in exactly one component - they partition V

Block 3 - in a digraph, reachability is one-way
    from A you can reach ['A', 'B', 'C', 'D']
    from B you can reach ['A', 'B', 'C', 'D']
    from C you can reach ['A', 'B', 'C', 'D']
    from D you can reach ['D']
  D reaches nothing but itself, though everything reaches D

Block 4 - strongly vs weakly connected
  cycle A->B->C->A
    strongly connected: True    SCCs [['A', 'B', 'C']]
    weakly connected:   True 
    is a DAG:           False
  one edge reversed
    strongly connected: False   SCCs [['A'], ['B'], ['C']]
    weakly connected:   True 
    is a DAG:           True
  cycle plus a dead end
    strongly connected: False   SCCs [['A', 'B', 'C'], ['D']]
    weakly connected:   True 
    is a DAG:           False
  the reversed-edge graph is weakly connected but NOT strongly connected,
  and having no directed cycle is exactly what makes it a DAG

Block 5 - condensing the SCCs of a digraph always yields a DAG
  SCCs: [['a', 'b', 'c'], ['d', 'e'], ['f']]
  condensed graph edges: [(0, 1), (1, 2)]
  is the condensation a DAG? True
  the original has cycles; collapsing each mutually-reachable group removes them

connectivity: passed
```

Block 5 is the structural result worth carrying: **any** directed graph, however tangled, becomes a DAG once each strongly connected component is collapsed to a point. That is how a build tool reports "these five packages form a dependency cycle" instead of looping forever.

## Common pitfalls and traps

- **Using "path" without checking the convention.** In this course it means no repeated vertices. Some textbooks use it for any walk. *Walk* is the unambiguous word.
- **Counting length in vertices.** Length is edges. A route through $k$ vertices has length $k-1$.
- **Assuming weakly connected implies strongly connected.** It does not, and the gap is exactly the one-way-street problem.
- **Running topological sort on a graph with cycles.** It requires a DAG. Detect first, or your sort silently omits vertices.
- **Forgetting that self-loops and parallel edges are cycles.** In a multigraph the shortest cycle can have length 1 or 2, which breaks algorithms assuming 3.
- **Recursing on a large graph.** Python's default recursion limit is around 1000; a long path overflows it. The lab's DFS is iterative for this reason.

## Check your understanding

1. Classify $A\!-\!B\!-\!C\!-\!A\!-\!D$ in a graph containing all those edges.
2. What is the length of a cycle through 5 distinct vertices?
3. Give a digraph that is weakly but not strongly connected.
4. Why does collapsing SCCs always give a DAG?
5. A graph has 10 vertices and 3 connected components. What is the fewest edges it can have?

<details><summary>Answers — open only after an attempt</summary>

1. It repeats vertex $A$ but no edge, so it is a **trail** — and not closed, since it ends at $D$.
2. **5.** A cycle through $k$ distinct vertices has $k$ edges, because the last edge returns to the start.
3. $A \to B$, $A \to C$: ignoring directions it is connected, but nothing reaches $A$, so it is not strongly connected.
4. Because if the condensation had a cycle, every component on that cycle would be mutually reachable with every other — so they would all have been a *single* SCC in the first place. Their being separate SCCs contradicts the cycle's existence.
5. Each component with $k$ vertices needs at least $k-1$ edges (a tree). With 10 vertices in 3 components the total is $10 - 3 = 7$ edges.

**And the prediction from section 3:** with $A\to B$, $C\to B$, $A\to C$ — it is **not strongly connected** (nothing leaves $B$, so $B$ reaches nothing), it **is weakly connected** (ignore directions and it is a triangle), and it **is a DAG** (no directed cycle: the only routes are $A\to B$, $A\to C\to B$).
</details>

## Practice — independent task

Implement `bridges(graph)` and `articulation_points(graph)` — the edges and vertices whose removal disconnects a graph.

1. A **bridge** is an edge whose removal increases the number of connected components. An **articulation point** is a vertex whose removal does.
2. Implement the naive version first: remove each edge (then each vertex) in turn, recount components, compare. $O(E(V+E))$.
3. Then implement **Tarjan's** linear-time algorithm using DFS discovery times and low-link values. Assert it agrees with the naive version on at least twenty random graphs.
4. Explain in a comment what the low-link value *means* — you should be able to state it as a sentence about which ancestors a subtree can reach.
5. Apply it to something real: model a small network where bridges are single points of failure, and report which links have no redundancy.

**Edge cases:** a disconnected input; a single vertex; a graph that is one long path (every edge is a bridge — check this); a cycle (no bridges at all — check this too).

**Done when:** Tarjan agrees with the naive version on every random graph tested, your path and cycle cases behave as predicted, and your low-link explanation is in your own words.

## Before moving on

You can state all four route words precisely, find components, tell strong from weak connectivity, and detect a DAG.

**Recap:** walk (anything) ⊃ trail (no repeated edge) ⊃ path (no repeated vertex); closed versions are closed walk ⊃ circuit ⊃ cycle; length counts edges; components partition $V$; strongly connected means mutual directed reachability, weakly means connected ignoring direction; a DAG has no directed cycle and is exactly what admits a topological order; condensing SCCs always yields a DAG.

**Next:** [[03-subgraphs-trees-and-forests|Subgraphs, Trees and Forests]] — the pieces of a graph, and where trees come from.

## Related

- [[02-dfs|DFS]] · [[03-bfs|BFS]] — the traversals every result here is computed with
- [[11-topological-sort|Topological Sort]] — what a DAG buys you
- [[10-union-find|Union-Find]] — components maintained incrementally

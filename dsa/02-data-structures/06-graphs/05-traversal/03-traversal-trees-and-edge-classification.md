# Module: Traversal Trees and Edge Classification (What the Search Leaves Behind)

**[Intermediate]** — A traversal does not only *visit* vertices. It **builds a tree** out of the edges it used, and sorts every other edge into one of three kinds. Almost every "clever" graph algorithm you will meet — cycle detection, topological sort, strongly connected components, bipartite checking, bridges and articulation points — is a rule about that classification rather than a new search.

This is the lesson that turns [[01-depth-first-search|DFS]] and [[02-breadth-first-search|BFS]] from *ways to touch every vertex* into *ways to learn the structure of a graph*.

---

## Before you start

- You can implement DFS recursively and iteratively, and say what the explicit stack replaces — [[01-depth-first-search|depth-first search]].
- You can implement BFS with a queue and reconstruct a path from a parent map — [[02-breadth-first-search|breadth-first search]].
- You can say precisely what a **path**, a **cycle** and a **directed cycle** are, and what makes a graph a **DAG (directed acyclic graph)** — [[02-paths-cycles-and-connectivity|paths, cycles and connectivity]].
- You know that a **tree** is a connected acyclic graph with $V-1$ edges — [[03-subgraphs-trees-and-forests|subgraphs, trees and forests]].

**After this lesson you will be able to:**

1. Compute **discovery and finish times** for a DFS by hand, and use them to decide whether one vertex is an ancestor of another.
2. Classify every edge of a directed graph as **tree, back, forward or cross**, and justify each from the timestamps alone.
3. Explain *why* "the graph has a directed cycle" and "a DFS finds a back edge" are the same statement — and why this is the correctness argument behind DFS-based topological sort.
4. State what changes for **undirected** graphs and for **BFS**, and say which parts of the classification are properties of the graph and which are artefacts of where you started.

**Study route:** read 1–4, stop at the prediction in section 5 and answer it before reading on, then run the lab. Sections 8 and 9 are where the payoff is.

---

## 1. Why this exists: the search knows more than it tells you

Here is a question a dependency resolver has to answer, and it sounds like it needs a new algorithm:

> Build A needs B. B needs C. C needs A. **Is this build order possible?**

You already know the answer is no, because $A \to B \to C \to A$ is a directed cycle. But how would a program *find* that cycle without checking every possible ordering, of which there are $V!$?

The naive fix is tempting and wrong: "run DFS, and if you ever meet a vertex you have already visited, there is a cycle." Try it on this graph, which has **no cycle at all**:

```
    A ──▶ B ──▶ D
    │            ▲
    └──▶ C ──────┘
```

Starting at `A`: visit `A`, visit `B`, visit `D`, back up, visit `C`, and from `C` look at `D` — already visited. The naive rule reports a cycle. There is none. `A → C → D` is simply a second, separate route to `D`.

**"Already visited" is one bit, and one bit is not enough.** The vertex `D` was already visited, but it was *finished* — the search had left it and come back out. The vertex `A` in the real cycle would have been already visited and *still on the current path*. Those are different situations and they need different answers, so they need more than a visited set to tell apart.

Everything in this lesson comes from that one observation: **record not just whether you visited a vertex, but when you arrived and when you left.**

---

## Terms used in traversal trees

1. **Traversal tree**: This is the subgraph made up of exactly the edges the traversal used to reach a vertex for the first time. Every vertex except the starting one is reached by exactly one such edge, so these edges form a tree. In the graph above, `A→B`, `B→D` and `A→C` are the traversal tree; `C→D` is not in it, because `D` had already been reached.
2. **Traversal forest**: This is what you get when one traversal is not enough to reach everything. If some vertices are still unvisited after the search from the first source finishes, you start a fresh search from one of them, which grows a second tree. The collection of those trees is a forest.
3. **DFS tree**: This is also called a **depth-first tree**. This is the traversal tree built by a depth-first search specifically. Its shape is long and narrow, because DFS keeps descending.
4. **BFS tree**: This is also called a **breadth-first tree** or a **shortest-path tree**. This is the traversal tree built by a breadth-first search. Its shape is short and wide, and every root-to-vertex path in it is a shortest path in the original graph, measured in number of edges.
5. **Discovery time**: This is also written $d[v]$ and called the **entry time** or **arrival time**. This is the value of a counter at the moment the search first arrives at vertex $v$ and colours it grey. In the lab below, `u` has discovery time 1 because it is the first vertex entered.
6. **Finish time**: This is also written $f[v]$ and called the **exit time** or **departure time**. This is the value of the same counter at the moment the search has examined every edge out of $v$ and leaves it for good. In the lab, `x` has finish time 5, meaning the search left `x` before it left `y`, `v` or `u`.
7. **Ancestor**: This is a vertex that lies on the traversal-tree path from the root down to another vertex. If `u` is an ancestor of `x`, then the search entered `u`, and had not yet left `u`, when it entered `x`.
8. **Descendant**: This is the other end of that relationship. If `u` is an ancestor of `x`, then `x` is a descendant of `u`. Every vertex is trivially both an ancestor and a descendant of itself.
9. **Tree edge**: This is an edge the search used to reach a previously unvisited vertex — that is, an edge of the traversal tree. `A→B` above is a tree edge.
10. **Back edge**: This is an edge from a vertex to one of its own ancestors in the traversal tree. It points *backwards* up the current path. A self-loop counts as a back edge, because a vertex is its own ancestor.
11. **Forward edge**: This is an edge from a vertex to one of its descendants, where that descendant was reached by some *other*, longer route first. It is a shortcut down the tree that the search did not need. `A→D` would be a forward edge if the search had gone `A→B→D` first.
12. **Cross edge**: This is an edge between two vertices where neither is an ancestor of the other. It jumps sideways — between two different branches of one tree, or between two different trees of the forest. `C→D` in the graph above is a cross edge.
13. **White / grey / black**: This is the three-colour scheme for a vertex's state during DFS. **White** means not yet discovered. **Grey** means discovered but not finished — the search is currently somewhere inside it, so it is on the recursion stack. **Black** means finished. The whole difficulty in the motivating example was that a visited set merges grey and black into one bit.

---

## 2. The clock, and what a timestamp pair means

Give the search a counter that starts at zero and ticks by one on two occasions: **entering** a vertex, and **leaving** it. Record the value both times.

Each vertex therefore gets an interval $[\,d[v],\ f[v]\,]$. With $V$ vertices, the counter ends at $2V$, because every vertex is entered once and left once.

Write those intervals as brackets and something immediately becomes visible. Take the graph used in the lab:

```
        u ──────▶ v ──────▶ y
        │         ▲         │
        │         │         │
        └────────▶x ◀───────┘

        w ──────▶ z ──┐          w ──────▶ y
        ▲             │
        └─────────────┘  (z has a self-loop)
```

Depth-first from `u`, taking neighbours in the order listed, produces:

| Vertex | $d$ | $f$ | Parent in the DFS tree |
| :--- | ---: | ---: | :--- |
| `u` | 1 | 8 | — (root) |
| `v` | 2 | 7 | `u` |
| `y` | 3 | 6 | `v` |
| `x` | 4 | 5 | `y` |
| `w` | 9 | 12 | — (root of the second tree) |
| `z` | 10 | 11 | `w` |

As a timeline, where `(u` means "entered u" and `u)` means "left u":

```
 1   2   3   4   5   6   7   8    9   10   11   12
 (u  (v  (y  (x  x)  y)  v)  u)   (w  (z   z)   w)
 └───────────────────────────┘    └──────────────┘
        first DFS tree             second DFS tree
```

**The intervals nest.** `x`'s interval $[4,5]$ sits entirely inside `y`'s $[3,6]$, which sits inside `v`'s $[2,7]$, which sits inside `u`'s $[1,8]$. And `w`'s $[9,12]$ is entirely disjoint from all of them.

### The parenthesis theorem

**State it in words first.** For any two vertices in a depth-first search, their discovery/finish intervals are either completely nested one inside the other, or completely disjoint — they can never partially overlap. And nesting is exactly ancestry: one interval sits inside another precisely when the outer vertex is an ancestor of the inner one.

$$\text{$u$ is an ancestor of $x$} \iff d[u] < d[x] < f[x] < f[u]$$

**Why it must be true.** The search leaves a vertex only after every edge out of it has been examined, and examining an edge means the whole search below it has already returned. So if the search enters `x` while it is still inside `u`, it cannot leave `u` until it has left `x`. There is no mechanism by which the brackets could interleave — the call stack physically prevents it. This is the same reason you cannot close a function call before closing the calls it made.

**This is what makes ancestry a constant-time test.** Once you have the timestamps, asking "is `u` an ancestor of `x`?" is two integer comparisons, not a walk up the tree.

---

## 3. Classifying an edge from the timestamps alone

Now take any edge $u \to v$ and ask what kind it is. The colour of `v` at the moment DFS examines the edge answers it, and the rule is only three lines:

1. **`v` is white** — it has not been discovered. The search is about to discover it *through this edge*, so this is a **tree edge**.
2. **`v` is grey** — it has been discovered and not finished, so the search is currently inside `v`. That makes `v` an ancestor of `u`. This is a **back edge**.
3. **`v` is black** — it is finished. Two cases remain, separated by discovery time: if $d[u] < d[v]$, then `v` was discovered after `u` but has already finished, so `v` is a descendant of `u` and this is a **forward edge**. Otherwise $d[v] < d[u]$, `v` belongs to an earlier-finished part of the search, and this is a **cross edge**.

Applied to the running example:

| Edge | Colour of the target when examined | Kind | Why |
| :--- | :--- | :--- | :--- |
| `u → v` | white | tree | `v` first reached here |
| `v → y` | white | tree | `y` first reached here |
| `y → x` | white | tree | `x` first reached here |
| `x → v` | grey | **back** | `v` is still open ($d[v]{=}2 < d[x]{=}4 < f[x]{=}5 < f[v]{=}7$) |
| `u → x` | black | **forward** | `x` finished, and $d[u]{=}1 < d[x]{=}4$ — `x` is below `u` |
| `w → y` | black | **cross** | `y` finished, and $d[y]{=}3 < d[w]{=}9$ — different tree |
| `w → z` | white | tree | `z` first reached here |
| `z → z` | grey | **back** | a self-loop; `z` is its own ancestor |

Four tree edges, two back, one forward, one cross — eight edges, every one accounted for. **Every edge lands in exactly one of the four categories, always.** That is not a coincidence; the three rules above are exhaustive over the three possible colours.

---

## 4. Why a back edge *is* a cycle

This is the whole point, so it is worth stating both directions carefully.

**If DFS finds a back edge, the graph has a directed cycle.** A back edge $u \to v$ means `v` is an ancestor of `u`. Ancestor means there is a path of tree edges $v \rightsquigarrow u$. Append the back edge $u \to v$ and you have a closed directed walk that returns to `v` — a directed cycle. In the example, `v → y → x` are tree edges and `x → v` is the back edge, giving the cycle $v \to y \to x \to v$.

**If the graph has a directed cycle, DFS will find a back edge.** Let $C$ be a cycle and let `v` be the vertex of $C$ that DFS discovers *first*. Every other vertex of $C$ is reachable from `v` along $C$ without leaving $C$, and all of them are white when `v` is discovered. So DFS, exploring out of `v`, reaches all of them before finishing `v` — they all become descendants of `v`. In particular the vertex `p` that points *into* `v` along the cycle is a descendant of `v`, and `p` is still grey-or-below when the edge $p \to v$ is examined, with `v` grey. That edge is a back edge.

Together: **a directed graph is a DAG if and only if a DFS over it produces no back edges.** This is the correctness proof for DFS-based [[01-topological-sort|topological sort]], and it is why that algorithm gets cycle detection for free rather than as an extra pass.

> **Predict before you read on.** The running example has one forward edge (`u → x`) and one cross edge (`w → y`). Suppose you run the same DFS but visit `w` first instead of `u`. Which of these three counts changes — tree edges, back edges, forward/cross edges? Write down an answer before section 9 shows you the measured result.

---

## 5. Undirected graphs: two of the four kinds vanish

**An undirected DFS produces only tree edges and back edges. Forward and cross edges cannot occur.**

The reason is that an undirected edge has no preferred direction, so the search sees it from whichever end it reaches first, and *that end defines the classification*. Suppose an undirected edge $\{u, v\}$ and suppose the search reaches `u` first. Then while `u` is grey, the search examines the edge:

- If `v` is white, the search descends into it now, and the edge is a tree edge.
- If `v` is not white, `v` was discovered earlier and — crucially — cannot have finished yet, because finishing `v` would have required examining this very edge from `v`'s side, which would have discovered `u`. So `v` is grey, and the edge is a back edge.

There is no third option, so no forward and no cross edges. **A forward edge would be an edge to a descendant that the search "missed" on the way down, and in an undirected graph there is no way to miss it.**

**The trap this creates.** Because every undirected tree edge is also visible from the child looking back at its parent, a naive "grey neighbour means cycle" check reports a cycle on every single edge of every graph, including a two-vertex graph with one edge. The fix is to ignore the edge you arrived on — and to ignore it *by edge*, not by vertex, or parallel edges between the same pair (which genuinely are a cycle) get silently dropped too.

---

## 6. What BFS leaves behind instead

BFS builds a tree too, and it has a property DFS's tree does not.

**Every edge of the graph joins two vertices whose BFS levels differ by at most one.** If `u` is at level $k$, then every neighbour of `u` is discovered no later than the moment `u` is dequeued, so no neighbour can be at level $k+2$ or beyond — it would have been reached from `u` at level $k+1$ first. And by symmetry it cannot be at level $k-2$ either.

Two consequences worth holding onto:

1. **This is the shortest-path guarantee, restated.** The level of `v` *is* the minimum number of edges from the source to `v`, which is why BFS and not DFS answers "fewest hops".
2. **This is how you test bipartiteness.** Colour each level alternately. Every edge either crosses between consecutive levels (fine — its endpoints get different colours) or joins two vertices *within* one level. An edge inside a level is an odd cycle, and an odd cycle is exactly what stops a graph being bipartite. So: BFS, and check whether any edge has both endpoints on the same level.

DFS has no such bound. A DFS tree on a path graph of 5,000 vertices is 5,000 levels deep, and that is exactly the depth that kills the recursive implementation.

---

## 7. Worked example — complete runnable lab

Save as `edge_classification.py` in any empty directory. No dependencies beyond the standard library; nothing is written to disk.

```python
"""Classify every edge of a graph by the traversal tree DFS builds.

Run:  python3 edge_classification.py
"""

from collections import deque

# The running example. Adjacency lists are kept in a fixed order so the
# traversal — and therefore the classification — is reproducible.
DIRECTED = {
    "u": ["v", "x"],
    "v": ["y"],
    "w": ["y", "z"],
    "x": ["v"],
    "y": ["x"],
    "z": ["z"],
}

WHITE, GREY, BLACK = 0, 1, 2


def dfs_classify(graph, undirected=False):
    """Return (discovery, finish, parent, edges) for a full DFS forest.

    edges maps (u, v) -> one of "tree", "back", "forward", "cross".

    With undirected=True each undirected edge is classified once, at the first
    encounter. That matters: an undirected edge is stored as two arcs, and
    classifying both independently invents edge kinds that are not really there.
    """
    colour = {v: WHITE for v in graph}
    discovery, finish, parent = {}, {}, {}
    edges = {}
    clock = 0

    def visit(u):
        nonlocal clock
        clock += 1
        discovery[u] = clock
        colour[u] = GREY
        for v in graph[u]:
            if undirected and (v, u) in edges:
                continue                    # already classified from the other side
            if colour[v] == WHITE:
                # v is unvisited, so this edge is how we reach it: a tree edge.
                parent[v] = u
                edges[(u, v)] = "tree"
                visit(v)
            elif colour[v] == GREY:
                # v is still on the recursion stack, so v is an ancestor of u.
                # Going from u back up to an ancestor closes a cycle.
                edges[(u, v)] = "back"
            else:
                # v is finished. Discovery times decide which kind it is.
                edges[(u, v)] = "forward" if discovery[u] < discovery[v] else "cross"
        colour[u] = BLACK
        clock += 1
        finish[u] = clock

    for v in graph:
        if colour[v] == WHITE:
            visit(v)
    return discovery, finish, parent, edges


def is_descendant(a, d, discovery, finish):
    """True if d lies inside a's discovery/finish interval (the parenthesis theorem)."""
    return discovery[a] < discovery[d] and finish[d] < finish[a]


def bfs_levels(graph, source):
    level = {source: 0}
    queue = deque([source])
    while queue:
        u = queue.popleft()
        for v in graph[u]:
            if v not in level:
                level[v] = level[u] + 1
                queue.append(v)
    return level


def undirect(graph):
    out = {v: [] for v in graph}
    for u, vs in graph.items():
        for v in vs:
            if v == u:
                continue                    # drop self-loops
            if v not in out[u]:
                out[u].append(v)
            if u not in out[v]:
                out[v].append(u)
    return out


def main():
    d, f, parent, edges = dfs_classify(DIRECTED)

    print("=== 1. Discovery / finish times (DFS from 'u', then 'w') ===")
    for v in sorted(d, key=lambda x: d[x]):
        print(f"  {v}: ({d[v]}/{f[v]})  parent={parent.get(v, '-')}")

    print("\n=== 2. Every edge, classified ===")
    for (u, v), kind in edges.items():
        print(f"  {u} -> {v:<2} {kind}")

    counts = {}
    for kind in edges.values():
        counts[kind] = counts.get(kind, 0) + 1
    print(f"\n  totals: {counts}")
    print(f"  tree edges + non-tree edges = {sum(counts.values())} = |E|")

    print("\n=== 3. The parenthesis theorem holds for every pair ===")
    violations = 0
    for a in DIRECTED:
        for b in DIRECTED:
            if a == b:
                continue
            ia = (d[a], f[a])
            ib = (d[b], f[b])
            nested = is_descendant(a, b, d, f) or is_descendant(b, a, d, f)
            disjoint = ia[1] < ib[0] or ib[1] < ia[0]
            if not (nested or disjoint):
                violations += 1
    print(f"  pairs that are neither nested nor disjoint: {violations}  (must be 0)")

    print("\n=== 4. A back edge is exactly a directed cycle ===")
    for (u, v), kind in edges.items():
        if kind == "back":
            anc = "self-loop" if u == v else f"{v} is an ancestor of {u}"
            print(f"  {u} -> {v}: {anc} -> cycle")
    print(f"  graph has a directed cycle: {any(k == 'back' for k in edges.values())}")

    print("\n=== 5. Undirected DFS produces NO forward or cross edges ===")
    ud = undirect(DIRECTED)
    _, _, _, uedges = dfs_classify(ud, undirected=True)
    ucounts = {}
    for kind in uedges.values():
        ucounts[kind] = ucounts.get(kind, 0) + 1
    print(f"  {len(uedges)} undirected edges, each classified once")
    print(f"  undirected edge kinds: {ucounts}")
    print(f"  forward: {ucounts.get('forward', 0)}, cross: {ucounts.get('cross', 0)}  (both must be 0)")

    print("\n=== 6. BFS: every edge joins levels that differ by at most 1 ===")
    level = bfs_levels(ud, "u")
    worst = 0
    for u, vs in ud.items():
        for v in vs:
            if u in level and v in level:
                worst = max(worst, abs(level[u] - level[v]))
    print(f"  levels from 'u': {dict(sorted(level.items(), key=lambda kv: kv[1]))}")
    print(f"  largest level difference across any edge: {worst}  (DFS has no such bound)")

    print("\n=== 7. The same graph, DFS started from 'w' instead ===")
    reordered = {"w": DIRECTED["w"], **{k: v for k, v in DIRECTED.items() if k != "w"}}
    _, _, _, edges2 = dfs_classify(reordered)
    counts2 = {}
    for kind in edges2.values():
        counts2[kind] = counts2.get(kind, 0) + 1
    print(f"  totals now: {counts2}")
    print(f"  back-edge count unchanged: {counts.get('back', 0)} -> {counts2.get('back', 0)}")
    print(f"  forward/cross counts changed: {counts.get('forward', 0)}/{counts.get('cross', 0)}"
          f" -> {counts2.get('forward', 0)}/{counts2.get('cross', 0)}")


if __name__ == "__main__":
    main()
```

### Expected output

This is the output of an actual run, not a reconstruction:

```
=== 1. Discovery / finish times (DFS from 'u', then 'w') ===
  u: (1/8)  parent=-
  v: (2/7)  parent=u
  y: (3/6)  parent=v
  x: (4/5)  parent=y
  w: (9/12)  parent=-
  z: (10/11)  parent=w

=== 2. Every edge, classified ===
  u -> v  tree
  v -> y  tree
  y -> x  tree
  x -> v  back
  u -> x  forward
  w -> y  cross
  w -> z  tree
  z -> z  back

  totals: {'tree': 4, 'back': 2, 'forward': 1, 'cross': 1}
  tree edges + non-tree edges = 8 = |E|

=== 3. The parenthesis theorem holds for every pair ===
  pairs that are neither nested nor disjoint: 0  (must be 0)

=== 4. A back edge is exactly a directed cycle ===
  x -> v: v is an ancestor of x -> cycle
  z -> z: self-loop -> cycle
  graph has a directed cycle: True

=== 5. Undirected DFS produces NO forward or cross edges ===
  7 undirected edges, each classified once
  undirected edge kinds: {'tree': 5, 'back': 2}
  forward: 0, cross: 0  (both must be 0)

=== 6. BFS: every edge joins levels that differ by at most 1 ===
  levels from 'u': {'u': 0, 'v': 1, 'x': 1, 'y': 2, 'w': 3, 'z': 4}
  largest level difference across any edge: 1  (DFS has no such bound)

=== 7. The same graph, DFS started from 'w' instead ===
  totals now: {'tree': 4, 'back': 2, 'cross': 2}
  back-edge count unchanged: 2 -> 2
  forward/cross counts changed: 1/1 -> 0/2
```

### What each block is actually demonstrating

- **Block 3** is the parenthesis theorem checked exhaustively over all 30 ordered pairs. A single violation would mean the timestamps are not recording what we claim.
- **Block 5** is the undirected theorem. Note the guard `if undirected and (v, u) in edges`. Without it, each undirected edge is classified twice and the second pass invents forward edges that do not exist — an easy and convincing-looking bug.
- **Block 5** reports 5 tree edges for 6 vertices in one component. That is $V - 1$, which is the [[03-subgraphs-trees-and-forests|defining edge count of a spanning tree]] — the traversal tree really is a tree.

---

## 8. Which parts are facts about the graph, and which are accidents

Block 7 is the one to take seriously, because it separates two things students routinely conflate.

**The back-edge count did not change** when the search started somewhere else. It cannot: back edges correspond to cycles, cycles are a property of the graph, and the graph did not change. More precisely — *whether there is at least one back edge* is invariant, and that is the part algorithms rely on.

**The forward/cross split did change**, from one of each to two cross edges. Starting at `w` means `y` is discovered inside `w`'s subtree, so the later visit from `u` sees a finished vertex in a different branch — cross rather than forward. **Forward and cross are artefacts of where you started and what order you listed the neighbours in.** They tell you about *this traversal*, not about the graph.

This is why real algorithms are built on back edges and on finish times, and essentially never on forward or cross edges directly:

| Algorithm | What it actually uses |
| :--- | :--- |
| Cycle detection (directed) | "does any back edge exist" |
| [[01-topological-sort\|Topological sort]], DFS variant | vertices in **decreasing finish time** |
| Kosaraju's SCC algorithm | decreasing finish time, then DFS on the reversed graph |
| Tarjan's SCC algorithm | discovery times plus a lowest-reachable-discovery-time value |
| Bridges and articulation points | for each vertex, the lowest discovery time reachable via one back edge |
| Bipartite check | BFS levels, i.e. no edge within a level |

Notice the pattern: **discovery time, finish time, and back edges.** Learn those three and the rest of the graph-algorithm catalogue stops looking like a list of unrelated tricks.

---

## 9. Common pitfalls and traps

1. **Using a visited set where you need three colours.** A visited set cannot distinguish "on the current path" from "finished and left". On a directed graph this makes cycle detection report cycles that do not exist, exactly as in section 1. The symptom is a dependency resolver that rejects a perfectly valid build.
2. **Forgetting that the undirected parent edge looks like a back edge.** Every child sees its parent as grey. Skip the edge you arrived on — and skip it by edge identity, not by vertex, or you will also skip a genuine parallel edge, which really is a two-edge cycle.
3. **Assuming the four categories are graph properties.** Only "a back edge exists" survives changing the start vertex. If a solution's correctness depends on an edge being *forward* rather than *cross*, it is depending on adjacency-list ordering, and it will break.
4. **Reading timestamps as "visit order" and nothing more.** The value of $f[v]$ is not "the order I finished in" used as a label — it is a comparable number whose *relative* ordering encodes ancestry. Sorting by decreasing $f$ is a topological order; sorting by increasing $d$ is not.
5. **Doing the classification with BFS and expecting the same four kinds.** BFS on a directed graph does produce non-tree edges, but they do not correspond to ancestry in the same way, and there is no parenthesis theorem for BFS because there is no nesting. If a problem talks about back edges, it means DFS.
6. **Self-loops.** A self-loop is a back edge and a cycle of length one. Code that special-cases `u == v` by skipping it will silently declare cyclic graphs acyclic.

---

## 10. Check your understanding

Answer before opening each one.

1. **A DFS on a directed graph produces zero back edges but several cross edges. Is the graph a DAG?**
   <details><summary>Answer</summary>Yes. "DAG" is equivalent to "no back edges", full stop. Cross edges are perfectly compatible with acyclicity — they are just edges into a part of the graph the search has already finished with. The graph in section 1 (<code>A→B</code>, <code>A→C</code>, <code>B→D</code>, <code>C→D</code>) is a DAG with a cross edge.</details>

2. **You are told $d[a] = 3$, $f[a] = 14$, $d[b] = 7$, $f[b] = 20$. What can you conclude?**
   <details><summary>Answer</summary>That the numbers are impossible. The intervals $[3,14]$ and $[7,20]$ partially overlap, which the parenthesis theorem forbids. Either the timestamps came from something that is not a depth-first search, or they were recorded wrongly.</details>

3. **Why does the DFS-based topological sort output vertices in decreasing finish time rather than increasing discovery time?**
   <details><summary>Answer</summary>Because for a tree, forward or cross edge $u \to v$ in a DAG, $v$ always finishes before $u$ — the search either descends into $v$ and returns before leaving $u$, or $v$ was already finished when the edge was examined. So $f[u] > f[v]$ for every edge, and sorting by decreasing $f$ puts every vertex before everything it points to. Discovery time gives no such guarantee: a cross edge $u \to v$ can have $d[v] < d[u]$, which would place $v$ first and violate the order.</details>

4. **In an undirected connected graph with $V$ vertices and $E$ edges, how many back edges will a DFS find?**
   <details><summary>Answer</summary>Exactly $E - (V - 1)$. The tree edges number $V-1$ because the DFS tree spans the component, undirected DFS produces only tree and back edges, and every edge is classified exactly once. In the lab: $7 - (6-1) = 2$, which is what block 5 reports. This quantity is the <b>cycle rank</b> or circuit rank of the graph.</details>

5. **A colleague's undirected cycle detector returns `True` for a graph that is a single edge `A—B`. What is the bug, in one sentence?**
   <details><summary>Answer</summary>It treats the parent edge as a back edge: on arriving at <code>B</code> from <code>A</code> it examines the edge back to <code>A</code>, sees <code>A</code> is grey, and concludes cycle — the fix is to skip the edge the search arrived on.</details>

---

## 11. Practice — independent task

Implement `analyse(graph, directed=True)` that returns a report about a graph using only one DFS pass.

**Inputs:** an adjacency-list `dict` mapping vertex → list of neighbours, and a `directed` flag.

**Return** a dict with:

- `"times"` — vertex → `(discovery, finish)`
- `"edges"` — `(u, v)` → classification
- `"acyclic"` — bool
- `"cycle"` — an actual list of vertices forming one cycle, or `None`. Recover it from the parent map plus the back edge, not by searching again.
- `"topo_order"` — a valid topological order if acyclic, else `None`
- `"components"` — for the undirected case, the number of connected components

**Edge cases you must handle:** the empty graph; a single vertex with no edges; a self-loop; a vertex with no outgoing edges; a disconnected graph needing a forest; parallel edges in the undirected case.

**Checks to write:**

1. Assert every edge appears in `"edges"` exactly once, and that the four counts sum to $|E|$.
2. Assert that `"acyclic"` agrees with an independent brute-force check — for small graphs, try every permutation of vertices and see whether any is a valid topological order.
3. Assert that when `"cycle"` is not `None`, every consecutive pair really is an edge and the last vertex points back to the first.
4. For the undirected case, assert `back_edges == E - V + components`.

**Done when:** all four checks pass on at least five graphs including a DAG, a graph with one cycle, a self-loop-only graph, a disconnected forest, and the running example from this lesson — and you can state, without rerunning, which of your reported numbers would change if you shuffled the adjacency lists.

Then take it to a real problem: [[087-course-schedule|Course Schedule]] and [[088-course-schedule-ii|Course Schedule II]] are this lesson with the vocabulary removed.

---

## Before moving on

You can compute discovery and finish times by hand, classify any edge from them, prove in both directions that back edges and directed cycles are the same thing, and say which parts of the classification are properties of the graph rather than of your traversal.

**Recap:** a traversal builds a tree out of first-visit edges and sorts the rest into back, forward and cross; the colour of the target when the edge is examined decides which; intervals nest or are disjoint, never overlap, and nesting is ancestry; a back edge exists if and only if there is a directed cycle, which is why DFS topological sort detects cycles for free; undirected DFS has only tree and back edges; BFS edges span at most one level, which is the shortest-path and bipartite property.

**Next:** [[01-topological-sort|Topological Sort]] — the first algorithm that is nothing but a rule about finish times, and the direct application of everything above.

---

## Related

- [[01-depth-first-search|Depth-First Search]] — the traversal whose tree this lesson dissects
- [[02-breadth-first-search|Breadth-First Search]] — the other tree, and the level property
- [[02-paths-cycles-and-connectivity|Paths, Cycles and Connectivity]] — where cycle, DAG and component are defined
- [[03-subgraphs-trees-and-forests|Subgraphs, Trees and Forests]] — why a traversal tree has $V-1$ edges
- [[01-topological-sort|Topological Sort]] — decreasing finish time, and cycle detection for free
- [[10-union-find|Union-Find]] — the other way to find undirected cycles, incrementally
- [[05-traversal/index|the traversal folder]]

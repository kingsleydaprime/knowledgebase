# Module: Connected Components (How Many Separate Groups Are There?)

**[Intermediate]** — The simplest question you can ask about a graph, and the one asked most often in practice: **given these things and the connections between them, how many separate clusters are there, and who is in each?**

Teams and the meetings between them. Users and their friendships. Servers and their network links. Pixels and their neighbours. It is the same question every time, it has three standard answers, and **choosing between them is decided by one thing: whether the edges are all known up front.**

---

## Before you start

- You can implement [[01-depth-first-search|DFS]] and [[02-breadth-first-search|BFS]], and know why a graph traversal needs a visited set.
- You know what a **connected component** is — [[02-paths-cycles-and-connectivity|paths, cycles and connectivity]] defines it, along with strong versus weak connectivity.
- You have met [[10-union-find|union-find]], or are willing to meet it here.

**After this lesson you will be able to:**

1. Count components and list their members with **DFS, BFS or union-find**, and say which to use when.
2. Use the counting identity **components = V − (edges that merged something)**.
3. Explain why an isolated vertex is a component, and why forgetting it is the standard off-by-N.
4. Say what changes when the edges are **directed**, and pick weak or strong connectivity deliberately.

**Study route:** read 1–3, answer the prediction in section 4, then run the lab. Section 5 is the one that decides your implementation in a real system.

---

## 1. The question, concretely

Seven teams. Three meetings happened:

```
   platform --- payments --- fraud        design --- brand

   legal        research        (attended nothing)
```

**How many separate clusters?**

The lab answers it three independent ways and they agree:

```
   DFS        : 4 clusters
      ['brand', 'design']
      ['fraud', 'payments', 'platform']
      ['legal']
      ['research']
```

**Four, not two.** `legal` and `research` attended no meetings, and each is a connected component of one.

**That is the most common mistake in this problem**, and it is a mistake of definition rather than of code: a component is a *maximal set of mutually reachable vertices*, and a lone vertex satisfies that trivially. If your answer is driven by iterating over **edges**, isolated vertices are invisible and you will undercount. Iterate over **vertices**.

---

## Terms used here

1. **Connected component**: This is a maximal set of vertices that can all reach one another. "Maximal" means you cannot add any other vertex without breaking the property. **Every vertex is in exactly one component**, so the components partition the graph — nothing left over, nothing counted twice.
2. **Isolated vertex**: This is a vertex with no edges. It forms a component by itself.
3. **Flood fill**: This is the technique of starting at one vertex and traversing everything reachable from it, marking as you go. One flood fill discovers exactly one component, so the number of times you must start a fresh one *is* the component count.
4. **Union-find**: This is also known as **disjoint-set union (DSU)**. This is a structure maintaining a partition under two operations: `find` (which group is this in?) and `union` (merge these two groups). See [[10-union-find|union-find]].
5. **Redundant edge**: This is an edge whose endpoints are already in the same component. It merges nothing and leaves the count unchanged. **In a graph built only from merging edges, a redundant edge is exactly a cycle.**
6. **Weakly connected**: This describes components of a *directed* graph computed by ignoring edge direction.
7. **Strongly connected**: This describes a set of vertices in a directed graph that can all reach each other **respecting direction**. An **SCC (strongly connected component)** is a maximal such set.
8. **Incremental / dynamic connectivity**: This is the setting where edges arrive over time and you must answer after each one. It is the case that decides between traversal and union-find.

---

## 2. Method one and two: flood fill with DFS or BFS

**The algorithm is one sentence: loop over every vertex; if it is unvisited, start a traversal from it and mark everything reachable — that is one component.**

```python
def components(graph):
    seen, comps = set(), []
    for start in graph:            # over VERTICES, not edges
        if start in seen:
            continue
        stack, group = [start], []
        seen.add(start)
        while stack:
            u = stack.pop()
            group.append(u)
            for v in graph[u]:
                if v not in seen:
                    seen.add(v)
                    stack.append(v)
        comps.append(group)
    return comps
```

**Swap the stack for a queue and it is BFS** — and the component list is identical, because *which* vertices are reachable does not depend on the order you visit them. The lab confirms DFS and BFS agree on every input.

**Cost:** $O(V + E)$. Every vertex is pushed once and every edge examined twice (once from each end). **You cannot do better** — you have to look at the whole graph to know it is all connected.

**Choose BFS over DFS when** you also want the *distance* between two members — BFS gives the fewest-meetings-apart path for free. Choose DFS when the graph is deep and you want $O(\text{depth})$ memory instead of $O(\text{width})$ — but note [[01-depth-first-search|recursive DFS dies at about 1,000 frames]], so use the explicit-stack form above on anything large.

---

## 3. Method three: union-find, and the counting identity

Union-find answers the same question without traversing anything.

**Start by assuming nothing is connected: $V$ components, everyone alone. Then process the edges. Each edge either joins two different groups — count drops by one — or joins two vertices already together, and changes nothing.**

The lab traces it:

```
   start: 7 components
      platform -- payments  merged                       -> 6 components
      payments -- fraud     merged                       -> 5 components
        design -- brand     merged                       -> 4 components
      payments -- platform  redundant (already together) -> 4 components
```

Giving the identity worth remembering:

$$\text{components} = V - (\text{number of edges that actually merged two groups})$$

$7 - 3 = 4$. ✓

**Two things fall out of the same counter at no extra cost:**

1. **Cycle detection.** A redundant edge in an undirected graph means its endpoints were already connected, so adding it closes a cycle. `union` returning `False` *is* "this edge creates a cycle" — which is exactly how [[06-minimum-spanning-tree|Kruskal's algorithm]] avoids them.
2. **"Is this a tree?"** A graph is a tree iff it is connected and has $V-1$ edges — that is, the count reaches 1 and every edge merged.

**Cost:** with path compression and union by rank, effectively $O(\alpha(V))$ per operation — [[02-amortized-analysis|an amortised result that needs a potential argument to prove]], and below 5 for any $V$ that will ever exist.

---

## 4. Which method, and why it is not a matter of taste

> **Predict before reading on.** 2,000 teams. Meetings arrive one at a time, and after each one you must report the current number of clusters. **Is re-running DFS after each meeting acceptable, and roughly how much slower is it than union-find?**

The lab measures it over 600 arriving edges:

```
     union-find (incremental) : 0.0026s
     DFS re-run each time     : 1.2407s
     same answers throughout  : True
     ratio                    : 486x
```

**Around 500×, and the gap grows with both $V$ and the number of edges**, because re-running DFS is $O(V+E)$ *per edge* — $O(E(V+E))$ overall — while union-find pays $O(\alpha(V))$ per edge and never recomputes anything.

**This is the decision, and it is structural rather than aesthetic:**

| Situation | Use | Why |
| :--- | :--- | :--- |
| All edges known, one answer needed | **DFS or BFS** | $O(V+E)$, simplest code, gives you the members directly |
| Edges **arrive over time** | **union-find** | incremental; no recomputation |
| Need the path between two vertices | **BFS** | fewest edges apart, for free |
| On a grid | **DFS/BFS flood fill** | neighbours are computed, not stored |
| Edges are also **removed** | **neither** | see below |

**The last row is the real limitation.** Union-find cannot un-merge — there is no `split` operation, because path compression has destroyed the information about *which* edge joined what. If edges can disappear, you are in **dynamic connectivity**, which needs considerably heavier machinery (link-cut trees, or Euler tour trees) or a rebuild from scratch.

---

## 5. Directed edges: two different answers to "connected"

If meetings are directed — *A invited B* rather than *A and B met* — then "connected" splits into two genuinely different questions.

The lab runs both on `a→b, b→c, c→a, c→d, d→e, e→d`:

```
   weakly connected components  (ignore direction): 1
      ['a', 'b', 'c', 'd', 'e']

   strongly connected components (mutual reachability): 2
      ['a', 'b', 'c']
      ['d', 'e']
```

**Ignoring direction, it is one blob. Respecting direction, `d` and `e` can be reached from `a`, `b`, `c` but cannot get back** — so they form a separate SCC.

**Which one you want is a modelling question, not an algorithmic one.** "Which teams share information at all?" is weak connectivity. "Which teams can all reach each other?" is strong. Asking for "the connected components" of a directed graph without saying which is ambiguous, and it is a reasonable thing to ask an interviewer to clarify.

**Weak components** are just the undirected algorithm on the underlying undirected graph. **SCCs** need [[03-traversal-trees-and-edge-classification|finish times]]: Kosaraju's algorithm runs a DFS to order vertices by decreasing finish time, then a second DFS on the *reversed* graph, and each tree of that second forest is one SCC. Both are $O(V+E)$.

---

## 6. Worked example — complete runnable lab

Save as `connected_components.py`. Standard library only. All three methods are cross-checked against each other on 400 random graphs.

```python
"""Counting clusters: teams as vertices, meetings as edges.

Three ways to answer 'how many separate groups are there, and who is in each',
all cross-checked against one another.

Run:  python3 connected_components.py
"""

import random
import time
from collections import deque

# Teams, and the meetings that happened between them.
TEAMS = ["platform", "payments", "fraud", "design", "brand", "legal", "research"]
MEETINGS = [
    ("platform", "payments"),
    ("payments", "fraud"),
    ("design", "brand"),
]
# legal and research attended no meetings at all.


def build(vertices, edges):
    g = {v: set() for v in vertices}
    for a, b in edges:
        g[a].add(b)
        g[b].add(a)
    return g


# ------------------------------------------------------------ 1. DFS flood fill
def components_dfs(graph):
    seen, comps = set(), []
    for start in graph:
        if start in seen:
            continue
        stack, group = [start], []
        seen.add(start)
        while stack:
            u = stack.pop()
            group.append(u)
            for v in graph[u]:
                if v not in seen:
                    seen.add(v)
                    stack.append(v)
        comps.append(sorted(group))
    return sorted(comps)


# ------------------------------------------------------------ 2. BFS flood fill
def components_bfs(graph):
    seen, comps = set(), []
    for start in graph:
        if start in seen:
            continue
        q, group = deque([start]), []
        seen.add(start)
        while q:
            u = q.popleft()
            group.append(u)
            for v in graph[u]:
                if v not in seen:
                    seen.add(v)
                    q.append(v)
        comps.append(sorted(group))
    return sorted(comps)


# --------------------------------------------------------------- 3. union-find
class UnionFind:
    def __init__(self, items):
        self.parent = {x: x for x in items}
        self.rank = {x: 0 for x in items}
        self.count = len(items)          # every vertex starts as its own component

    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]   # path compression
            x = self.parent[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False                 # already together: this edge is redundant
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
        self.count -= 1                  # two groups became one
        return True


def components_union_find(vertices, edges):
    uf = UnionFind(vertices)
    for a, b in edges:
        uf.union(a, b)
    groups = {}
    for v in vertices:
        groups.setdefault(uf.find(v), []).append(v)
    return sorted(sorted(g) for g in groups.values()), uf.count


# ------------------------------------------------- directed: weak vs strong
def weakly_connected(vertices, directed_edges):
    return components_dfs(build(vertices, directed_edges))


def strongly_connected(vertices, directed_edges):
    """Kosaraju: DFS by finish time, then DFS on the reversed graph."""
    adj = {v: [] for v in vertices}
    rev = {v: [] for v in vertices}
    for a, b in directed_edges:
        adj[a].append(b)
        rev[b].append(a)

    seen, order = set(), []

    def visit(u):
        stack = [(u, iter(adj[u]))]
        seen.add(u)
        while stack:
            node, it = stack[-1]
            advanced = False
            for v in it:
                if v not in seen:
                    seen.add(v)
                    stack.append((v, iter(adj[v])))
                    advanced = True
                    break
            if not advanced:
                order.append(stack.pop()[0])

    for v in vertices:
        if v not in seen:
            visit(v)

    seen2, comps = set(), []
    for v in reversed(order):
        if v in seen2:
            continue
        stack, group = [v], []
        seen2.add(v)
        while stack:
            u = stack.pop()
            group.append(u)
            for w in rev[u]:
                if w not in seen2:
                    seen2.add(w)
                    stack.append(w)
        comps.append(sorted(group))
    return sorted(comps)


def main():
    graph = build(TEAMS, MEETINGS)

    print("=" * 76)
    print("1. THE QUESTION: which teams are connected, and how many clusters?")
    print("=" * 76)
    print(f"\n   teams    : {TEAMS}")
    print(f"   meetings : {MEETINGS}")
    print("\n   platform --- payments --- fraud        design --- brand")
    print("\n   legal        research        (attended nothing)")

    dfs = components_dfs(graph)
    bfs = components_bfs(graph)
    uf, uf_count = components_union_find(TEAMS, MEETINGS)

    print(f"\n   DFS        : {len(dfs)} clusters")
    for g in dfs:
        print(f"      {g}")
    print(f"\n   all three methods agree: {dfs == bfs == uf}")
    print(f"   union-find's running counter: {uf_count}")

    print("\n   -> note legal and research are each a cluster of ONE. A vertex with")
    print("      no edges is still a connected component, and forgetting that is")
    print("      the most common off-by-N in this problem.")

    print("\n" + "=" * 76)
    print("2. THE COUNTING SHORTCUT")
    print("=" * 76)
    print("\n   Start with V components -- everyone alone. Every edge that joins two")
    print("   DIFFERENT groups reduces the count by one. Edges inside a group change")
    print("   nothing.")
    uf2 = UnionFind(TEAMS)
    count = len(TEAMS)
    print(f"\n   start: {count} components")
    for a, b in MEETINGS:
        merged = uf2.union(a, b)
        count = uf2.count
        note = "merged" if merged else "redundant (already together)"
        print(f"     {a:>9} -- {b:<9} {note:<28} -> {count} components")
    extra = ("payments", "platform")
    merged = uf2.union(*extra)
    print(f"     {extra[0]:>9} -- {extra[1]:<9} "
          f"{'redundant (already together)' if not merged else 'merged':<28} -> {uf2.count} components")
    print("\n   -> components = V - (number of edges that actually merged something)")
    print(f"      {len(TEAMS)} teams - 3 merging meetings = {len(TEAMS) - 3} clusters")

    print("\n" + "=" * 76)
    print("3. WHICH METHOD TO USE")
    print("=" * 76)
    print("""
   all edges known up front, one answer   -> DFS or BFS, O(V+E), simplest
   edges ARRIVE over time                 -> union-find, O(alpha(V)) per edge
   need the actual path between two teams -> BFS (fewest meetings apart)
   need it on a grid                      -> DFS/BFS flood fill
   edges also get REMOVED                 -> neither; union-find cannot un-merge""")

    print("\n   The incremental case, measured -- 2,000 teams, edges arriving one")
    print("   at a time, recounting after each:")
    n = 2000
    random.seed(1)
    verts = list(range(n))
    arriving = [(random.randrange(n), random.randrange(n)) for _ in range(600)]

    t0 = time.perf_counter()
    uf3 = UnionFind(verts)
    uf_counts = []
    for a, b in arriving:
        uf3.union(a, b)
        uf_counts.append(uf3.count)
    t_uf = time.perf_counter() - t0

    t0 = time.perf_counter()
    dfs_counts, sofar = [], []
    for a, b in arriving:
        sofar.append((a, b))
        dfs_counts.append(len(components_dfs(build(verts, sofar))))
    t_dfs = time.perf_counter() - t0

    print(f"     union-find (incremental) : {t_uf:.4f}s")
    print(f"     DFS re-run each time     : {t_dfs:.4f}s")
    print(f"     same answers throughout  : {uf_counts == dfs_counts}")
    print(f"     ratio                    : {t_dfs / t_uf:.0f}x")
    print("   -> (timings vary by machine; the AGREEMENT is the part that reproduces)")

    print("\n" + "=" * 76)
    print("4. DIRECTED MEETINGS: 'attended' is not always mutual")
    print("=" * 76)
    directed = [("a", "b"), ("b", "c"), ("c", "a"), ("c", "d"), ("d", "e"), ("e", "d")]
    verts2 = ["a", "b", "c", "d", "e"]
    print(f"\n   directed edges: {directed}")
    weak = weakly_connected(verts2, directed)
    strong = strongly_connected(verts2, directed)
    print(f"\n   weakly connected components  (ignore direction): {len(weak)}")
    for g in weak:
        print(f"      {g}")
    print(f"\n   strongly connected components (mutual reachability): {len(strong)}")
    for g in strong:
        print(f"      {g}")
    print("\n   -> ignoring direction, everything is one blob. Respecting it, you")
    print("      cannot get back from d/e to a/b/c, so they are separate SCCs.")
    print("   -> 'are these teams connected?' has two different answers, and which")
    print("      one you want depends on whether the relation is symmetric.")

    print("\n" + "=" * 76)
    print("5. CROSS-CHECK ON RANDOM GRAPHS")
    print("=" * 76)
    bad = 0
    for t in range(400):
        random.seed(t + 31)
        k = random.randint(1, 12)
        vs = list(range(k))
        es = [(random.randrange(k), random.randrange(k))
              for _ in range(random.randint(0, 15))]
        a = components_dfs(build(vs, es))
        b = components_bfs(build(vs, es))
        c, cnt = components_union_find(vs, es)
        if not (a == b == c and len(a) == cnt):
            bad += 1
    print(f"\n   DFS, BFS and union-find agreed on {400 - bad}/400 random graphs,")
    print("   including the component COUNT from union-find's running counter.")


if __name__ == "__main__":
    main()
```

### Expected output

Generated by running the file above. The timing lines in block 3 are machine-dependent; every other number reproduces, and the lab says so itself:

```
============================================================================
1. THE QUESTION: which teams are connected, and how many clusters?
============================================================================

   teams    : ['platform', 'payments', 'fraud', 'design', 'brand', 'legal', 'research']
   meetings : [('platform', 'payments'), ('payments', 'fraud'), ('design', 'brand')]

   platform --- payments --- fraud        design --- brand

   legal        research        (attended nothing)

   DFS        : 4 clusters
      ['brand', 'design']
      ['fraud', 'payments', 'platform']
      ['legal']
      ['research']

   all three methods agree: True
   union-find's running counter: 4

   -> note legal and research are each a cluster of ONE. A vertex with
      no edges is still a connected component, and forgetting that is
      the most common off-by-N in this problem.

============================================================================
2. THE COUNTING SHORTCUT
============================================================================

   Start with V components -- everyone alone. Every edge that joins two
   DIFFERENT groups reduces the count by one. Edges inside a group change
   nothing.

   start: 7 components
      platform -- payments  merged                       -> 6 components
      payments -- fraud     merged                       -> 5 components
        design -- brand     merged                       -> 4 components
      payments -- platform  redundant (already together) -> 4 components

   -> components = V - (number of edges that actually merged something)
      7 teams - 3 merging meetings = 4 clusters

============================================================================
3. WHICH METHOD TO USE
============================================================================

   all edges known up front, one answer   -> DFS or BFS, O(V+E), simplest
   edges ARRIVE over time                 -> union-find, O(alpha(V)) per edge
   need the actual path between two teams -> BFS (fewest meetings apart)
   need it on a grid                      -> DFS/BFS flood fill
   edges also get REMOVED                 -> neither; union-find cannot un-merge

   The incremental case, measured -- 2,000 teams, edges arriving one
   at a time, recounting after each:
     union-find (incremental) : 0.0026s
     DFS re-run each time     : 1.2407s
     same answers throughout  : True
     ratio                    : 486x
   -> (timings vary by machine; the AGREEMENT is the part that reproduces)

============================================================================
4. DIRECTED MEETINGS: 'attended' is not always mutual
============================================================================

   directed edges: [('a', 'b'), ('b', 'c'), ('c', 'a'), ('c', 'd'), ('d', 'e'), ('e', 'd')]

   weakly connected components  (ignore direction): 1
      ['a', 'b', 'c', 'd', 'e']

   strongly connected components (mutual reachability): 2
      ['a', 'b', 'c']
      ['d', 'e']

   -> ignoring direction, everything is one blob. Respecting it, you
      cannot get back from d/e to a/b/c, so they are separate SCCs.
   -> 'are these teams connected?' has two different answers, and which
      one you want depends on whether the relation is symmetric.

============================================================================
5. CROSS-CHECK ON RANDOM GRAPHS
============================================================================

   DFS, BFS and union-find agreed on 400/400 random graphs,
   including the component COUNT from union-find's running counter.
```

---

## 7. Common pitfalls and traps

1. **Iterating over edges instead of vertices.** Isolated vertices have no edges, so they never appear, and you undercount. The lab's `legal` and `research` exist only because the loop runs over vertices.
2. **Forgetting that a lone vertex is a component.** Same bug, stated as a definition error. Seven teams and three meetings give **four** clusters, not two.
3. **Recursive DFS on a large graph.** [[01-depth-first-search|About 1,000 frames in CPython]]; a 5,000-vertex chain is one component and one `RecursionError`. Use the explicit stack.
4. **Re-running a traversal per edge in an incremental setting.** Measured at ~500× slower than union-find, and it degrades further as the graph grows.
5. **Expecting union-find to handle deletions.** There is no un-merge. Edge removal is dynamic connectivity, which is a different and much harder problem.
6. **Using union-find when you need the actual members and never get another edge.** It works, but you must group by root afterwards; a single DFS hands you the groups directly and is simpler.
7. **Saying "connected components" of a directed graph without qualifying it.** Weak and strong give different answers — 1 versus 2 in the lab. Decide which the problem means.
8. **Counting a redundant edge as a merge.** `union` must report whether it actually merged; incrementing blindly breaks both the count and the cycle detection built on it.

---

## 8. Check your understanding

1. **Seven vertices, three edges, no vertex appearing twice across them. How many components?**
   <details><summary>Answer</summary>Four. Three edges each merge a distinct pair, using six vertices and leaving one alone: $7 - 3 = 4$ by the identity components = $V$ − merging edges. Equivalently, three pairs plus one isolated vertex.</details>

2. **Why do DFS and BFS always produce the same components?**
   <details><summary>Answer</summary>Because a component is defined by <i>reachability</i>, which does not depend on visit order. Both traversals explore everything reachable from their start vertex and nothing else — they differ only in the order, which changes the traversal tree but not its vertex set. The lab asserts this on 400 random graphs.</details>

3. **When does union-find beat a traversal, and when is it the wrong choice?**
   <details><summary>Answer</summary><b>Beats:</b> when edges arrive over time and you must answer repeatedly — ~500× in the lab, because a traversal recomputes from scratch each time while union-find pays $O(\alpha(V))$ per edge. <b>Wrong:</b> when all edges are known up front and you want the members, where one DFS is simpler and gives the groups directly; and when edges can be <i>removed</i>, which union-find cannot support at all.</details>

4. **What does it mean when `union(a, b)` finds them already in the same set?**
   <details><summary>Answer</summary>That a path between <code>a</code> and <code>b</code> already exists, so this edge closes a <b>cycle</b> and merges nothing. The component count is unchanged. This is how [[06-minimum-spanning-tree|Kruskal's algorithm]] rejects edges that would create a cycle, and how you detect cycles in an undirected graph incrementally.</details>

5. **A directed graph's weak components number 1 and its SCCs number 5. What does that tell you?**
   <details><summary>Answer</summary>That everything is joined when you ignore direction, but respecting direction the graph splits into five mutually-reachable groups — so there are one-way connections between them. Condensing each SCC to a single vertex always yields a DAG, so those five groups have a topological order: information flows one way between them and cannot return.</details>

---

## 9. Practice — independent task

**Part 1 — three implementations.** `components(vertices, edges)` returning the groups, via DFS, BFS and union-find. Assert all three agree on 500 random graphs **including graphs with isolated vertices, self-loops and parallel edges** — each of which breaks a naive implementation differently.

**Part 2 — the identity.** Instrument union-find to count merging versus redundant edges. Verify `components == V - merges` on every test graph, and confirm that the redundant count equals the number of independent cycles ($E - V + \text{components}$, the cycle rank).

**Part 3 — the incremental measurement.** Reproduce the lab's comparison at $V \in \{100, 1000, 10000\}$. Plot or tabulate the ratio and state how it scales. **Predict the trend before measuring.**

**Part 4 — on a grid.** "Number of islands": count connected regions of `1`s in a grid of `0`/`1`, 4-connected. Do it by flood fill **and** by union-find over cell indices. Then the follow-up that decides the method: **islands are added one at a time and you must report the count after each** — say which implementation you would ship and why.

**Part 5 — directed.** Implement weakly connected components and Kosaraju's SCC. On 300 random directed graphs assert `#SCC >= #weak`, and that condensing the SCCs yields a graph with no directed cycle. **Explain in one sentence why that inequality must hold.**

**Part 6 — the limitation.** Attempt to support edge *removal* with union-find. Document precisely where it breaks, then implement the naive alternative (rebuild and re-traverse) and measure what it costs.

**Edge cases:** the empty graph; one vertex, no edges; every vertex isolated; a complete graph; a self-loop; parallel edges; a graph that is already one component.

**Done when:** part 1 agrees on all 500 graphs including the awkward ones; part 2's identity holds everywhere; part 3's trend matches your prediction; part 4 has a defended choice; part 5's assertions pass with the inequality explained; and part 6 documents the break point with a measurement.

Then find it worked: [[090-number-of-connected-components|Number of Connected Components]], [[080-number-of-islands|Number of Islands]], [[091-graph-valid-tree|Graph Valid Tree]], [[089-redundant-connection|Redundant Connection]].

---

## Before moving on

You can count components and list their members three ways, use the counting identity, explain why an isolated vertex counts, and choose weak or strong connectivity for a directed graph.

**Recap:** a connected component is a maximal mutually-reachable set, and the components **partition** the vertices — so **iterate over vertices, not edges**, or isolated vertices vanish and you undercount (seven teams, three meetings, **four** clusters). **Flood fill** with DFS or BFS is $O(V+E)$, gives the members directly, and both orders produce identical components because reachability does not depend on visit order. **Union-find** starts at $V$ components and decrements on every merging edge, giving **components = V − merges**; a non-merging edge is exactly a cycle, which is how Kruskal's rejects them. **The choice is structural:** all edges known up front → traversal; edges arriving over time → union-find, measured ~500× faster; edges being **removed** → neither, that is dynamic connectivity. For directed graphs, **weak** ignores direction and **strong** requires mutual reachability — 1 component versus 2 on the lab's graph — and SCCs need finish times, via Kosaraju's two passes.

**Next:** [[01-topological-sort|Topological Sort]] — the next-simplest thing you can compute from a traversal, and the first that needs the graph to be acyclic.

---

## Related

- [[02-paths-cycles-and-connectivity|Paths, Cycles and Connectivity]] — where component, weak and strong are defined
- [[01-depth-first-search|DFS]] · [[02-breadth-first-search|BFS]] — the two traversals this is the first application of
- [[10-union-find|Union-Find]] — the structure, its complexity, and path compression
- [[06-minimum-spanning-tree|Minimum Spanning Tree]] — Kruskal's, which is this cycle check plus a sort
- [[02-amortized-analysis|Amortised Analysis]] — why union-find is $O(\alpha(V))$ and why only a potential argument proves it
- [[03-traversal-trees-and-edge-classification|Traversal Trees and Edge Classification]] — the finish times SCCs are built on
- [[06-algorithms/index|the graph algorithms index]]

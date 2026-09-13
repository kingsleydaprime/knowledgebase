# Module: Floyd–Warshall (Every Shortest Path, in Three Lines)

**[Advanced]** — [[02-dijkstra|Dijkstra]] and [[03-bellman-ford|Bellman–Ford]] answer "shortest path **from this source**". Floyd–Warshall answers "shortest path **between every pair**", in $O(V^3)$, with a triple loop short enough to write from memory. It is also the cleanest dynamic program in this course — the state, the transition and the base case are all visible in five lines — which makes it worth studying even when you would not deploy it.

---

## Before you start

- You can run [[02-dijkstra|Dijkstra]] and [[03-bellman-ford|Bellman–Ford]], and say which assumption each one needs.
- You know what an [[04-representations|adjacency matrix]] is and why it costs $O(V^2)$ space.
- You have seen the idea of solving a problem by **building up over a growing set of allowed choices** — this is a [[15-dynamic-programming|dynamic programming]] lesson wearing a graph costume.

**After this lesson you will be able to:**

1. State the **subproblem** Floyd–Warshall solves, and say exactly what $d[i][j]$ means after round $k$.
2. Explain why the $k$ loop **must** be outermost, and demonstrate the wrong order producing wrong answers.
3. Detect negative cycles by reading the **diagonal**, and reconstruct any path from a `next` matrix.
4. Choose between Floyd–Warshall and $V$ runs of Dijkstra from the graph's density.

**Study route:** read 1–4, answer the prediction in section 5 before continuing, then run the lab — block 6 is the one that settles the loop-order argument with evidence rather than assertion.

---

## 1. Why this exists: the all-pairs question

Some questions are not about one source:

1. **"What is the diameter of this network?"** — the largest shortest-path distance between any two nodes. You need all pairs to know the largest.
2. **"Precompute a routing table."** A router that answers queries in $O(1)$ needs the answers already computed, for every destination.
3. **"Which pairs are connected at all?"** — transitive closure, which turns out to be the same algorithm with two operators swapped.
4. **"Is there an arbitrage cycle?"** — detectable from the diagonal in one pass.

The obvious approach is to run a single-source algorithm $V$ times. That works, and for sparse graphs it is the right answer. **Floyd–Warshall takes a completely different route — and the route is the interesting part, because it never thinks about paths at all. It thinks about which vertices a path is *allowed to pass through*.**

---

## Terms used in all-pairs shortest paths

1. **All-pairs shortest path**: This is the problem of computing the shortest distance between **every** ordered pair of vertices, producing a $V \times V$ table rather than a single array.
2. **Intermediate vertex**: This is a vertex that a path passes *through* — neither its start nor its end. In the path $A \to B \to C \to D$, the intermediates are $B$ and $C$. **This is the concept the entire algorithm is organised around.**
3. **The distance matrix**: This is written $d[i][j]$. This is the table being filled in: the best known cost from $i$ to $j$. It starts as the adjacency matrix — direct edges only — and ends as the true shortest distances.
4. **The `next` matrix**: This is also called the **successor matrix**. This is `next[i][j]`, the first vertex to move to when travelling from $i$ towards $j$ along the best route. It is how you recover an actual path from a table of costs.
5. **Round $k$**: This is one pass of the outer loop, during which vertex $k$ becomes newly permitted as an intermediate. After round $k$, $d[i][j]$ holds the shortest path from $i$ to $j$ **that uses only the first $k$ vertices as intermediates**.
6. **Transitive closure**: This is the table of which vertices are reachable from which, ignoring cost. Computing it is Floyd–Warshall with $\min$ replaced by `or` and $+$ replaced by `and`, and that variant is called **Warshall's algorithm**.
7. **Dense graph**: This is a graph where $E$ is close to $V^2$ — most possible edges exist. **Sparse** means $E$ is closer to $V$. Which of the two you have decides whether Floyd–Warshall is the right tool.

---

## 2. The idea: permit one more intermediate at a time

Here is the reframing that makes the algorithm obvious.

**Do not ask "what is the shortest path from $i$ to $j$?". Ask "what is the shortest path from $i$ to $j$ that is only allowed to pass through vertices from some permitted set?"**

Start with the permitted set **empty**. Then the only routes available are direct edges, so the answer is just the adjacency matrix. That is the base case, and it is free.

Now permit one more vertex, $k$. For any pair $(i, j)$, the best route either:

- **does not use $k$** — in which case the answer is unchanged from before, or
- **does use $k$** — in which case it goes from $i$ to $k$, then from $k$ to $j$, and **both of those halves are already solved**, because they only use the previously permitted vertices as intermediates.

So:

$$d_k[i][j] = \min\bigl(d_{k-1}[i][j],\; d_{k-1}[i][k] + d_{k-1}[k][j]\bigr)$$

**In words: the shortest path allowed to use the first $k$ vertices is either the one that ignores $k$ entirely, or the best route into $k$ followed by the best route out of it.** Repeat until every vertex is permitted, and the constraint has disappeared — which means the answer is unconstrained, which means it is the shortest path.

That is the whole algorithm:

```python
for k in vertices:
    for i in vertices:
        for j in vertices:
            if d[i][k] + d[k][j] < d[i][j]:
                d[i][j] = d[i][k] + d[k][j]
                nxt[i][j] = nxt[i][k]
```

**Why a path can use each intermediate at most once** — and therefore why considering each $k$ exactly once is enough — is that revisiting a vertex means the path contains a cycle, and (absent negative cycles) removing that cycle never makes the path longer. So there is always a shortest path that is simple, and a simple path uses each vertex at most once as an intermediate.

---

## 3. Watching it happen

The lab traces a four-vertex graph round by round. With no intermediates permitted, the matrix is just the edges:

```
  initial (no intermediates allowed)
            A     B     C     D
    A       0     3   inf     7
    B       8     0     2   inf
    C       5   inf     0     1
    D       2   inf   inf     0
```

`A → C` is infinite because there is no direct edge. After permitting `B`, the route $A \to B \to C$ appears at cost $3 + 2 = 5$. After permitting `C`, $A \to C \to D$ gives $5 + 1 = 6$, beating the direct edge of weight 7. The final table:

```
            A     B     C     D
    A       0     3     5     6
    B       5     0     2     3
    C       3     6     0     1
    D       2     5     7     0
```

**Read `B → A` in the final table: 5.** The direct edge $B \to A$ has weight 8. The algorithm found $B \to C \to D \to A = 2 + 1 + 2 = 5$, a three-edge path, **without ever enumerating a path.** It composed it from two halves, each of which was itself composed from halves.

The lab cross-checks all 16 pairs against Bellman–Ford run from each source, and they agree.

### Recovering the path

The costs alone do not tell you the route. The `next` matrix does, and the update is one extra line: when you improve $d[i][j]$ by going through $k$, the *first step* from $i$ is whatever the first step towards $k$ was — `nxt[i][j] = nxt[i][k]`.

To walk the path, keep stepping: `i = nxt[i][j]` until `i == j`. The lab prints all twelve routes, including `B -> C -> D -> A`.

---

## 4. The loop order is the algorithm

> **Predict before reading on.** The triple loop has $k$ outermost, then $i$, then $j$. Suppose you swap it so $i$ is outermost and $k$ is innermost — the same comparisons, the same number of iterations, just reordered. Does it still work?

**No, and this is the single most important thing in the lesson.**

The correctness argument in section 2 has one requirement: **when you consider routing through $k$, the values $d[i][k]$ and $d[k][j]$ must already be final with respect to all previously permitted intermediates.** The outer $k$ loop is what guarantees that — round $k$ begins only after round $k-1$ has completely finished for every pair.

Put $k$ on the inside and you destroy it. You will use $d[i][k]$ before $d[i][k]$ has itself been improved, and the result is an **overestimate** — a real path, but not the shortest one.

The lab demonstrates it twice. On the four-vertex graph:

```
    differing cells (i, j, correct, wrong): [('B', 'A', 5, 7)]
```

The wrong order reports $B \to A = 7$ instead of 5, because when it computed $B \to A$ it had not yet learned that $C \to A$ could be improved to 3 via $D$.

And then, because one example is not evidence, block 6 runs **200 random graphs** and checks both orderings against Bellman–Ford:

```
    graphs tested: 200
    k-outermost   agreed with Bellman-Ford: 200/200
    i-outermost   DISAGREED on: 105/200 graphs
```

**More than half.** This is not a corner case — the wrong loop order is wrong most of the time, and the reason it survives in people's memory is that on small or nearly-complete graphs it often coincidentally agrees.

---

## 5. Negative cycles live on the diagonal

$d[v][v]$ starts at 0 — the cost of going from a vertex to itself by doing nothing. It can only become negative if there is a route that leaves $v$, comes back, and costs less than nothing.

**So: a negative cycle exists if and only if some $d[v][v] < 0$ after the algorithm finishes.** One scan of the diagonal, $O(V)$, no extra pass required.

The lab checks both cases on a triangle:

```
    cycle weight +1 (no negative cycle)
      diagonal: {'X': 0, 'Y': 0, 'Z': 0}   negative cycle detected: False
    cycle weight -3 (negative cycle)
      diagonal: {'X': -3, 'Y': -3, 'Z': -6}   negative cycle detected: True
```

**As with Bellman–Ford, the off-diagonal numbers in the negative-cycle case are meaningless** — detect and report, do not use.

> **One caution the textbooks gloss over.** With a negative cycle present, the $O(V^3)$ loop can propagate arbitrarily negative values into cells, and with floating-point weights this can reach $-\infty$ or produce `nan`. Detect the cycle and stop, rather than handing the matrix to anything downstream.

---

## 6. Floyd–Warshall or $V$ Dijkstras?

| | Floyd–Warshall | $V$ × Dijkstra |
| :--- | :--- | :--- |
| Cost | $\Theta(V^3)$ always | $O(V E \log V)$ |
| Negative weights | **yes** | no |
| Negative cycle detection | yes, on the diagonal | no |
| Space | $\Theta(V^2)$ | $\Theta(V^2)$ for the output |
| Lines of code | about 5 | about 20 |
| Best when | **dense** graphs, small $V$ | **sparse** graphs |

The lab computes the crossover directly:

```
    sparse graphs (E ~ 5V):
    V= 1000 E=  5000 | Floyd-Warshall V^3 = 1,000,000,000 | Dijkstra x V ~    70,000,000 | FW wins: False
    dense graphs (E ~ V^2/2):
    V= 1000 E=500000 | Floyd-Warshall V^3 = 1,000,000,000 | Dijkstra x V ~ 7,000,000,000 | FW wins: True
```

**The rule of thumb: if $E$ is close to $V^2$, use Floyd–Warshall; if $E$ is closer to $V$, run Dijkstra $V$ times.** And if you have negative weights on a sparse graph and need all pairs, the right answer is **Johnson's algorithm** — one Bellman–Ford run to reweight every edge to be non-negative, then $V$ Dijkstras on the reweighted graph, for $O(VE\log V)$ with negative weights allowed.

**In practice, $V^3$ caps you at a few thousand vertices.** At $V = 5000$ that is $1.25 \times 10^{11}$ operations. Floyd–Warshall's real niche is small dense graphs where its five lines beat twenty lines of Dijkstra on engineering time.

---

## 7. The same algorithm, other operators

Replace $(\min, +)$ with other pairs and the identical triple loop solves different problems. This is not a coincidence — it works for any pair of operators forming a **semiring**, where one distributes over the other.

| Problem | Combine paths | Combine edges | Start value |
| :--- | :--- | :--- | :--- |
| Shortest path | $\min$ | $+$ | $\infty$ |
| **Transitive closure** (Warshall) | `or` | `and` | `False` |
| Widest path / bottleneck | $\max$ | $\min$ | $-\infty$ |
| Most reliable path | $\max$ | $\times$ | 0 |
| Counting paths | $+$ | $\times$ | 0 |

The lab runs the transitive closure variant on a chain `A→B→C→D` and produces the upper-triangular reachability table you would expect.

**Recognising this family is worth more than memorising the shortest-path version**, because "shortest" is only one of the questions it answers.

---

## 8. Worked example — complete runnable lab

Save as `floyd_warshall.py`. Standard library only.

```python
"""Floyd-Warshall: every shortest path, by allowing one more intermediate vertex at a time.

Run:  python3 floyd_warshall.py
"""

INF = float("inf")

V = ["A", "B", "C", "D"]
EDGES = [
    ("A", "B", 3), ("A", "D", 7),
    ("B", "A", 8), ("B", "C", 2),
    ("C", "A", 5), ("C", "D", 1),
    ("D", "A", 2),
]


def build(vertices, edges):
    d = {u: {v: (0 if u == v else INF) for v in vertices} for u in vertices}
    nxt = {u: {v: (v if u == v else None) for v in vertices} for u in vertices}
    for u, v, w in edges:
        if w < d[u][v]:
            d[u][v] = w
            nxt[u][v] = v
    return d, nxt


def floyd_warshall(vertices, edges, trace=False):
    d, nxt = build(vertices, edges)
    snapshots = [("initial (no intermediates allowed)", copy(d))]
    for k in vertices:
        for i in vertices:
            for j in vertices:
                if d[i][k] + d[k][j] < d[i][j]:
                    d[i][j] = d[i][k] + d[k][j]
                    nxt[i][j] = nxt[i][k]
        if trace:
            snapshots.append((f"after allowing {k} as an intermediate", copy(d)))
    return d, nxt, snapshots


def copy(d):
    return {u: dict(r) for u, r in d.items()}


def path(nxt, i, j):
    if nxt[i][j] is None:
        return None
    out = [i]
    while i != j:
        i = nxt[i][j]
        if i is None:
            return None
        out.append(i)
    return out


def show(d, vertices, title):
    print(f"  {title}")
    print("       " + "".join(f"{v:>6}" for v in vertices))
    for i in vertices:
        cells = "".join(f"{('inf' if d[i][j] == INF else d[i][j]):>6}" for j in vertices)
        print(f"    {i}  {cells}")


def bellman_ford(vertices, edges, source):
    dist = {v: INF for v in vertices}
    dist[source] = 0
    for _ in range(len(vertices) - 1):
        for u, v, w in edges:
            if dist[u] != INF and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
    return dist


def main():
    print("=== 1. The graph ===")
    for u, v, w in EDGES:
        print(f"    {u} -> {v}  weight {w}")

    print("\n=== 2. Watching k grow: each round allows ONE more intermediate ===")
    d, nxt, snaps = floyd_warshall(V, EDGES, trace=True)
    for title, mat in snaps:
        print()
        show(mat, V, title)
    print("\n  -> d[i][j] after round k = shortest path using only {first k vertices} inside")

    print("\n=== 3. Reconstructing actual paths ===")
    for i in V:
        for j in V:
            if i != j:
                p = path(nxt, i, j)
                cost = d[i][j]
                print(f"    {i} -> {j}: cost {cost:>3}   path {' -> '.join(p) if p else 'none'}")

    print("\n=== 4. Cross-check against Bellman-Ford from every source ===")
    ok = True
    for s in V:
        bf = bellman_ford(V, EDGES, s)
        for t in V:
            if bf[t] != d[s][t]:
                ok = False
                print(f"    MISMATCH {s}->{t}: FW={d[s][t]} BF={bf[t]}")
    print(f"    all {len(V)**2} pairs agree with Bellman-Ford: {ok}")

    print("\n=== 5. The loop order is not a stylistic choice ===")
    print("    Correct order is k, then i, then j -- k MUST be outermost.")
    d_wrong, _ = build(V, EDGES)
    for i in V:                       # i outermost: WRONG
        for j in V:
            for k in V:
                if d_wrong[i][k] + d_wrong[k][j] < d_wrong[i][j]:
                    d_wrong[i][j] = d_wrong[i][k] + d_wrong[k][j]
    print()
    show(d, V, "k outermost (correct)")
    print()
    show(d_wrong, V, "i outermost (wrong)")
    diffs = [(i, j, d[i][j], d_wrong[i][j]) for i in V for j in V if d[i][j] != d_wrong[i][j]]
    print(f"\n    differing cells (i, j, correct, wrong): {diffs}")
    print("    -> B->A is really 5 (B->C->D->A = 2+1+2). The wrong order reports 7,")
    print("       because when it computed B->A it had not yet learned C->A via D.")

    print("\n=== 6. How often does the wrong order fail? (200 random graphs) ===")
    import random
    random.seed(7)
    names = ["v0", "v1", "v2", "v3", "v4", "v5"]
    wrong_count, checked = 0, 0
    worst = None
    for _ in range(200):
        es = []
        for a in names:
            for b in names:
                if a != b and random.random() < 0.35:
                    es.append((a, b, random.randint(1, 9)))
        good, _, _ = floyd_warshall(names, es)
        bad, _ = build(names, es)
        for i in names:
            for j in names:
                for k in names:
                    if bad[i][k] + bad[k][j] < bad[i][j]:
                        bad[i][j] = bad[i][k] + bad[k][j]
        # ground truth, independently: Bellman-Ford from every source
        truth = {s0: bellman_ford(names, es, s0) for s0 in names}
        g_ok = all(good[i][j] == truth[i][j] for i in names for j in names)
        b_ok = all(bad[i][j] == truth[i][j] for i in names for j in names)
        checked += 1
        if not g_ok:
            print("    !! correct order disagreed with Bellman-Ford -- bug in the lab")
        if not b_ok:
            wrong_count += 1
            if worst is None:
                worst = [(i, j, truth[i][j], bad[i][j])
                         for i in names for j in names if truth[i][j] != bad[i][j]]
    print(f"    graphs tested: {checked}")
    print(f"    k-outermost   agreed with Bellman-Ford: {checked}/{checked}")
    print(f"    i-outermost   DISAGREED on: {wrong_count}/{checked} graphs")
    print(f"    first failure, cells (i, j, true, wrong): {worst[:4] if worst else None}")
    print("    -> the wrong order overestimates: it uses d[i][k] before d[i][k] is final")

    print("\n=== 7. Negative cycle detection: look at the diagonal ===")
    V3 = ["X", "Y", "Z"]
    E3_ok = [("X", "Y", 4), ("Y", "Z", -2), ("Z", "X", -1)]      # sum = 1, fine
    E3_bad = [("X", "Y", 4), ("Y", "Z", -6), ("Z", "X", -1)]     # sum = -3, cycle
    for label, E3 in (("cycle weight +1 (no negative cycle)", E3_ok),
                      ("cycle weight -3 (negative cycle)", E3_bad)):
        dd, _, _ = floyd_warshall(V3, E3)
        diag = {v: dd[v][v] for v in V3}
        neg = any(dd[v][v] < 0 for v in V3)
        print(f"    {label}")
        print(f"      diagonal: {diag}   negative cycle detected: {neg}")
    print("    -> d[v][v] < 0 means v can return to itself at negative cost")

    print("\n=== 8. Transitive closure: the same algorithm with OR and AND ===")
    # A subset of the edges, chosen so that not everything reaches everything.
    CLOSURE_EDGES = [("A", "B", 3), ("B", "C", 2), ("C", "D", 1)]
    print("    using only A->B, B->C, C->D (so the answer is not all-True)")
    reach = {i: {j: (i == j) for j in V} for i in V}
    for u, v, _ in CLOSURE_EDGES:
        reach[u][v] = True
    for k in V:
        for i in V:
            for j in V:
                reach[i][j] = reach[i][j] or (reach[i][k] and reach[k][j])
    print("       " + "".join(f"{v:>6}" for v in V))
    for i in V:
        print(f"    {i}  " + "".join(f"{('T' if reach[i][j] else 'F'):>6}" for j in V))
    print("    -> replace (min, +) with (or, and) and you get Warshall's reachability")

    print("\n=== 9. Cost comparison ===")
    print("    sparse graphs (E ~ 5V):")
    for n, e in ((100, 500), (1000, 5000), (5000, 25000)):
        fw = n ** 3
        dij = n * e * 14
        print(f"    V={n:>5} E={e:>6} | Floyd-Warshall V^3 = {fw:>15,} "
              f"| Dijkstra x V ~ {dij:>15,} | FW wins: {fw < dij}")
    print("    dense graphs (E ~ V^2/2):")
    for n in (100, 500, 1000):
        e = n * n // 2
        fw = n ** 3
        dij = n * e * 14
        print(f"    V={n:>5} E={e:>6} | Floyd-Warshall V^3 = {fw:>15,} "
              f"| Dijkstra x V ~ {dij:>15,} | FW wins: {fw < dij}")
    print("    -> Floyd-Warshall wins on DENSE graphs, loses badly on sparse ones")


if __name__ == "__main__":
    main()
```

### Expected output

Generated by running the file above:

```
=== 1. The graph ===
    A -> B  weight 3
    A -> D  weight 7
    B -> A  weight 8
    B -> C  weight 2
    C -> A  weight 5
    C -> D  weight 1
    D -> A  weight 2

=== 2. Watching k grow: each round allows ONE more intermediate ===

  initial (no intermediates allowed)
            A     B     C     D
    A       0     3   inf     7
    B       8     0     2   inf
    C       5   inf     0     1
    D       2   inf   inf     0

  after allowing A as an intermediate
            A     B     C     D
    A       0     3   inf     7
    B       8     0     2    15
    C       5     8     0     1
    D       2     5   inf     0

  after allowing B as an intermediate
            A     B     C     D
    A       0     3     5     7
    B       8     0     2    15
    C       5     8     0     1
    D       2     5     7     0

  after allowing C as an intermediate
            A     B     C     D
    A       0     3     5     6
    B       7     0     2     3
    C       5     8     0     1
    D       2     5     7     0

  after allowing D as an intermediate
            A     B     C     D
    A       0     3     5     6
    B       5     0     2     3
    C       3     6     0     1
    D       2     5     7     0

  -> d[i][j] after round k = shortest path using only {first k vertices} inside

=== 3. Reconstructing actual paths ===
    A -> B: cost   3   path A -> B
    A -> C: cost   5   path A -> B -> C
    A -> D: cost   6   path A -> B -> C -> D
    B -> A: cost   5   path B -> C -> D -> A
    B -> C: cost   2   path B -> C
    B -> D: cost   3   path B -> C -> D
    C -> A: cost   3   path C -> D -> A
    C -> B: cost   6   path C -> D -> A -> B
    C -> D: cost   1   path C -> D
    D -> A: cost   2   path D -> A
    D -> B: cost   5   path D -> A -> B
    D -> C: cost   7   path D -> A -> B -> C

=== 4. Cross-check against Bellman-Ford from every source ===
    all 16 pairs agree with Bellman-Ford: True

=== 5. The loop order is not a stylistic choice ===
    Correct order is k, then i, then j -- k MUST be outermost.

  k outermost (correct)
            A     B     C     D
    A       0     3     5     6
    B       5     0     2     3
    C       3     6     0     1
    D       2     5     7     0

  i outermost (wrong)
            A     B     C     D
    A       0     3     5     6
    B       7     0     2     3
    C       3     6     0     1
    D       2     5     7     0

    differing cells (i, j, correct, wrong): [('B', 'A', 5, 7)]
    -> B->A is really 5 (B->C->D->A = 2+1+2). The wrong order reports 7,
       because when it computed B->A it had not yet learned C->A via D.

=== 6. How often does the wrong order fail? (200 random graphs) ===
    graphs tested: 200
    k-outermost   agreed with Bellman-Ford: 200/200
    i-outermost   DISAGREED on: 105/200 graphs
    first failure, cells (i, j, true, wrong): [('v2', 'v0', 13, inf)]
    -> the wrong order overestimates: it uses d[i][k] before d[i][k] is final

=== 7. Negative cycle detection: look at the diagonal ===
    cycle weight +1 (no negative cycle)
      diagonal: {'X': 0, 'Y': 0, 'Z': 0}   negative cycle detected: False
    cycle weight -3 (negative cycle)
      diagonal: {'X': -3, 'Y': -3, 'Z': -6}   negative cycle detected: True
    -> d[v][v] < 0 means v can return to itself at negative cost

=== 8. Transitive closure: the same algorithm with OR and AND ===
    using only A->B, B->C, C->D (so the answer is not all-True)
            A     B     C     D
    A       T     T     T     T
    B       F     T     T     T
    C       F     F     T     T
    D       F     F     F     T
    -> replace (min, +) with (or, and) and you get Warshall's reachability

=== 9. Cost comparison ===
    sparse graphs (E ~ 5V):
    V=  100 E=   500 | Floyd-Warshall V^3 =       1,000,000 | Dijkstra x V ~         700,000 | FW wins: False
    V= 1000 E=  5000 | Floyd-Warshall V^3 =   1,000,000,000 | Dijkstra x V ~      70,000,000 | FW wins: False
    V= 5000 E= 25000 | Floyd-Warshall V^3 = 125,000,000,000 | Dijkstra x V ~   1,750,000,000 | FW wins: False
    dense graphs (E ~ V^2/2):
    V=  100 E=  5000 | Floyd-Warshall V^3 =       1,000,000 | Dijkstra x V ~       7,000,000 | FW wins: True
    V=  500 E=125000 | Floyd-Warshall V^3 =     125,000,000 | Dijkstra x V ~     875,000,000 | FW wins: True
    V= 1000 E=500000 | Floyd-Warshall V^3 =   1,000,000,000 | Dijkstra x V ~   7,000,000,000 | FW wins: True
    -> Floyd-Warshall wins on DENSE graphs, loses badly on sparse ones
```

---

## 9. Common pitfalls and traps

1. **Getting the loop order wrong.** $k$ must be outermost. The lab shows the wrong order disagreeing with ground truth on **105 of 200** random graphs. If you remember one thing from this lesson, remember this.
2. **Initialising the diagonal to infinity.** $d[v][v]$ must start at **0**. Start it at infinity and the negative-cycle test never fires, and self-loops get misread.
3. **Forgetting parallel edges.** If the input can contain two edges between the same pair, keep the **minimum** when building the matrix. Overwriting blindly means the last one in the list wins, which may not be the cheapest.
4. **`INF + INF` overflow.** With `float("inf")` this is fine. With a large integer sentinel like `10**9`, adding two gives $2 \times 10^9$, which may overflow a fixed-width integer in C++ or Java, wrap to negative, and look like a shortest path. Guard with `if d[i][k] != INF and d[k][j] != INF`.
5. **Using it on a sparse graph.** At $V = 1000$, $E = 5000$, Floyd–Warshall does a billion operations where $V$ Dijkstras do 70 million — **14× slower**, and it gets worse as the graph grows.
6. **Trusting the matrix when a negative cycle exists.** Check the diagonal *before* using any value. The off-diagonal entries are partial results, not answers.
7. **Assuming it is undirected-safe.** It handles directed graphs natively. For an undirected graph, insert **both** directions when building the matrix — and remember that an undirected negative edge is automatically a negative cycle.
8. **Reconstructing paths without the `next` matrix.** The distance table does not contain the routes. Maintaining `next` costs one extra line during the update and nothing at all afterwards.

---

## 10. Check your understanding

1. **After round $k$, what exactly does $d[i][j]$ hold?**
   <details><summary>Answer</summary>The cost of the shortest path from $i$ to $j$ that uses <b>only the first $k$ vertices as intermediates</b>. The endpoints $i$ and $j$ are not restricted — they never count as intermediates. After the final round every vertex is permitted, so the restriction is vacuous and the value is the true shortest distance.</details>

2. **Why does the algorithm not need to consider using $k$ twice?**
   <details><summary>Answer</summary>Because a path visiting $k$ twice contains a cycle through $k$, and with no negative cycles present, deleting that cycle cannot increase the cost. So a shortest path that is simple always exists, and a simple path uses each vertex at most once as an intermediate. Considering each $k$ exactly once is therefore enough.</details>

3. **You need all-pairs shortest paths on a graph with $V=800$, $E=310{,}000$, all weights positive. Which algorithm?**
   <details><summary>Answer</summary>Floyd–Warshall. The graph is dense ($E \approx V^2/2$), so $V^3 = 5.1\times10^8$ against $V E \log V \approx 800 \times 310{,}000 \times 10 = 2.5\times10^9$ for repeated Dijkstra — about five times cheaper, and a fraction of the code.</details>

4. **Same question but $V = 800$ and $E = 2{,}400$, with some negative weights and no negative cycles.**
   <details><summary>Answer</summary>Johnson's algorithm. The graph is sparse, so $V$ Dijkstras would win on cost — but Dijkstra cannot handle negative weights. Johnson's runs Bellman–Ford once to compute a potential that reweights every edge to be non-negative while preserving shortest paths, then runs $V$ Dijkstras. Floyd–Warshall would also be correct, just about 40× slower here.</details>

5. **A colleague computes the transitive closure by running Floyd–Warshall with weight 1 on every edge and testing `d[i][j] < INF`. Does it work, and is it a good idea?**
   <details><summary>Answer</summary>It works — a finite distance means a path exists. It is wasteful: it computes and compares integers where booleans would do, and the boolean version uses one bit per cell instead of a word, which for large $V$ is the difference between fitting in cache and not. Warshall's variant with <code>or</code>/<code>and</code> is the same triple loop and strictly cheaper. It also risks the overflow of pitfall 4 for no benefit.</details>

---

## 11. Practice — independent task

Implement `all_pairs(vertices, edges)` returning distances, paths, and a negative-cycle verdict.

**Part 1 — the core.** Distance matrix plus `next` matrix, with a `path(i, j)` helper. Assert every returned path's edge weights actually sum to the reported distance — **this catches `next` bugs that the distances alone hide.**

**Part 2 — prove the loop order matters.** Implement all six permutations of the three loops. Run all six on 500 random graphs, checking each against Bellman–Ford from every source. Report the failure rate per permutation. **Predict which permutations will work before you run it**, and explain any that surprise you.

**Part 3 — negative cycles.** Detect via the diagonal. Then *identify* one: find a $v$ with $d[v][v] < 0$ and recover the actual cycle through it. Verify its weights sum negative.

**Part 4 — the semiring family.** Parameterise your implementation on `(combine, extend, identity)` so the same function computes shortest path, transitive closure, widest path, and path count. Verify each against an independent brute-force over all simple paths on graphs with $V \le 6$.

**Part 5 — the crossover.** Time your implementation against $V$ runs of Dijkstra across a range of densities at fixed $V=200$. Find the density at which they cross. **Compare that measured crossover to the one predicted by $V^3$ versus $VE\log V$**, and account for any gap.

**Edge cases:** a single vertex; no edges at all; parallel edges of different weights; a self-loop of positive weight (must not change anything) and of negative weight (a negative cycle of length 1); a disconnected graph, where some cells stay infinite.

**Done when:** part 1's path/distance assertion passes on 500 random graphs; part 2's failure rates match your predictions; part 4's four variants all agree with brute force; and you can state the measured crossover density with a number.

---

## Before moving on

You can state the subproblem Floyd–Warshall solves, explain why $k$ must be the outer loop and demonstrate the alternative failing, detect negative cycles from the diagonal, reconstruct paths from a `next` matrix, and choose between this and repeated Dijkstra from density.

**Recap:** reframe the question as "shortest path allowed to pass through only the first $k$ vertices", and the recurrence writes itself: $d_k[i][j] = \min(d_{k-1}[i][j],\ d_{k-1}[i][k] + d_{k-1}[k][j])$ — either the path avoids $k$, or it is two already-solved halves joined at $k$. **The $k$ loop must be outermost**, because the two halves must be final before you compose them; the wrong order disagreed with ground truth on 105 of 200 random graphs. Cost is $\Theta(V^3)$ regardless of edge count, space $\Theta(V^2)$. Negative weights are fine; negative cycles show up as $d[v][v] < 0$. Keep a `next` matrix to recover routes. Use it on **dense** graphs; on sparse ones run Dijkstra $V$ times, or Johnson's if weights can be negative. Swap $(\min,+)$ for `(or, and)` and the same loop computes transitive closure.

**Next:** [[05-a-star|A\*]] — the opposite trade. Instead of computing every path, aim the search at one goal using an estimate of the distance remaining, and expand as few vertices as the estimate allows.

---

## Related

- [[03-bellman-ford|Bellman–Ford]] — single source with negative weights; the reweighting step inside Johnson's algorithm
- [[02-dijkstra|Dijkstra's Algorithm]] — run $V$ times, the sparse-graph alternative
- [[04-representations|Representations]] — the adjacency matrix this operates on
- [[15-dynamic-programming|Dynamic Programming]] — the technique this is an instance of
- [[02-paths-cycles-and-connectivity|Paths, Cycles and Connectivity]] — reachability and the transitive closure
- [[06-algorithms/index|the graph algorithms index]]

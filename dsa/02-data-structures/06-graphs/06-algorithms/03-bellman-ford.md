# Module: Bellman–Ford (Shortest Paths When Weights Can Be Negative)

**[Advanced]** — [[02-dijkstra|Dijkstra]] is faster and it is the one everybody names. It is also **wrong** on any graph with a negative edge, and it does not tell you — it returns a plausible number. Bellman–Ford is the algorithm that trades a factor of $V$ for correctness on any weights at all, and it is the only one here that can tell you when "shortest path" has no answer.

---

## Before you start

- You can implement [[02-dijkstra|Dijkstra]] and explain why it finalises the closest unfinalised vertex.
- You know what a **directed cycle** is, and what makes a graph a **DAG (directed acyclic graph)** — [[02-paths-cycles-and-connectivity|paths, cycles and connectivity]].
- You can read an [[04-representations|edge list]], and you know it is a different representation from an adjacency list.

**After this lesson you will be able to:**

1. Explain **why** Dijkstra breaks on negative weights, in terms of its finalisation step rather than by assertion.
2. Implement Bellman–Ford, and justify the $V-1$ rounds from the maximum length of a shortest path.
3. **Detect a negative cycle** with one extra pass, and say why detection is the only sensible response rather than a correction.
4. Choose between BFS, Dijkstra and Bellman–Ford from a graph's properties.

**Study route:** read 1–3, predict the answer in section 4 before reading it, then run the lab. Section 6 is where negative weights stop being a curiosity.

---

## 1. Why this exists: a wrong answer that looks right

Dijkstra's correctness rests on one assumption, and it is worth stating precisely:

> **Once the closest unfinalised vertex is popped, its distance is final — because every other route to it would have to go through a vertex that is already further away, and extending a path can only make it longer.**

**The last clause is the assumption.** "Extending a path can only make it longer" is true exactly when every edge weight is non-negative. Add one negative edge and it collapses.

Here is the smallest graph that breaks it:

```
          1              2
    S ────────▶ A ────────▶ C
    │                       ▲
    │ 5                     │ -4
    └────────▶ B ───────────┘
```

Trace Dijkstra from `S`:

1. Pop `S` at 0. Relax: `A = 1`, `B = 5`.
2. Pop `A` at 1 — the closest. Relax: `C = 1 + 2 = 3`.
3. Pop `C` at 3 — closer than `B` at 5. **`C` is now finalised at 3.**
4. Pop `B` at 5. Relax `C`: $5 + (-4) = 1$, which is better than 3 — **but `C` is finalised, so the improvement is discarded.**

Dijkstra reports $C = 3$. The true answer is $1$, via $S \to B \to C$. The lab runs both and prints them side by side:

```
  Dijkstra     : A=1  B=5  C=3  S=0
  Bellman-Ford : A=1  B=5  C=1  S=0
```

**No exception is raised. No warning is printed.** You get a number that is 200% of the truth, and in a production routing system you would never know. That is the reason this lesson exists: not because negative weights are common, but because the failure mode is silent.

### Where negative weights actually come from

They sound artificial until you have met them:

1. **Currency arbitrage.** Take $-\log(\text{exchange rate})$ as the edge weight, and a profitable trading cycle becomes a negative cycle. Finding one is exactly the negative-cycle detection in section 5.
2. **Any cost that can be a rebate.** Toll roads with credits, energy recovered by a downhill leg, a delivery route that picks up a paying load partway.
3. **Difference constraints.** Systems of inequalities $x_j - x_i \le w$ map directly onto a shortest-path problem with arbitrary-sign weights, which is how schedulers solve timing constraints.
4. **Johnson's algorithm**, which reweights a graph to remove negative edges so Dijkstra can be run many times — and uses Bellman–Ford once to compute the reweighting.

---

## Terms used in Bellman–Ford

1. **Relaxation**: This is the single operation the whole algorithm is built from. To relax an edge $u \to v$ with weight $w$ is to ask whether going to $u$ and then taking that edge beats the best route to $v$ found so far — and if it does, to record the better value. In code it is one `if`: `if dist[u] + w < dist[v]: dist[v] = dist[u] + w`.
2. **Round**: This is also called a **pass** or an **iteration**. This is one sweep in which **every edge in the graph** is relaxed once, in some order. Bellman–Ford performs $V-1$ rounds.
3. **Negative cycle**: This is a directed cycle whose edge weights sum to a negative number. Its existence means you can lower a path's cost without limit by going round it again, so **the shortest path is not merely hard to find — it does not exist.**
4. **Reachable negative cycle**: This is a negative cycle you can actually get to from the source. A negative cycle sitting in an unreachable part of the graph does not affect any distance from that source, and a careful implementation reports only reachable ones.
5. **Edge list**: This is the representation Bellman–Ford wants — a flat list of $(u, v, w)$ triples. It never asks "what are the neighbours of $u$?", so the adjacency list that Dijkstra and [[01-depth-first-search|DFS]] need buys it nothing.
6. **Early termination**: This is stopping once a full round changes nothing. If an entire pass over every edge improves no distance, no later pass can either, because the inputs to every comparison are unchanged.
7. **Predecessor array**: This is also called the **parent array**. This is the record of which vertex each distance came from, which is how you recover an actual path rather than only its cost.

---

## 2. The algorithm

**In words: start with every distance at infinity except the source, then relax every edge in the graph, $V-1$ times over.**

That is the whole thing. There is no priority queue, no visited set, no finalisation — and the absence of finalisation is precisely why it survives negative weights. A distance can be improved at any point, right up to the last round.

```python
def bellman_ford(graph, source):
    dist = {v: INF for v in graph}
    parent = {v: None for v in graph}
    dist[source] = 0
    edges = [(u, v, w) for u in graph for v, w in graph[u]]

    for _ in range(len(graph) - 1):          # V-1 rounds
        changed = False
        for u, v, w in edges:                # relax EVERY edge
            if dist[u] != INF and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                parent[v] = u
                changed = True
        if not changed:
            break                            # early termination

    # One extra pass: any further improvement means a negative cycle.
    for u, v, w in edges:
        if dist[u] != INF and dist[u] + w < dist[v]:
            return dist, parent, True
    return dist, parent, False
```

**The `dist[u] != INF` guard is not decoration.** Without it, `INF + (-4)` is still `INF` in floating point but would be a real comparison with integers or a sentinel — and relaxing out of an unreached vertex would invent paths that do not exist.

---

## 3. Why exactly $V-1$ rounds

This is the part to be able to derive rather than recall.

**The claim in words: after $k$ rounds, every vertex reachable by a shortest path of at most $k$ edges has its final distance. Since no shortest path can use more than $V-1$ edges, $V-1$ rounds finish the job.**

**Why a shortest path uses at most $V-1$ edges.** A path with $V$ edges visits $V+1$ vertices, so by the pigeonhole principle it repeats one — it contains a cycle. If the graph has no negative cycle, removing that cycle cannot increase the cost, so a shortest path that is simple always exists. A simple path visits at most $V$ vertices and therefore uses at most $V-1$ edges.

**Why one round extends the guarantee by one edge.** Suppose the shortest path to $v$ is $s \to \dots \to u \to v$ using $k$ edges, and after $k-1$ rounds `dist[u]` is already final. During round $k$, every edge is relaxed — including $u \to v$ — so `dist[v]` becomes at most `dist[u] + w`, which is the shortest-path value. It cannot go lower, because no shorter path exists. Induction does the rest.

**Note what this argument does *not* assume: the order of edges within a round.** That is why the bound is $V-1$ and not smaller — a bad order makes progress one edge at a time. The lab shows exactly this, relaxing a 5-vertex chain in reverse order:

```
  start : v0=0  v1=inf  v2=inf  v3=inf  v4=inf
  round1: v0=0  v1=1    v2=inf  v3=inf  v4=inf
  round2: v0=0  v1=1    v2=2    v3=inf  v4=inf
  round3: v0=0  v1=1    v2=2    v3=3    v4=inf
  round4: v0=0  v1=1    v2=2    v3=3    v4=4
```

One vertex per round — the worst case, achieved. **And the same graph with the edges in a sensible order converges in a single round**, which the lab also shows. $V-1$ is a guarantee about the worst edge ordering, not a description of every run. This is why early termination is worth having: it often stops after two or three rounds, and the lab reports 2 rounds used on both test graphs where 3 and 4 were allowed. (The last of those rounds is the one that changed nothing and triggered the stop.)

---

## 4. Negative cycles: detection, not repair

> **Predict before reading on.** Take the trap graph and add one edge, `C -> B` with weight $-1$. Now $B \to C \to B$ costs $-4 + -1 = -5$. What should `bellman_ford` return for `dist[B]`? Commit to an answer before continuing.

**The honest answer is that there is no correct value to return**, and that is the point.

Walk $B \to C \to B$ once and you save 5. Walk it twice and you save 10. There is no lower bound, so $\text{dist}[B] = -\infty$, and every vertex reachable *from* the cycle inherits the same problem. **"Shortest path" is undefined here — not expensive, not hard, undefined.**

The lab reports what the algorithm actually produces:

```
  negative cycle reachable from S: True
  distances after V-1 rounds     : A=1  B=-10  C=-9  S=0
```

$B = -10$ is not an answer. It is simply how far the algorithm got in three rounds; with more rounds it would keep falling. **The `True` is the answer.**

### How the detection works

After $V-1$ rounds, every distance is final **if no negative cycle is reachable**. So run one more round: if any edge can still be relaxed, some distance is still falling, which can only happen if it is falling forever. One extra $O(E)$ pass, and the test is exact.

**This is why the check is a separate pass rather than a guard inside the loop.** You cannot detect it during the main rounds, because a distance legitimately improving on round 3 looks identical to one improving because of a cycle. Only the fact that it is *still* improving after $V-1$ rounds distinguishes them.

**To find the cycle itself** rather than just detect it: remember which vertex was relaxed in that extra pass, walk the predecessor array back $V$ times to guarantee you are inside the cycle, then walk until you return to where you started.

---

## 5. Choosing between the three

| Algorithm | Cost | Correct when | Detects negative cycles |
| :--- | :--- | :--- | :--- |
| [[02-breadth-first-search\|BFS]] | $O(V+E)$ | all weights equal | — |
| [[02-dijkstra\|Dijkstra]] | $O(E\log V)$ | **no negative weights** | no |
| **Bellman–Ford** | $O(V \cdot E)$ | **any weights** | **yes** |

**The factor you are buying with is $V$.** On a graph with 10,000 vertices and 50,000 edges, Dijkstra does roughly $50{,}000 \times 14 \approx 700{,}000$ units of work and Bellman–Ford does $10{,}000 \times 50{,}000 = 5 \times 10^8$. That is a difference between milliseconds and minutes, which is why nobody uses Bellman–Ford when Dijkstra is valid.

**Two refinements worth knowing by name:**

1. **SPFA** (shortest path faster algorithm) — Bellman–Ford with a queue of vertices whose distance changed, so you only relax edges out of those. Much faster in practice, **the same $O(VE)$ worst case**, and there are adversarial graphs that hit it. Do not quote it as an improvement in asymptotic terms.
2. **On a DAG, neither is needed.** Relax edges in [[01-topological-sort|topological order]] and you get shortest paths in $O(V+E)$ with *any* weights, negative included — because a topological order guarantees you never need to revisit. If your graph is acyclic, this is strictly the right answer.

---

## 6. Worked example — complete runnable lab

Save as `bellman_ford.py`. Standard library only.

```python
"""Bellman-Ford: shortest paths that survive negative weights, and detect negative cycles.

Run:  python3 bellman_ford.py
"""

import heapq

INF = float("inf")

# Dijkstra gets this graph WRONG. C is finalised at 3 before the cheaper
# route through B (which costs 5 to reach, then -4) is ever considered.
TRAP = {
    "S": [("A", 1), ("B", 5)],
    "A": [("C", 2)],
    "B": [("C", -4)],
    "C": [],
}

# Same graph plus C -> B, which closes a cycle of total weight -4 + -1 = -5.
NEG_CYCLE = {
    "S": [("A", 1), ("B", 5)],
    "A": [("C", 2)],
    "B": [("C", -4)],
    "C": [("B", -1)],
}

# A chain, used to show why V-1 rounds are both necessary and sufficient.
CHAIN = {
    "v0": [("v1", 1)],
    "v1": [("v2", 1)],
    "v2": [("v3", 1)],
    "v3": [("v4", 1)],
    "v4": [],
}


def dijkstra(graph, source):
    """Textbook Dijkstra WITH finalisation -- the version that breaks."""
    dist = {v: INF for v in graph}
    dist[source] = 0
    done = set()
    pq = [(0, source)]
    while pq:
        d, u = heapq.heappop(pq)
        if u in done:
            continue
        done.add(u)                       # <- once finalised, never revisited
        for v, w in graph[u]:
            if v not in done and d + w < dist[v]:
                dist[v] = d + w
                heapq.heappush(pq, (dist[v], v))
    return dist


def bellman_ford(graph, source):
    """Return (dist, parent, negative_cycle_reachable, rounds_used)."""
    dist = {v: INF for v in graph}
    parent = {v: None for v in graph}
    dist[source] = 0
    edges = [(u, v, w) for u in graph for v, w in graph[u]]

    rounds_used = 0
    for i in range(len(graph) - 1):
        changed = False
        for u, v, w in edges:
            if dist[u] != INF and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                parent[v] = u
                changed = True
        rounds_used = i + 1
        if not changed:                   # nothing improved: we are done early
            break

    # One more pass. Any further improvement means a reachable negative cycle.
    negative = False
    for u, v, w in edges:
        if dist[u] != INF and dist[u] + w < dist[v]:
            negative = True
            break
    return dist, parent, negative, rounds_used


def trace_rounds(graph, source):
    """Same algorithm, but report the distance table after every round."""
    dist = {v: INF for v in graph}
    dist[source] = 0
    edges = [(u, v, w) for u in graph for v, w in graph[u]]
    # Deliberately a bad edge order: it relaxes the chain back-to-front, which
    # is the order that actually needs all V-1 rounds.
    edges.reverse()
    snapshots = [dict(dist)]
    for _ in range(len(graph) - 1):
        for u, v, w in edges:
            if dist[u] != INF and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
        snapshots.append(dict(dist))
    return snapshots


def path_to(parent, target):
    out, seen = [], set()
    while target is not None:
        if target in seen:
            return None                   # walked into a cycle
        seen.add(target)
        out.append(target)
        target = parent[target]
    return list(reversed(out))


def show(dist):
    return "  ".join(f"{v}={'inf' if d == INF else d}" for v, d in sorted(dist.items()))


def main():
    print("=== 1. The graph where Dijkstra is silently wrong ===")
    print("  S->A(1)  S->B(5)  A->C(2)  B->C(-4)")
    d_dij = dijkstra(TRAP, "S")
    d_bf, parent, neg, rounds = bellman_ford(TRAP, "S")
    print(f"  Dijkstra     : {show(d_dij)}")
    print(f"  Bellman-Ford : {show(d_bf)}")
    print(f"  true cost of S->B->C = 5 + (-4) = {5 + (-4)}")
    print(f"  Dijkstra's answer for C: {d_dij['C']}   Bellman-Ford's: {d_bf['C']}")
    print("  -> Dijkstra finalised C at 3 before it had looked at B at all.")
    print("     It returns a number, not an error. That is what makes it dangerous.")
    print(f"  shortest path to C: {' -> '.join(path_to(parent, 'C'))}")

    print("\n=== 2. Why V-1 rounds, and not fewer ===")
    print("  A 5-vertex chain v0->v1->v2->v3->v4, edges relaxed in the WORST order.")
    snaps = trace_rounds(CHAIN, "v0")
    for i, snap in enumerate(snaps):
        label = "start " if i == 0 else f"round{i}"
        print(f"  {label}: {show(snap)}")
    print("  -> each round extends the frontier by exactly one edge in this order.")
    print("     A path can use at most V-1 = 4 edges, so 4 rounds always suffice.")

    print("\n  The same graph with a GOOD edge order finishes in one round:")
    dist = {v: INF for v in CHAIN}
    dist["v0"] = 0
    good_edges = [(u, v, w) for u in sorted(CHAIN) for v, w in CHAIN[u]]
    for u, v, w in good_edges:
        if dist[u] != INF and dist[u] + w < dist[v]:
            dist[v] = dist[u] + w
    print(f"  after 1 round: {show(dist)}")
    print("  -> V-1 is the worst case over edge orders, not the cost of every run.")

    print("\n=== 3. Early termination ===")
    for name, g in (("TRAP", TRAP), ("CHAIN", CHAIN)):
        _, _, _, r = bellman_ford(g, "S" if name == "TRAP" else "v0")
        print(f"  {name:<6}: V-1 = {len(g)-1} rounds allowed, actually used {r}")
    print("  -> if a full pass changes nothing, every later pass would change nothing too")

    print("\n=== 4. Detecting a negative cycle ===")
    print("  Adding C->B(-1) makes B->C->B cost -4 + -1 = -5, repeatable forever.")
    d2, parent2, neg2, _ = bellman_ford(NEG_CYCLE, "S")
    print(f"  negative cycle reachable from S: {neg2}")
    print(f"  distances after V-1 rounds     : {show(d2)}")
    print("  -> these numbers are meaningless: going round the cycle again lowers them.")
    print("     'Shortest path' is UNDEFINED when a negative cycle is reachable,")
    print("     which is why the check is a separate Vth pass rather than a fix.")

    d3, _, neg3, _ = bellman_ford(TRAP, "S")
    print(f"  same check on the cycle-free graph: {neg3}")

    print("\n=== 5. What each algorithm costs, and when it is correct ===")
    rows = [
        ("BFS",            "O(V+E)",      "unweighted only"),
        ("Dijkstra",       "O(E log V)",  "non-negative weights only"),
        ("Bellman-Ford",   "O(V*E)",      "any weights; detects negative cycles"),
    ]
    print("   algorithm      | cost         | correct when")
    for a, c, w in rows:
        print(f"   {a:<14} | {c:<12} | {w}")
    V, E = len(TRAP), sum(len(a) for a in TRAP.values())
    print(f"\n  this graph: V={V}, E={E}")
    print(f"  Bellman-Ford relaxations performed: {(V-1)*E} worst case, "
          f"{rounds*E} actually")


if __name__ == "__main__":
    main()
```

### Expected output

Generated by running the file above:

```
=== 1. The graph where Dijkstra is silently wrong ===
  S->A(1)  S->B(5)  A->C(2)  B->C(-4)
  Dijkstra     : A=1  B=5  C=3  S=0
  Bellman-Ford : A=1  B=5  C=1  S=0
  true cost of S->B->C = 5 + (-4) = 1
  Dijkstra's answer for C: 3   Bellman-Ford's: 1
  -> Dijkstra finalised C at 3 before it had looked at B at all.
     It returns a number, not an error. That is what makes it dangerous.
  shortest path to C: S -> B -> C

=== 2. Why V-1 rounds, and not fewer ===
  A 5-vertex chain v0->v1->v2->v3->v4, edges relaxed in the WORST order.
  start : v0=0  v1=inf  v2=inf  v3=inf  v4=inf
  round1: v0=0  v1=1  v2=inf  v3=inf  v4=inf
  round2: v0=0  v1=1  v2=2  v3=inf  v4=inf
  round3: v0=0  v1=1  v2=2  v3=3  v4=inf
  round4: v0=0  v1=1  v2=2  v3=3  v4=4
  -> each round extends the frontier by exactly one edge in this order.
     A path can use at most V-1 = 4 edges, so 4 rounds always suffice.

  The same graph with a GOOD edge order finishes in one round:
  after 1 round: v0=0  v1=1  v2=2  v3=3  v4=4
  -> V-1 is the worst case over edge orders, not the cost of every run.

=== 3. Early termination ===
  TRAP  : V-1 = 3 rounds allowed, actually used 2
  CHAIN : V-1 = 4 rounds allowed, actually used 2
  -> if a full pass changes nothing, every later pass would change nothing too

=== 4. Detecting a negative cycle ===
  Adding C->B(-1) makes B->C->B cost -4 + -1 = -5, repeatable forever.
  negative cycle reachable from S: True
  distances after V-1 rounds     : A=1  B=-10  C=-9  S=0
  -> these numbers are meaningless: going round the cycle again lowers them.
     'Shortest path' is UNDEFINED when a negative cycle is reachable,
     which is why the check is a separate Vth pass rather than a fix.
  same check on the cycle-free graph: False

=== 5. What each algorithm costs, and when it is correct ===
   algorithm      | cost         | correct when
   BFS            | O(V+E)       | unweighted only
   Dijkstra       | O(E log V)   | non-negative weights only
   Bellman-Ford   | O(V*E)       | any weights; detects negative cycles

  this graph: V=4, E=4
  Bellman-Ford relaxations performed: 12 worst case, 8 actually
```

---

## 7. Common pitfalls and traps

1. **Using Dijkstra because the weights "are probably fine".** If a weight *can* be negative, Dijkstra is not a fast approximation — it is an incorrect algorithm that returns a confident number. Check the sign constraint, do not assume it.
2. **Relaxing out of an unreached vertex.** Without the `dist[u] != INF` guard, an unreachable `u` with a negative outgoing edge invents a finite distance for `v`. With floats you may get away with it; with a sentinel integer you will not.
3. **Running only $V-1$ rounds and reporting the distances.** Without the extra pass you cannot know whether those numbers mean anything. **The extra pass is not optional** — it is what distinguishes "these are shortest paths" from "these are how far the algorithm got".
4. **Trying to "fix" a negative cycle by clamping.** There is no correct finite value. Detect it and report it; if the domain allows it (arbitrage), the cycle itself is the answer you wanted.
5. **Confusing a negative *edge* with a negative *cycle*.** Negative edges are fine and Bellman–Ford handles them exactly. Only negative **cycles** make the problem undefined. A DAG can have every edge negative and still have well-defined shortest paths.
6. **Assuming SPFA changes the complexity.** It is the same $O(VE)$ worst case. Competitive programmers have lost on adversarial tests built specifically to defeat it.
7. **Reporting an unreachable negative cycle.** A cycle the source cannot reach does not affect any distance from that source. Checking only edges whose tail has a finite distance handles this, which the lab's guard does.
8. **Forgetting that undirected negative edges are always a negative cycle.** An undirected edge $\{u,v\}$ of weight $-3$ can be traversed back and forth for $-6$, $-9$, and so on. **Negative weights only make sense on directed graphs**, and an undirected graph with any negative edge is automatically undefined.

**Pitfall 8 is the one worth having ready.** "Can Bellman–Ford handle negative weights in an undirected graph?" sounds like a question about the algorithm and is actually a question about whether the problem exists.

---

## 8. Check your understanding

1. **Why does Bellman–Ford not need a priority queue?**
   <details><summary>Answer</summary>Because it never commits to a vertex being finished, so it has no need to pick the best candidate next. Dijkstra's queue exists to serve the finalisation step — pop the closest, declare it final. Bellman–Ford relaxes every edge every round and lets any distance improve at any time, which is exactly what makes it correct with negative weights and exactly what costs it the extra factor of $V$.</details>

2. **A graph has 5 vertices. After 2 rounds nothing changed. Can you stop?**
   <details><summary>Answer</summary>Yes, and safely. If an entire pass over every edge improved nothing, then every value feeding every comparison is unchanged, so the next pass performs the identical comparisons with the identical results. Nothing can start changing again. You still need the negative-cycle check — but it has effectively already run, since the round that changed nothing <i>is</i> a pass with no successful relaxation.</details>

3. **You run Bellman–Ford and get `dist[X] = -47`. Is that a valid shortest distance?**
   <details><summary>Answer</summary>Unknown from that number alone — you must look at the negative-cycle flag. A negative distance is perfectly legitimate if the graph has negative edges and no negative cycle. If the flag is set, $-47$ is meaningless: it is just where the counter had got to when the rounds ran out.</details>

4. **Your graph is a DAG with negative weights. What should you use?**
   <details><summary>Answer</summary>Neither Dijkstra nor Bellman–Ford. Take a [[01-topological-sort|topological order]] and relax each vertex's outgoing edges in that order: $O(V+E)$, correct for any weights. The topological order guarantees that when you process $u$, every path into $u$ has already been considered, so one pass suffices. A DAG cannot contain any cycle, so it certainly cannot contain a negative one.</details>

5. **Why is the negative-cycle check a separate pass rather than a condition inside the main loop?**
   <details><summary>Answer</summary>Because during the $V-1$ rounds, a successful relaxation is completely normal — it is the algorithm working. A distance improving on round 3 of a legitimate graph is indistinguishable from one improving because of a cycle. The <i>only</i> signal is that improvement is still possible <b>after</b> $V-1$ rounds, by which point every genuine shortest path has been found. The position of the check is what gives it meaning.</details>

---

## 9. Practice — independent task

Implement `analyse(graph, source)` returning shortest paths **or** an explicit negative cycle.

**Return** a dict with `"dist"`, `"parent"`, `"has_negative_cycle"`, and `"cycle"` — an actual list of vertices forming a negative cycle, or `None`.

**Part 1 — the basics.** Implement Bellman–Ford with early termination and the extra detection pass. Verify it against the lab's trap graph.

**Part 2 — recover the cycle.** When detection fires, note the vertex `v` relaxed in the extra pass, then follow `parent` back $V$ times. **Explain in a comment why $V$ steps guarantees you are on the cycle rather than merely near it.** Then walk forward until you revisit a vertex; that segment is the cycle. Assert its weights sum to a negative number.

**Part 3 — only reachable cycles.** Build a graph with a negative cycle in a component the source cannot reach. Your `has_negative_cycle` must be `False` — the distances from this source are all well-defined. Show a version without the guard reporting `True`, and explain the difference.

**Part 4 — cross-check.** For graphs with no negative edges, assert your distances match [[02-dijkstra|Dijkstra]] exactly on at least 200 random graphs. For graphs with negative edges and no negative cycle, assert they match a brute-force search over all simple paths on small graphs ($V \le 7$).

**Part 5 — arbitrage.** Given a table of currency exchange rates, build the graph with weight $-\log(\text{rate})$ and use your detector to find a profitable cycle. **Verify the profit independently** by multiplying the actual rates round the cycle and checking the product exceeds 1.

**Edge cases:** a single vertex; an unreachable vertex (distance stays infinite); a self-loop with negative weight (a cycle of length 1); parallel edges of different weights; a zero-weight cycle, which is **not** a negative cycle and must not be reported.

**Done when:** all cross-checks pass; your recovered cycle really sums negative and really is a cycle; the unreachable-cycle case returns `False`; the zero-weight cycle returns `False`; and your arbitrage profit is confirmed by multiplying raw rates.

---

## Before moving on

You can explain Dijkstra's failure in terms of finalisation, derive the $V-1$ bound from the maximum length of a simple path, detect a negative cycle with one extra pass, and say why detection rather than repair is the only sensible response.

**Recap:** Bellman–Ford relaxes **every edge, $V-1$ times**, with no finalisation and no priority queue — which is exactly why negative weights do not break it. The bound is $V-1$ because a shortest path in a graph with no negative cycle is simple, and a simple path has at most $V-1$ edges; a bad edge ordering really does need all of them, while a good one can finish in a single round. One **extra pass** detects reachable negative cycles: if anything still relaxes, some distance is falling forever, and the shortest path is undefined rather than merely unknown. Cost is $O(VE)$ against Dijkstra's $O(E\log V)$ — a factor of $V$ bought for correctness. On a **DAG**, do neither: relax in topological order for $O(V+E)$ with any weights. Negative weights only make sense on directed graphs.

**Next:** [[04-floyd-warshall|Floyd–Warshall]] — the same problem for *every* pair of vertices at once, in three lines, and the cleanest dynamic program in the subject.

---

## Related

- [[02-dijkstra|Dijkstra's Algorithm]] — faster, and wrong here
- [[04-floyd-warshall|Floyd–Warshall]] — all pairs, and negative-cycle detection on the diagonal
- [[01-topological-sort|Topological Sort]] — the $O(V+E)$ answer when the graph is acyclic
- [[02-breadth-first-search|BFS]] — the answer when the weights are all equal
- [[02-paths-cycles-and-connectivity|Paths, Cycles and Connectivity]] — where directed cycle and DAG are defined
- [[04-representations|Representations]] — why this algorithm wants an edge list
- [[06-algorithms/index|the graph algorithms index]]

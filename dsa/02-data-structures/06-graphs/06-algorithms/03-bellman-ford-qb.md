# Bellman–Ford — Question Bank

Micro-questions over [[03-bellman-ford|the Bellman–Ford module]]. Answer in a full sentence before opening the toggle. Format explained in [[dsa/02-data-structures/01-arrays-qb|the arrays bank]].

---

## A. The wrong answer that looks right

**1. State Dijkstra's correctness assumption precisely.**

<details><summary>Answer</summary>

Once the closest unfinalised vertex is popped, its distance is final — because every other route would go through a vertex already further away, and **extending a path can only make it longer**.

</details>

**2. Which clause is the assumption, and when is it true?**

<details><summary>Answer</summary>

"Extending a path can only make it longer" — true **exactly when every edge weight is non-negative**.

</details>

**3. Trace the smallest graph that breaks Dijkstra: `S→A=1`, `S→B=5`, `A→C=2`, `B→C=-4`.**

<details><summary>Answer</summary>

Pop `S` (0): `A=1`, `B=5`. Pop `A` (1): `C=3`. Pop `C` (3) — **finalised at 3**. Pop `B` (5): relax `C` to $5-4=1$, better — **but `C` is finalised, so it is discarded.**

</details>

**4. What does Dijkstra report, and what is the truth?**

<details><summary>Answer</summary>

Dijkstra reports $C = 3$; the truth is $C = 1$ via $S \to B \to C$.

</details>

**5. Why does this lesson exist at all?**

<details><summary>Answer</summary>

**No exception is raised and no warning is printed.** You get a number that is 200% of the truth, and in production you would never know. Not because negative weights are common — because the failure is **silent**.

</details>

---

## B. Where negative weights come from

**6. Currency arbitrage — how does it become a graph problem?**

<details><summary>Answer</summary>

Take $-\log(\text{exchange rate})$ as the edge weight. A profitable trading cycle becomes a **negative cycle**, so finding arbitrage *is* negative-cycle detection.

</details>

**7. Give a mundane source of negative weights.**

<details><summary>Answer</summary>

Any cost that can be a rebate: toll roads with credits, energy recovered on a downhill leg, a delivery route that picks up a paying load partway.

</details>

**8. What are difference constraints?**

<details><summary>Answer</summary>

Systems of inequalities $x_j - x_i \le w$, which map directly onto a shortest-path problem with arbitrary-sign weights. It is how schedulers solve timing constraints.

</details>

**9. Where does Bellman–Ford appear inside another algorithm?**

<details><summary>Answer</summary>

**Johnson's algorithm** — it reweights a graph to remove negative edges so Dijkstra can be run many times, and uses Bellman–Ford once to compute the reweighting.

</details>

---

## C. The vocabulary

**10. What is relaxation, in code?**

<details><summary>Answer</summary>

```python
if dist[u] + w < dist[v]:
    dist[v] = dist[u] + w
```

Ask whether going via `u` beats the best route to `v` found so far; if so, record it.

</details>

**11. What is a round?**

<details><summary>Answer</summary>

Also a pass or iteration — one sweep in which **every edge in the graph** is relaxed once, in some order. Bellman–Ford performs $V-1$ of them.

</details>

**12. What is a negative cycle, and what does it do to the problem?**

<details><summary>Answer</summary>

A directed cycle whose weights sum to a negative number. You can lower a path's cost without limit by going round again, so **the shortest path does not merely become hard to find — it does not exist.**

</details>

**13. What is a *reachable* negative cycle, and why does the distinction matter?**

<details><summary>Answer</summary>

One you can actually get to from the source. A negative cycle in an unreachable part of the graph affects no distance from that source, and a careful implementation reports only reachable ones.

</details>

**14. What representation does Bellman–Ford want, and why?**

<details><summary>Answer</summary>

An **edge list** — a flat list of $(u, v, w)$ triples. It never asks "what are the neighbours of $u$?", so an adjacency list buys it nothing.

</details>

**15. What is early termination, and why is it valid?**

<details><summary>Answer</summary>

Stop once a full round changes nothing. If an entire pass improves no distance, no later pass can either — **the inputs to every comparison are unchanged**.

</details>

**16. What is the predecessor array for?**

<details><summary>Answer</summary>

Recording which vertex each distance came from, so you can recover an actual **path** rather than only its cost.

</details>

---

## D. The algorithm

**17. State Bellman–Ford in one sentence.**

<details><summary>Answer</summary>

Start with every distance at infinity except the source, then relax **every edge in the graph**, $V-1$ times over.

</details>

**18. What is conspicuously absent, and why does that matter?**

<details><summary>Answer</summary>

No priority queue, no visited set, **no finalisation** — and the absence of finalisation is precisely why it survives negative weights. A distance can improve right up to the last round.

</details>

**19. What does the `dist[u] != INF` guard prevent?**

<details><summary>Answer</summary>

Relaxing out of an **unreached** vertex. Without it, an unreachable `u` with a negative outgoing edge invents a finite distance for `v`. With floats you may get away with it; with a sentinel integer you will not.

</details>

**20. What is the extra pass after the $V-1$ rounds for?**

<details><summary>Answer</summary>

Negative-cycle detection: **any further improvement means a negative cycle**, because after $V-1$ rounds nothing should be improvable.

</details>

---

## E. Why exactly $V-1$ rounds

**21. State the invariant.**

<details><summary>Answer</summary>

After $k$ rounds, every vertex reachable by a shortest path of at most $k$ edges has its **final** distance.

</details>

**22. Why can a shortest path use at most $V-1$ edges?**

<details><summary>Answer</summary>

A path with $V$ edges visits $V+1$ vertices, so by pigeonhole it repeats one — it contains a cycle. With no negative cycle, removing that cycle cannot increase the cost, so a **simple** shortest path always exists, and a simple path uses at most $V-1$ edges.

</details>

**23. Why does one round extend the guarantee by one edge?**

<details><summary>Answer</summary>

If the shortest path to $v$ is $s \to \dots \to u \to v$ with $k$ edges and `dist[u]` is final after $k-1$ rounds, then round $k$ relaxes **every** edge including $u \to v$, so `dist[v]` becomes at most `dist[u] + w` — the shortest-path value. Induction does the rest.

</details>

**24. What does the argument deliberately *not* assume?**

<details><summary>Answer</summary>

**The order of edges within a round.** That is why the bound is $V-1$ and not smaller — a bad order makes progress one edge at a time.

</details>

**25. Show the worst case on a 5-vertex chain.**

<details><summary>Answer</summary>

Relaxing `v0→v1→v2→v3→v4` in **reverse** order advances exactly one vertex per round: after round 1 only `v1`, after round 2 only `v2`, and so on. The same graph in a sensible order converges in a **single** round.

</details>

**26. So what is $V-1$ actually a statement about?**

<details><summary>Answer</summary>

**A guarantee about the worst edge ordering**, not a description of every run — which is why early termination is worth having.

</details>

---

## F. Negative cycles

**27. Add `C → B` with weight $-1$ to the trap graph. What should `dist[B]` be?**

<details><summary>Answer</summary>

There is **no correct value**. $B \to C \to B$ costs $-5$; go round twice and save 10. There is no lower bound, so $\text{dist}[B] = -\infty$, and every vertex reachable *from* the cycle inherits the problem.

</details>

**28. State the honest framing.**

<details><summary>Answer</summary>

**"Shortest path" is undefined here — not expensive, not hard, undefined.**

</details>

**29. What should you do when you detect one?**

<details><summary>Answer</summary>

**Detect and report** — never clamp to a finite value. And if the domain allows it (arbitrage), **the cycle itself is the answer you wanted**.

</details>

**30. Distinguish a negative edge from a negative cycle.**

<details><summary>Answer</summary>

Negative **edges** are fine and Bellman–Ford handles them exactly. Only negative **cycles** make the problem undefined. A DAG can have every edge negative and still have well-defined shortest paths.

</details>

**31. Can Bellman–Ford handle negative weights in an *undirected* graph?**

<details><summary>Answer</summary>

No — and the question is not about the algorithm. An undirected edge of weight $-3$ can be traversed back and forth for $-6$, $-9$, …, so **any negative edge in an undirected graph is automatically a negative cycle**. Negative weights only make sense on directed graphs.

</details>

---

## G. Choosing between the three

**32. Complete the table: cost, correctness condition, negative-cycle detection.**

<details><summary>Answer</summary>

| Algorithm | Cost | Correct when | Detects negative cycles |
| :--- | :--- | :--- | :--- |
| BFS | $O(V+E)$ | all weights equal | — |
| Dijkstra | $O(E\log V)$ | no negative weights | no |
| Bellman–Ford | $O(V \cdot E)$ | **any** weights | **yes** |

</details>

**33. What factor are you paying, concretely?**

<details><summary>Answer</summary>

$V$. On 10,000 vertices and 50,000 edges: Dijkstra ≈ $7 \times 10^5$ units of work, Bellman–Ford $5 \times 10^8$. **Milliseconds versus minutes** — which is why nobody uses Bellman–Ford when Dijkstra is valid.

</details>

**34. What is SPFA, and what is the trap in quoting it?**

<details><summary>Answer</summary>

Bellman–Ford with a queue of vertices whose distance changed, so you only relax edges out of those. Much faster in practice — but **the same $O(VE)$ worst case**, with adversarial graphs built specifically to defeat it. Never quote it as an asymptotic improvement.

</details>

**35. What is the right answer on a DAG?**

<details><summary>Answer</summary>

Neither. Relax edges in [[01-topological-sort|topological order]] and you get shortest paths in $O(V+E)$ with **any** weights, negative included — because a topological order guarantees you never need to revisit.

</details>

---

## H. Traps

**36. Why is "the weights are probably fine, use Dijkstra" the worst pitfall?**

<details><summary>Answer</summary>

If a weight *can* be negative, Dijkstra is not a fast approximation — it is an **incorrect algorithm that returns a confident number**. Check the sign constraint; do not assume it.

</details>

**37. What do the distances mean if you skip the extra pass?**

<details><summary>Answer</summary>

Nothing reliable. **The extra pass is what distinguishes "these are shortest paths" from "these are how far the algorithm got".**

</details>

**38. Summarise Bellman–Ford in one sentence.**

<details><summary>Answer</summary>

Relax every edge $V-1$ times and never finalise anything — slower than Dijkstra by a factor of $V$, and the price of correctness under negative weights plus a cycle detector for free.

</details>

---

## Scorecard

| Pass | Date | Got it | Close | Blank | Questions missed |
| :--- | :--- | :----- | :---- | :---- | :--------------- |
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |

---

## Related

- [[03-bellman-ford|Bellman–Ford]] — the module
- [[02-dijkstra-qb|Dijkstra — Question Bank]] — the algorithm this one repairs
- [[04-floyd-warshall-qb|Floyd–Warshall — Question Bank]] — all pairs instead of one source

# Floyd–Warshall — Question Bank

Micro-questions over [[04-floyd-warshall|the Floyd–Warshall module]]. Answer in a full sentence before opening the toggle. Format explained in [[dsa/02-data-structures/01-arrays-qb|the arrays bank]].

---

## A. The all-pairs question

**1. Name four questions that are not about one source.**

<details><summary>Answer</summary>

1. The **diameter** of a network — the largest shortest-path distance between any two nodes.
2. A precomputed **routing table** answering queries in $O(1)$.
3. **Transitive closure** — which pairs are connected at all.
4. **Arbitrage detection** — is there a negative cycle.

</details>

**2. What is the obvious approach, and when is it right?**

<details><summary>Answer</summary>

Run a single-source algorithm $V$ times. For **sparse** graphs it is the right answer.

</details>

**3. What is Floyd–Warshall's completely different route?**

<details><summary>Answer</summary>

**It never thinks about paths at all.** It thinks about which vertices a path is *allowed to pass through*.

</details>

---

## B. The vocabulary

**4. What is the all-pairs shortest path problem?**

<details><summary>Answer</summary>

Computing the shortest distance between **every ordered pair** of vertices — a $V \times V$ table rather than a single array.

</details>

**5. What is an intermediate vertex?**

<details><summary>Answer</summary>

A vertex a path passes *through* — neither its start nor its end. In $A \to B \to C \to D$ the intermediates are $B$ and $C$. **This is the concept the entire algorithm is organised around.**

</details>

**6. What is the distance matrix, and what does it start and end as?**

<details><summary>Answer</summary>

$d[i][j]$ — the best known cost from $i$ to $j$. It **starts as the adjacency matrix** (direct edges only) and **ends as the true shortest distances**.

</details>

**7. What is the `next` matrix?**

<details><summary>Answer</summary>

Also the successor matrix — `next[i][j]` is the first vertex to move to when travelling from $i$ towards $j$ along the best route. It is how you recover an actual path from a table of costs.

</details>

**8. What is round $k$, precisely?**

<details><summary>Answer</summary>

One pass of the outer loop, during which vertex $k$ becomes newly permitted as an intermediate. **After round $k$, $d[i][j]$ holds the shortest path using only the first $k$ vertices as intermediates.**

</details>

**9. What is transitive closure, and what is that variant called?**

<details><summary>Answer</summary>

The table of which vertices are reachable from which, ignoring cost. It is Floyd–Warshall with $\min$ replaced by `or` and $+$ by `and` — called **Warshall's algorithm**.

</details>

---

## C. The idea

**10. State the reframing that makes the algorithm obvious.**

<details><summary>Answer</summary>

Do not ask "what is the shortest path from $i$ to $j$?" Ask **"what is the shortest path from $i$ to $j$ that is only allowed to pass through vertices from some permitted set?"**

</details>

**11. What is the base case, and why is it free?**

<details><summary>Answer</summary>

The permitted set is **empty**, so the only routes are direct edges — the answer is just the adjacency matrix.

</details>

**12. When you permit one more vertex $k$, what are the only two possibilities?**

<details><summary>Answer</summary>

The best route either **does not use $k$** (unchanged from before), or **does use $k$** — going $i \to k \to j$, where **both halves are already solved** because they use only previously permitted intermediates.

</details>

**13. Write the recurrence.**

<details><summary>Answer</summary>

$$d_k[i][j] = \min\bigl(d_{k-1}[i][j],\; d_{k-1}[i][k] + d_{k-1}[k][j]\bigr)$$

</details>

**14. Say the recurrence in words.**

<details><summary>Answer</summary>

The shortest path allowed to use the first $k$ vertices is either the one that ignores $k$ entirely, or **the best route into $k$ followed by the best route out of it**.

</details>

**15. Write the whole algorithm.**

<details><summary>Answer</summary>

```python
for k in vertices:
    for i in vertices:
        for j in vertices:
            if d[i][k] + d[k][j] < d[i][j]:
                d[i][j] = d[i][k] + d[k][j]
                nxt[i][j] = nxt[i][k]
```

</details>

**16. Why is considering each $k$ exactly once enough?**

<details><summary>Answer</summary>

Revisiting a vertex means the path contains a cycle, and (absent negative cycles) removing that cycle never lengthens it. So a **simple** shortest path always exists, and a simple path uses each vertex at most once as an intermediate.

</details>

**17. What is striking about how it finds a three-edge path like $B \to C \to D \to A$?**

<details><summary>Answer</summary>

It finds it **without ever enumerating a path**. It composes it from two halves, each itself composed from halves.

</details>

**18. How do you recover the actual route?**

<details><summary>Answer</summary>

One extra line on improvement: `nxt[i][j] = nxt[i][k]` — the first step from $i$ is whatever the first step towards $k$ was. Then walk by repeatedly setting `i = nxt[i][j]` until `i == j`.

</details>

---

## D. The loop order

**19. Does the algorithm still work if you swap $i$ outermost and $k$ innermost?**

<details><summary>Answer</summary>

**No — and this is the single most important thing in the lesson.**

</details>

**20. What exactly does the outer $k$ loop guarantee?**

<details><summary>Answer</summary>

That when you consider routing through $k$, the values $d[i][k]$ and $d[k][j]$ are **already final with respect to all previously permitted intermediates** — because round $k$ begins only after round $k-1$ has finished for every pair.

</details>

**21. What goes wrong with $k$ on the inside?**

<details><summary>Answer</summary>

You use $d[i][k]$ before $d[i][k]$ has itself been improved. The result is an **overestimate** — a real path, but not the shortest one.

</details>

**22. How often is the wrong order actually wrong?**

<details><summary>Answer</summary>

On **105 of 200** random graphs in the lab. Not a corner case — wrong most of the time. It survives in people's memory because on small or nearly-complete graphs it often coincidentally agrees.

</details>

---

## E. Negative cycles

**23. What does $d[v][v]$ start at, and what does it mean if it goes negative?**

<details><summary>Answer</summary>

It starts at **0** — the cost of going nowhere. It can only go negative if there is a route that leaves $v$, comes back, and costs less than nothing.

</details>

**24. State the detection rule.**

<details><summary>Answer</summary>

**A negative cycle exists iff some $d[v][v] < 0$ after the algorithm finishes.** One scan of the diagonal, $O(V)$, no extra pass.

</details>

**25. What is true of the off-diagonal numbers when a negative cycle exists?**

<details><summary>Answer</summary>

They are **meaningless** — detect and report, do not use. As with Bellman–Ford.

</details>

**26. What caution do textbooks gloss over here?**

<details><summary>Answer</summary>

With a negative cycle present, the $O(V^3)$ loop can propagate arbitrarily negative values, and with floating-point weights this can reach $-\infty$ or produce `nan`. **Detect the cycle and stop**, rather than handing the matrix downstream.

</details>

---

## F. Choosing

**27. Compare Floyd–Warshall with $V$ Dijkstras across six rows.**

<details><summary>Answer</summary>

| | Floyd–Warshall | $V \times$ Dijkstra |
| :--- | :--- | :--- |
| Cost | $\Theta(V^3)$ always | $O(VE\log V)$ |
| Negative weights | **yes** | no |
| Negative cycle detection | yes, diagonal | no |
| Space | $\Theta(V^2)$ | $\Theta(V^2)$ output |
| Lines of code | ~5 | ~20 |
| Best when | dense, small $V$ | sparse |

</details>

**28. State the rule of thumb.**

<details><summary>Answer</summary>

If $E$ is close to $V^2$, use Floyd–Warshall. If $E$ is closer to $V$, run Dijkstra $V$ times.

</details>

**29. At $V = 1000$, $E = 5000$, what is the gap?**

<details><summary>Answer</summary>

Floyd–Warshall does $10^9$ operations; $V$ Dijkstras do about $7 \times 10^7$ — **about 14× slower**, and worsening as the graph grows.

</details>

**30. Negative weights, sparse graph, all pairs needed — what is the right answer?**

<details><summary>Answer</summary>

**Johnson's algorithm**: one Bellman–Ford run to reweight every edge non-negative, then $V$ Dijkstras on the reweighted graph. $O(VE\log V)$ with negative weights allowed.

</details>

**31. What is Floyd–Warshall's real practical niche?**

<details><summary>Answer</summary>

**Small dense graphs**, where its five lines beat twenty lines of Dijkstra on engineering time. $V^3$ caps you at a few thousand vertices — at $V=5000$ that is $1.25 \times 10^{11}$ operations.

</details>

---

## G. The operator family

**32. Why do other operator pairs work in the same triple loop?**

<details><summary>Answer</summary>

Any pair of operators forming a **semiring**, where one distributes over the other, works identically.

</details>

**33. Give the operator table.**

<details><summary>Answer</summary>

| Problem | Combine paths | Combine edges | Start |
| :--- | :--- | :--- | :--- |
| Shortest path | $\min$ | $+$ | $\infty$ |
| Transitive closure | `or` | `and` | `False` |
| Widest path / bottleneck | $\max$ | $\min$ | $-\infty$ |
| Most reliable path | $\max$ | $\times$ | 0 |
| Counting paths | $+$ | $\times$ | 0 |

</details>

**34. Why is recognising the family worth more than the shortest-path version?**

<details><summary>Answer</summary>

Because "shortest" is only one of the questions it answers — the same five lines solve reachability, bottleneck, reliability and path counting.

</details>

---

## H. Traps

**35. What must the diagonal be initialised to, and what breaks otherwise?**

<details><summary>Answer</summary>

**0.** Start it at infinity and the negative-cycle test never fires, and self-loops get misread.

</details>

**36. How do you handle parallel edges when building the matrix?**

<details><summary>Answer</summary>

Keep the **minimum**. Overwriting blindly means the last one in the list wins, which may not be the cheapest.

</details>

**37. What is the `INF + INF` trap?**

<details><summary>Answer</summary>

Fine with `float("inf")`. With a large integer sentinel like $10^9$, adding two gives $2\times10^9$ — which may overflow a fixed-width int in C++ or Java, **wrap to negative, and look like a shortest path**. Guard with `if d[i][k] != INF and d[k][j] != INF`.

</details>

**38. How do you use it on an undirected graph?**

<details><summary>Answer</summary>

Insert **both** directions when building the matrix — and remember an undirected negative edge is automatically a negative cycle.

</details>

**39. Summarise Floyd–Warshall in one sentence.**

<details><summary>Answer</summary>

Permit one more intermediate vertex per round and take the best of "route ignores it" versus "route goes through it" — five lines, $\Theta(V^3)$, and only correct with $k$ on the outside.

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

- [[04-floyd-warshall|Floyd–Warshall]] — the module
- [[03-bellman-ford-qb|Bellman–Ford — Question Bank]] — single source with negative weights
- [[02-dijkstra-qb|Dijkstra — Question Bank]] — the sparse alternative, run $V$ times

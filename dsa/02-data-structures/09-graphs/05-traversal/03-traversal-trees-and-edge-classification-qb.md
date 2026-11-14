# Traversal Trees & Edge Classification — Question Bank

Micro-questions over [[03-traversal-trees-and-edge-classification|the edge classification module]]. Answer in a full sentence before opening the toggle. Format explained in [[dsa/02-data-structures/01-arrays-qb|the arrays bank]].

---

## A. Why this exists

**1. What question motivates the whole lesson?**

<details><summary>Answer</summary>

"Build A needs B, B needs C, C needs A — is this build order possible?" How does a program *find* the cycle without checking all $V!$ orderings?

</details>

**2. State the naive cycle rule, and why it is wrong.**

<details><summary>Answer</summary>

"Run DFS, and if you ever meet an already-visited vertex, there is a cycle." Wrong: on $A \to B \to D$, $A \to C \to D$ there is no cycle at all, but `C → D` meets a visited vertex. `A → C → D` is simply a second route to `D`.

</details>

**3. State the core observation of the lesson in one line.**

<details><summary>Answer</summary>

**"Already visited" is one bit, and one bit is not enough** — record not just *whether* you visited a vertex, but *when you arrived and when you left*.

</details>

**4. What two different situations does a visited set merge?**

<details><summary>Answer</summary>

"Already visited and **finished**" (the search left it and came back out) versus "already visited and **still on the current path**". Only the second is a cycle.

</details>

---

## B. The vocabulary

**5. What is a traversal tree?**

<details><summary>Answer</summary>

The subgraph made of exactly the edges the traversal used to reach each vertex **for the first time**. Every vertex except the start is reached by exactly one such edge, so they form a tree.

</details>

**6. What is a traversal forest?**

<details><summary>Answer</summary>

What you get when one traversal cannot reach everything: you start a fresh search from an unvisited vertex, growing a second tree. The collection is a forest.

</details>

**7. What shape is a DFS tree, and why?**

<details><summary>Answer</summary>

Long and narrow, because DFS keeps descending.

</details>

**8. What shape is a BFS tree, and what is its special property?**

<details><summary>Answer</summary>

Short and wide. Every root-to-vertex path in it is a **shortest path** in the original graph, measured in edges. Hence its other name: the shortest-path tree.

</details>

**9. What is discovery time $d[v]$?**

<details><summary>Answer</summary>

The counter value at the moment the search first arrives at $v$ and colours it grey. Also called entry or arrival time.

</details>

**10. What is finish time $f[v]$?**

<details><summary>Answer</summary>

The counter value at the moment the search has examined every edge out of $v$ and leaves it for good. Also called exit or departure time.

</details>

**11. Define ancestor in traversal-tree terms.**

<details><summary>Answer</summary>

A vertex on the traversal-tree path from the root down to another. If `u` is an ancestor of `x`, the search entered `u`, and had not yet left `u`, when it entered `x`.

</details>

**12. Is a vertex its own ancestor?**

<details><summary>Answer</summary>

Yes — trivially both its own ancestor and its own descendant. This is why a self-loop counts as a back edge.

</details>

**13. Define the four edge kinds.**

<details><summary>Answer</summary>

**Tree edge** — used to reach a previously unvisited vertex.
**Back edge** — points to one of the vertex's own ancestors.
**Forward edge** — points to a descendant reached by some other, longer route first.
**Cross edge** — joins two vertices where neither is an ancestor of the other.

</details>

**14. Explain the white/grey/black scheme.**

<details><summary>Answer</summary>

**White** = not yet discovered. **Grey** = discovered but not finished, i.e. currently on the recursion stack. **Black** = finished. A visited set merges grey and black into one bit, which was the whole problem.

</details>

---

## C. The clock

**15. When does the counter tick, and what does it end at?**

<details><summary>Answer</summary>

On **entering** a vertex and on **leaving** it. With $V$ vertices it ends at $2V$, because every vertex is entered once and left once.

</details>

**16. Write the running example's timeline as brackets.**

<details><summary>Answer</summary>

```
 1   2   3   4   5   6   7   8    9   10   11   12
 (u  (v  (y  (x  x)  y)  v)  u)   (w  (z   z)   w)
```

</details>

**17. What do you notice about the intervals?**

<details><summary>Answer</summary>

**They nest.** $x[4,5] \subset y[3,6] \subset v[2,7] \subset u[1,8]$, and $w[9,12]$ is entirely disjoint from all of them.

</details>

---

## D. The parenthesis theorem

**18. State the parenthesis theorem in words.**

<details><summary>Answer</summary>

For any two vertices, their discovery/finish intervals are either **completely nested** or **completely disjoint** — never partially overlapping. And nesting is exactly ancestry.

</details>

**19. State it symbolically.**

<details><summary>Answer</summary>

$$\text{$u$ is an ancestor of $x$} \iff d[u] < d[x] < f[x] < f[u]$$

</details>

**20. Why must it be true?**

<details><summary>Answer</summary>

The search leaves a vertex only after every edge out of it has been examined, which means the whole search below has already returned. If it enters `x` while still inside `u`, it cannot leave `u` until it has left `x`. **The call stack physically prevents interleaving** — the same reason you cannot close a function call before closing the calls it made.

</details>

**21. What does the theorem buy you computationally?**

<details><summary>Answer</summary>

Ancestry becomes a **constant-time test** — two integer comparisons, not a walk up the tree.

</details>

---

## E. Classifying an edge

**22. Give the three-line classification rule for edge $u \to v$.**

<details><summary>Answer</summary>

1. `v` white → **tree edge** (discovered through this edge).
2. `v` grey → **back edge** (the search is currently inside `v`, so `v` is an ancestor of `u`).
3. `v` black → **forward** if $d[u] < d[v]$ (`v` is a descendant), else **cross**.

</details>

**23. Why is every edge guaranteed to land in exactly one category?**

<details><summary>Answer</summary>

Because the three rules are exhaustive over the three possible colours, and a vertex has exactly one colour when the edge is examined.

</details>

**24. In the running example, classify `x → v` and justify with timestamps.**

<details><summary>Answer</summary>

**Back edge.** `v` is grey, and $d[v]{=}2 < d[x]{=}4 < f[x]{=}5 < f[v]{=}7$ — `v`'s interval contains `x`'s, so `v` is an ancestor.

</details>

**25. Classify `u → x` and `w → y`.**

<details><summary>Answer</summary>

`u → x`: **forward** — `x` is black and $d[u]{=}1 < d[x]{=}4$, so `x` is below `u`.
`w → y`: **cross** — `y` is black and $d[y]{=}3 < d[w]{=}9$, so `y` belongs to an earlier, different tree.

</details>

**26. What kind of edge is a self-loop?**

<details><summary>Answer</summary>

A **back edge** — a vertex is its own ancestor. It is a cycle of length one.

</details>

---

## F. Back edges and cycles

**27. Prove: if DFS finds a back edge, the graph has a directed cycle.**

<details><summary>Answer</summary>

A back edge $u \to v$ means `v` is an ancestor of `u`, so there is a path of tree edges $v \rightsquigarrow u$. Append the back edge and you have a closed directed walk returning to `v` — a directed cycle.

</details>

**28. Prove the converse: if the graph has a directed cycle, DFS finds a back edge.**

<details><summary>Answer</summary>

Let `v` be the vertex of cycle $C$ that DFS discovers **first**. Every other vertex of $C$ is reachable from `v` along $C$ and is white at that moment, so all become descendants of `v` before `v` finishes. In particular the vertex `p` pointing into `v` along the cycle is a descendant, and when edge $p \to v$ is examined `v` is still grey — a back edge.

</details>

**29. State the combined theorem.**

<details><summary>Answer</summary>

**A directed graph is a DAG if and only if a DFS over it produces no back edges.**

</details>

**30. What does that theorem justify?**

<details><summary>Answer</summary>

The correctness of DFS-based [[../06-algorithms/01-topological-sort|topological sort]] — and it is why that algorithm gets cycle detection **for free** rather than as an extra pass.

</details>

---

## G. Undirected graphs

**31. Which edge kinds can an undirected DFS produce?**

<details><summary>Answer</summary>

Only **tree edges and back edges**. Forward and cross edges cannot occur.

</details>

**32. Why can a forward or cross edge not occur?**

<details><summary>Answer</summary>

An undirected edge is seen from whichever end the search reaches first, and that end defines the classification. If `v` is not white when examined from grey `u`, it cannot have **finished** — finishing `v` would have required examining this very edge from `v`'s side, which would have discovered `u`. So `v` is grey, and the edge is a back edge.

</details>

**33. Say it as a slogan.**

<details><summary>Answer</summary>

A forward edge would be an edge to a descendant the search "missed" on the way down — **and in an undirected graph there is no way to miss it.**

</details>

**34. What trap does this create for cycle detection?**

<details><summary>Answer</summary>

Every child sees its parent as grey, so a naive "grey neighbour means cycle" reports a cycle on **every edge of every graph**, including a two-vertex graph with one edge.

</details>

**35. What is the fix, and what is the subtlety in the fix?**

<details><summary>Answer</summary>

Ignore the edge you arrived on — and ignore it **by edge identity, not by vertex**. Skipping by vertex also silently drops parallel edges, which genuinely are a two-edge cycle.

</details>

---

## H. What BFS leaves behind

**36. State the BFS level property.**

<details><summary>Answer</summary>

**Every edge of the graph joins two vertices whose BFS levels differ by at most one.**

</details>

**37. Why can no neighbour of a level-$k$ vertex be at level $k+2$?**

<details><summary>Answer</summary>

Every neighbour of `u` is discovered no later than the moment `u` is dequeued, so it would have been reached from `u` at level $k+1$ first. By symmetry it cannot be at $k-2$ either.

</details>

**38. What is the first consequence?**

<details><summary>Answer</summary>

It is the shortest-path guarantee restated: the level of `v` **is** the minimum number of edges from the source — which is why BFS and not DFS answers "fewest hops".

</details>

**39. What is the second consequence — the bipartiteness test?**

<details><summary>Answer</summary>

Colour each level alternately. Every edge either crosses consecutive levels (fine) or joins two vertices **within** one level. An edge inside a level is an odd cycle, and an odd cycle is exactly what stops a graph being bipartite. So: BFS, then check for any edge with both endpoints on the same level.

</details>

**40. Does DFS have an equivalent depth bound?**

<details><summary>Answer</summary>

No. A DFS tree on a path graph of 5,000 vertices is 5,000 levels deep — exactly the depth that kills the recursive implementation.

</details>

---

## I. Facts versus accidents

**41. Which edge count is invariant when you change the start vertex?**

<details><summary>Answer</summary>

The **back-edge** count — more precisely, *whether at least one back edge exists*. Back edges correspond to cycles, and cycles are a property of the graph.

</details>

**42. Which counts are not invariant, and why?**

<details><summary>Answer</summary>

The **forward/cross split**. Starting at `w` instead of `u` turns one forward + one cross into two cross edges. Forward and cross are artefacts of where you started and what order you listed neighbours — they describe *this traversal*, not the graph.

</details>

**43. What do the real algorithms actually use?**

<details><summary>Answer</summary>

| Algorithm | Uses |
| :--- | :--- |
| Directed cycle detection | does any back edge exist |
| Topological sort (DFS) | decreasing **finish time** |
| Kosaraju's SCC | decreasing finish time, then DFS on the reversed graph |
| Tarjan's SCC | discovery times plus lowest-reachable-discovery-time |
| Bridges / articulation points | lowest discovery time reachable via one back edge |
| Bipartite check | BFS levels — no edge within a level |

</details>

**44. What is the pattern across that table?**

<details><summary>Answer</summary>

**Discovery time, finish time, and back edges.** Learn those three and the rest of the graph-algorithm catalogue stops looking like a list of unrelated tricks.

</details>

---

## J. Traps

**45. What is the symptom of using a visited set where you need three colours?**

<details><summary>Answer</summary>

A dependency resolver that rejects a perfectly valid build — cycles reported that do not exist.

</details>

**46. Why is $f[v]$ not simply "the order I finished in"?**

<details><summary>Answer</summary>

It is a comparable number whose **relative** ordering encodes ancestry. Sorting by decreasing $f$ is a topological order; sorting by increasing $d$ is not.

</details>

**47. Can you do this classification with BFS?**

<details><summary>Answer</summary>

BFS on a directed graph does produce non-tree edges, but they do not correspond to ancestry in the same way, and **there is no parenthesis theorem for BFS because there is no nesting**. If a problem talks about back edges, it means DFS.

</details>

**48. What goes wrong if you special-case and skip `u == v`?**

<details><summary>Answer</summary>

Self-loops are back edges and cycles of length one. Skipping them silently declares cyclic graphs acyclic.

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

- [[03-traversal-trees-and-edge-classification|Traversal Trees & Edge Classification]] — the module
- [[01-depth-first-search-qb|Depth-First Search — Question Bank]]
- [[../06-algorithms/01-topological-sort|Topological Sort]] — the algorithm this lesson proves correct

# A\* Search — Question Bank

Micro-questions over [[05-a-star|the A\* module]]. Answer in a full sentence before opening the toggle. Format explained in [[dsa/02-data-structures/01-arrays-qb|the arrays bank]].

---

## A. Why it exists

**1. What is wrong with Dijkstra's direction of travel?**

<details><summary>Answer</summary>

It expands in order of distance from the **source** and has no concept of a destination, so it grows a circle outward in every direction — including directly away from where you want to go.

</details>

**2. Give the London–Edinburgh illustration.**

<details><summary>Answer</summary>

Dijkstra settles every town in Cornwall first, because they are closer to London than Edinburgh is. No shortest path to Edinburgh passes through Cornwall, and a human looking at a map knows it instantly.

</details>

**3. What does the human have that Dijkstra does not?**

<details><summary>Answer</summary>

**An estimate.** Straight-line distance is not the true road distance, but it is never *more* than it — and that turns out to be exactly the property needed.

</details>

**4. What did the lab measure on a 368-cell grid?**

<details><summary>Answer</summary>

Same optimal cost of 37 in all cases: zero heuristic (Dijkstra) expanded 360 cells (97.8%), Euclidean 260 (70.7%), Manhattan 233 (63.3%) — and with tie-breaking, 38 cells (~10%).

</details>

---

## B. The vocabulary

**5. What is $g(n)$?**

<details><summary>Answer</summary>

The **cost so far** — the best route found from start to $n$. A known, exact quantity about the past; the same number Dijkstra keeps.

</details>

**6. What is $h(n)$?**

<details><summary>Answer</summary>

The **heuristic** — an estimate of the remaining cost from $n$ to the goal. A guess about the future, supplied by you, and **the only new ingredient**.

</details>

**7. What is $f(n)$, and what does keying on it mean?**

<details><summary>Answer</summary>

$f(n) = g(n) + h(n)$, the estimated total cost of the best route through $n$. **A\* is exactly Dijkstra with the priority queue keyed on $f$ instead of $g$** — that single substitution is the whole algorithm.

</details>

**8. Define admissible.**

<details><summary>Answer</summary>

$h(n) \le$ the true remaining cost, for every $n$ — **never overestimates**. An admissible heuristic is *optimistic*: it may promise a shortcut that does not exist, but it never warns you off a route that is actually good.

</details>

**9. Define consistent.**

<details><summary>Answer</summary>

Also monotone — $h(n) \le \text{cost}(n, n') + h(n')$ for every edge, with $h(\text{goal}) = 0$. The estimate may drop by at most the cost of the step you take.

</details>

**10. How do admissible and consistent relate?**

<details><summary>Answer</summary>

**Consistency is strictly stronger.** Every consistent heuristic is admissible; not the reverse.

</details>

**11. What are the open and closed sets?**

<details><summary>Answer</summary>

**Open** (frontier/fringe): discovered but not yet expanded — in practice the priority queue. **Closed** (expanded/visited): already popped and processed.

</details>

**12. What does "expanding a node" mean, and why is the expansion count the standard measure?**

<details><summary>Answer</summary>

Removing it from the open set and generating its successors. The count is **proportional to real work and independent of the machine**.

</details>

**13. What is greedy best-first search?**

<details><summary>Answer</summary>

Keying the queue on $h$ alone, ignoring $g$. Fast and **not optimal**, because it never accounts for the cost already paid.

</details>

---

## C. The algorithm

**14. What single line differs from Dijkstra?**

<details><summary>Answer</summary>

The push: `heapq.heappush(pq, (ng + h(nb), nb))` instead of `(ng, nb)`.

</details>

**15. What happens if $h(n) = 0$ everywhere?**

<details><summary>Answer</summary>

It **is** Dijkstra, character for character — $f = g + 0 = g$. A\* is a strict generalisation, so "A\* versus Dijkstra" is better read as "A\* with a good $h$ versus A\* with $h = 0$".

</details>

**16. Why must the goal test happen on *pop* and not on *push*?**

<details><summary>Answer</summary>

The first time you **discover** the goal you may have an expensive route to it. The first time you **expand** it, its $f$ is the queue minimum, and since $h(\text{goal}) = 0$, $f = g$ — so $g$ is the true shortest distance.

</details>

**17. Why is the push-time test a nasty bug?**

<details><summary>Answer</summary>

It returns suboptimal paths, **usually right and occasionally wrong**, which makes it easy to miss in testing.

</details>

---

## D. The optimality proof

**18. State the optimality claim.**

<details><summary>Answer</summary>

If the heuristic never overestimates, then the first time A\* **expands** the goal, it has found the shortest path to it.

</details>

**19. Give the proof.**

<details><summary>Answer</summary>

Suppose A\* is about to expand the goal at $f = g = C$, and a shorter path of cost $C^* < C$ exists. That path has some node $n$ still open. Then
$$f(n) = g(n) + h(n) \le g(n) + \text{true remaining} = C^* < C$$
so $n$ has smaller $f$ and would have been popped first — contradiction.

</details>

**20. Which step is exactly admissibility?**

<details><summary>Answer</summary>

The middle inequality, $h(n) \le$ true remaining cost.

</details>

**21. What does the proof *not* require of $h$?**

<details><summary>Answer</summary>

Anything else. It can be wildly inaccurate, zero, or discontinuous — as long as it never promises the remaining journey is **longer** than it really is.

</details>

---

## E. What consistency buys

**22. What are the two things consistency gives you?**

<details><summary>Answer</summary>

1. **$f$ never decreases along a path.**
2. **A closed node never needs reopening.**

</details>

**23. What goes wrong with a merely-admissible, inconsistent heuristic?**

<details><summary>Answer</summary>

You can discover a cheaper route to an already-expanded node and must put it back in the open set — costing time and complicating the code.

</details>

**24. Answer the standard interview question: difference between admissible and consistent?**

<details><summary>Answer</summary>

**Admissible gives you the right answer; consistent gives you the right answer without reopening nodes.**

</details>

**25. Why is Manhattan admissible on a 4-connected unit-cost grid?**

<details><summary>Answer</summary>

With no walls it **is** the exact distance, and walls can only make the true distance longer. An estimate equal to the truth in the easiest case, where truth only grows from there, can never overestimate.

</details>

**26. Why is Manhattan inadmissible on an 8-connected grid?**

<details><summary>Answer</summary>

A single diagonal step costs 1, but Manhattan reports 2. **The heuristic must match the movement model** — this is the most common way people break A\* in practice.

</details>

---

## F. Choosing a heuristic

**27. Give the heuristic for each movement model.**

<details><summary>Answer</summary>

| Movement | Heuristic |
| :--- | :--- |
| 4-directional, unit cost | Manhattan $\lvert\Delta r\rvert + \lvert\Delta c\rvert$ |
| 8-directional, diagonals cost 1 | Chebyshev $\max(\lvert\Delta r\rvert, \lvert\Delta c\rvert)$ |
| 8-directional, diagonals $\sqrt2$ | Octile |
| Euclidean plane | straight-line distance |
| Road network | straight-line ÷ max speed |
| Sliding tile puzzle | sum of Manhattan distances |
| Anything | 0 (= Dijkstra) |

</details>

**28. State the design rule for inventing a heuristic.**

<details><summary>Answer</summary>

**Solve a *relaxed* version of your problem — one with constraints deleted — and use its exact answer.** A relaxed problem's optimum can never exceed the real optimum, so it is automatically admissible.

</details>

**29. Apply the rule to Manhattan and to the 15-puzzle.**

<details><summary>Answer</summary>

Manhattan is the exact answer to "this grid with the walls removed". Sum-of-Manhattan is the exact answer to "this puzzle if tiles could pass through each other".

</details>

**30. What does it mean for $h_1$ to *dominate* $h_2$?**

<details><summary>Answer</summary>

$h_1 \ge h_2$ everywhere, both admissible. **Dominating heuristics never expand more nodes** — which is why Manhattan (233) beats Euclidean (260) on a 4-connected grid, despite both being admissible.

</details>

---

## G. Weighted A\*

**31. What is weighted A\*?**

<details><summary>Answer</summary>

$f = g + w \cdot h$ for $w > 1$. Inflating $h$ makes the search greedier and faster, at the cost of optimality.

</details>

**32. Multiply an admissible heuristic by 3 — what changes, and in which direction?**

<details><summary>Answer</summary>

**Both change.** Expansions fall; path cost rises; optimality is lost.

</details>

**33. What is the formal promise?**

<details><summary>Answer</summary>

The path returned is at most $w$ times the optimal cost.

</details>

**34. At $w = 1.2$ the heuristic already overestimates at 14 cells, yet the path is still optimal. What does that teach?**

<details><summary>Answer</summary>

**Admissibility is sufficient for optimality, not necessary.** Breaking it means you have lost the *guarantee*, not necessarily the answer.

</details>

**35. Why does that make inadmissible heuristics dangerous?**

<details><summary>Answer</summary>

**They usually work, and then quietly do not.**

</details>

**36. When is the trade legitimate?**

<details><summary>Answer</summary>

Game pathfinding hundreds of units per frame will take a 10%-worse path for a 3× speedup — nobody can see the difference, everyone can see the frame drop.

</details>

---

## H. Tie-breaking

**37. What is a plateau, and why does a uniform grid create one?**

<details><summary>Answer</summary>

A large region of equal $f$ that A\* has no reason to prefer any part of. Every route of the same length through open ground has identical $f$.

</details>

**38. What did deliberate tie-breaking achieve in the lab?**

<details><summary>Answer</summary>

233 cells down to **38** — a 6× reduction — for the same optimal path, with nothing about the heuristic changed.

</details>

**39. Which way should ties be broken, and why?**

<details><summary>Answer</summary>

Prefer **larger $g$** (equivalently **smaller $h$**, since $f$ is constant on the plateau). Larger $g$ means further along the journey, so it drives the search down the plateau toward the goal instead of fanning out sideways.

</details>

**40. How do you implement it?**

<details><summary>Answer</summary>

Make the priority a tuple: `(f, h, counter, node)`. Python compares on $f$ first and only consults later elements on a tie.

</details>

**41. What is the `counter` element for?**

<details><summary>Answer</summary>

**Not decoration** — it guarantees a total order so the heap never tries to compare node objects themselves, which may not be orderable. It also makes runs reproducible.

</details>

**42. Name two further standard tie-breaking techniques.**

<details><summary>Answer</summary>

1. Scale $h$ by $1+\varepsilon$ for tiny $\varepsilon$ (around $1/\text{path length}$) — bounded optimality loss, often negligible.
2. Add a tiny cross-product term preferring nodes near the straight start–goal line — standard in games, where path aesthetics matter.

</details>

---

## I. The family

**43. Complete the table: what the queue key decides.**

<details><summary>Answer</summary>

| Key | Algorithm | Optimal? |
| :--- | :--- | :--- |
| $g$ | Dijkstra / uniform-cost | yes |
| $g$, equal costs | BFS | yes |
| $h$ | greedy best-first | **no** |
| $g + h$ | A\* | yes, if $h$ admissible |
| $g + w h$ | weighted A\* | within factor $w$ |

</details>

**44. Why is greedy best-first the instructive failure?**

<details><summary>Answer</summary>

Ignoring $g$, it will happily walk a 500-step route that looks like it heads the right way over a 20-step route that starts by moving away. **$g$ is what keeps the search honest about what has already been spent.**

</details>

---

## J. Traps

**45. What is the mixing-units trap?**

<details><summary>Answer</summary>

If $g$ is in seconds and $h$ in metres, $f$ is meaningless. Straight-line distance is admissible for a *time* cost only after dividing by the maximum possible speed.

</details>

**46. When should you not use A\* at all?**

<details><summary>Answer</summary>

For all-pairs (use [[04-floyd-warshall|Floyd–Warshall]]) or one-source-to-everything (plain [[02-dijkstra|Dijkstra]] — the heuristic buys nothing without a single target).

</details>

**47. Does A\* work with negative edge weights?**

<details><summary>Answer</summary>

No. It inherits Dijkstra's finalisation and therefore Dijkstra's failure. **No heuristic repairs this** — use [[03-bellman-ford|Bellman–Ford]].

</details>

**48. What do you get from a weak heuristic?**

<details><summary>Answer</summary>

Dijkstra, plus the cost of the machinery. **Measure expansions, not intentions.**

</details>

**49. Summarise A\* in one sentence.**

<details><summary>Answer</summary>

Dijkstra with the queue keyed on cost-so-far plus an optimistic estimate of cost-remaining — optimal whenever the estimate never overestimates, and faster in proportion to how good the estimate is.

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

- [[05-a-star|A\* Search]] — the module
- [[02-dijkstra-qb|Dijkstra — Question Bank]] — A\* with $h = 0$
- [[03-bellman-ford-qb|Bellman–Ford — Question Bank]] — what no heuristic can fix

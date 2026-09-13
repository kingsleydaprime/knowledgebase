# Greedy Algorithms

**Take the locally best option and never look back — when that is provably enough, and when it quietly is not.**

Two lessons, written to [[COURSE-STANDARD|the course standard]]. The first establishes the conditions and the classic trap; the second works the selection-and-scheduling family that interviews reach for most.

> **The one idea:** a greedy algorithm always produces an answer, fast, and the answer is often right. **That is exactly what makes it dangerous** — when the greedy choice is not safe, you get a plausible wrong number rather than a failure. The technique is not "try greedy and see"; it is "find the key, then prove it".

## The lessons

1. [[01-when-greedy-works|When Greedy Works]] — **[Intermediate]** — what makes a greedy choice safe; the greedy-choice property and optimal substructure; the coin-change trap, where $\{1,3,4\}$ at amount 6 defeats the obvious rule; a provably correct greedy worked in full with its exchange argument; and the greedy-versus-DP decision guide.
2. [[02-selection-and-scheduling|Selection and Scheduling]] — **[Intermediate → Advanced]** — the **hire-K-workers** cost problem, where a group's cost is a product rather than a sum and the cheapest-looking candidates are usually wrong; interval scheduling and why only the **end time** is a valid sort key; "select the most" versus "cover them all"; and the exchange argument written out properly.

## The template, and its limit

**Almost every greedy in this course is: sort by one key, then sweep once.**

| Problem | Sort by | Then |
| :--- | :--- | :--- |
| Hire K workers | wage/quality ratio | max-heap of $k$ qualities |
| Most non-overlapping meetings | end time | take if it starts after the last end |
| Fewest rooms | time, ends before starts | running count, track the peak |
| [[06-minimum-spanning-tree\|MST]] (Kruskal) | edge weight | [[10-union-find\|union-find]] |
| Coin change $\{1,3,4\}$ | — no key works — | [[06-dynamic-programming/index\|dynamic programming]] |

**The last row is the whole reason lesson 01 comes first.** Finding the key is the insight; proving it with an **exchange argument** — take any optimal solution, swap in the greedy's first choice, show it is still valid and no worse — is what separates an algorithm from a guess.

## Greedy or dynamic programming?

| | Greedy | [[06-dynamic-programming/index\|Dynamic programming]] |
| :--- | :--- | :--- |
| Decides | once, irrevocably | by trying every option |
| Needs | the greedy-choice property, **proved** | overlapping subproblems + optimal substructure |
| Cost | usually $O(n\log n)$ | usually states × transition |
| When wrong | silently returns a worse answer | — |

**Both need optimal substructure. Only greedy needs the extra claim that a local rule picks the right subproblem** — which is precisely the claim that fails for coin change, and precisely what an exchange argument establishes when it holds.

## What is verified

Every lab was executed and its expected output generated from that run. **Every greedy in lesson 02 is checked against exhaustive search rather than demonstrated:**

| Lesson | What the lab demonstrates |
| :--- | :--- |
| [[01-when-greedy-works\|when greedy works]] | greedy coin change failing on $\{1,3,4\}$ and $\{1,7,10\}$, and 0/1 knapsack failing on the rule that is optimal for the fractional version |
| [[02-selection-and-scheduling\|selection and scheduling]] | hire-K greedy agreeing with brute force **400/400** while "take the K cheapest wages" is wrong on **130/400**; earliest-start and shortest-duration each failing on one input and tying on another; interval scheduling and the room sweep each **300/300** |

## Related

- [[03-algorithms/index|03-algorithms]] — the parent folder
- [[06-dynamic-programming/index|Dynamic Programming]] — the fallback when no greedy key exists
- [[06-minimum-spanning-tree|Minimum Spanning Tree]] — the template applied to a graph
- [[08-heaps|Heaps]] · [[10-union-find|Union-Find]] — the two structures these lean on
- [[08-overlapping-intervals|Overlapping intervals]] · [[07-top-k-elements|Top-K elements]] — the pattern layer above

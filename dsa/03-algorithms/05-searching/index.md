# Searching

**Finding a thing.** The word covers two genuinely different activities, and keeping them apart is most of what this folder is for.

1. **Searching a collection.** You have a container of values and you want one of them. The question is how few elements you can get away with looking at. Answer: all of them if the data is unordered, and $\log n$ of them if it is sorted. This is linear and binary search.
2. **Searching a space.** There is no container. There is a starting *state*, a rule for generating the states reachable from it, and a goal test — and the "collection" is generated as you go, is usually enormous, and may be infinite. Chess positions, puzzle configurations, route planning, and every [[06-graphs/04-representations|implicit graph]] are this. The question is not "how few elements" but "which state to expand next".

Both are called search. Only the second one has a frontier, a heuristic, or a reason to care about tie-breaking.

## The lessons

1. [[01-linear-and-binary-search|Linear and Binary Search]] — **[Beginner → Intermediate]** — the $O(n)$ fallback and the $O(\log n)$ payoff for sorting first; Python's `bisect`; the three classic binary-search bugs, each demonstrated failing, including the overflow that sat in the JDK for nine years.
2. [[02-binary-search-on-the-answer|Binary Search on the Answer]] — **[Intermediate]** — the move that makes binary search apply where there is no sorted array in sight: search the space of possible **answers**, using a monotone predicate as the comparison. Both templates, why they round the midpoint differently, and how to prove monotonicity before trusting it.
3. [[03-state-space-search|State-Space Search]] — **[Intermediate → Advanced]** — the general frame: states, successors, the frontier, the explored set, duplicate detection, cost functions, heuristics and tie-breaking. **One search function; the frontier's container selects the algorithm** — and tree search costs 60× more than graph search by depth 10.

## How the searches relate

| Strategy | Frontier is a... | Finds |
| :--- | :--- | :--- |
| Linear search | — (no frontier; just a scan) | any match, $O(n)$ |
| Binary search | — (halving an interval) | a match in a **sorted** collection, $O(\log n)$ |
| [[02-breadth-first-search\|BFS]] | queue | fewest **edges** |
| [[01-depth-first-search\|DFS]] | stack | *some* path, cheaply in memory |
| Uniform-cost / [[02-dijkstra\|Dijkstra]] | min-heap on cost-so-far $g$ | lowest **cost** |
| Greedy best-first | min-heap on estimate-to-goal $h$ | fast, but not necessarily the best |
| A\* | min-heap on $f = g + h$ | lowest cost, expanding fewer nodes than Dijkstra |

**Read down the last four rows and only one thing changes: what the priority queue is keyed on.** That is the payoff of treating these as one family rather than five algorithms.

## Related

- [[04-sorting/index|Sorting]] — what you do first to make binary search possible, and when that trade pays
- [[05-traversal/index|Graph traversal]] — BFS and DFS, the uninformed search strategies
- [[06-algorithms/index|Graph algorithms]] — Dijkstra and A\*, the informed ones
- [[09-modified-binary-search|Modified binary search]] — the pattern layer above lessons 01 and 02
- [[05-a-star|A\*]] — the informed strategy of lesson 03, in full
- [[03-algorithms/index|03-algorithms]] — the parent folder

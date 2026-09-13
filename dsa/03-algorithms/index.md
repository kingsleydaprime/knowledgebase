# Algorithms

**Procedures that operate on data**, as opposed to the ways of storing it in [[02-data-structures/index|02-data-structures]].

> **The filing rule, and its one exception.** If a note is about *storing*, it is a structure; if it is about *doing*, it is an algorithm. The exception is that **an algorithm which belongs to exactly one structure is filed with that structure**, because keeping it next to the vocabulary it assumes is what makes it readable. Two families have moved out of this folder on that basis:
>
> - **Tree traversal** — pre-, in-, post- and level-order — lives in [[04-traversal/index|02-data-structures/05-trees/04-traversal/]].
> - **Graph traversal** (DFS, BFS, edge classification) lives in [[05-traversal/index|06-graphs/05-traversal/]], and **graph algorithms** (topological sort, Dijkstra, MST, and the shortest-path family) live in [[06-algorithms/index|06-graphs/06-algorithms/]].
>
> What remains here is everything that is *not* the property of a single structure: the measuring system, the general problem-solving techniques, and the number and bit work.

## Reading order

### The foundation — read this before any data structure

1. [[01-complexity-analysis/index|Complexity Analysis]] — **[Beginner → Intermediate]** — a folder. $O$, $\Omega$ and $\Theta$ and why they are not interchangeable; best, average and worst case; recurrences and the Master Theorem; amortised analysis and the three methods for doing it.

Everything in this course is quoted in the vocabulary that folder establishes, so it genuinely comes first — right after [[01-loops-and-what-they-cost|loops and what they cost]].

### Recursion and the techniques built on it

2. **Recursion** — *not yet written* — base cases, recursive cases, the call stack, problem decomposition, recursion trees, and memoisation as the bridge to dynamic programming.
3. **Divide and Conquer** — *not yet written* — split, solve, combine; why merge sort, quicksort and binary search are all one idea; and the recurrence shape it always produces.

### Sorting and searching

4. [[04-sorting/index|Sorting]] — **[Beginner → Advanced]** — a folder: the $\Omega(n\log n)$ lower bound and what it actually forbids, the elementary sorts, merge, quick, and the non-comparison sorts (counting, radix, bucket) that beat the bound by not comparing.
5. [[05-searching/index|Searching]] — **[Beginner → Intermediate]** — a folder: linear and binary search over a collection, binary search on the answer, and state-space search — the frontier, the explored set, heuristics and tie-breaking.

### Techniques

6. **Dynamic Programming** — *not yet written* — a folder: overlapping subproblems, optimal substructure, state definition, transition, memoisation and tabulation, and the classic one- and two-dimensional recurrences.
7. [[10-greedy-algorithms|Greedy Algorithms]] — **[Intermediate]** — when taking the locally best choice is provably right, and a lab where it is not: coin change failing on $\{1,3,4\}$, and 0/1 knapsack failing on the rule that is optimal for the fractional version.
8. [[09-max-slice-algorithms|Max Slice]] — **[Intermediate]** — Kadane's algorithm and the maximum-subarray family.
9. [[08-leader-algorithm|Leader / Majority]] — **[Intermediate]** — Boyer–Moore voting in $O(1)$ space.

### Number and bit work

10. [[07-number-theory-basics|Number Theory Basics]] — **[Intermediate]** — primes, sieves, GCD, modular arithmetic.
11. [[11-bit-manipulation|Bit Manipulation]] — **[Intermediate]** — masks, shifts, and the tricks worth recognising.
12. [[12-math-and-geometry|Math and Geometry]] — **[Intermediate]** — matrix rotation, spiral traversal, coordinate reasoning.

## What lives elsewhere, and where

| If you are looking for | Go to |
| :--- | :--- |
| Pre-, in-, post-order, level-order on a tree | [[04-traversal/index\|05-trees/04-traversal/]] |
| DFS, BFS, edge classification | [[05-traversal/index\|06-graphs/05-traversal/]] |
| Topological sort, Dijkstra, MST, shortest paths, A\* | [[06-algorithms/index\|06-graphs/06-algorithms/]] |
| Backtracking, sliding window, two pointers, and the other recognition patterns | [[04-patterns/index\|04-patterns/]] |

## How these pair with the structures

| Algorithm | Wants |
| :--- | :--- |
| Counting / radix sort | arrays as buckets |
| Merge sort | a scratch array of size $n$ |
| Quicksort | the call stack, $O(\log n)$ deep if you recurse on the smaller side |
| Binary search | a **sorted** random-access container |
| Dynamic programming | a table, or a memo dictionary |
| Sieve of Eratosthenes | a boolean array of size $n$ |

## What is verified

**Every finished note in this folder follows [[COURSE-STANDARD|the course standard]]**, alongside [[02-data-structures/index|02-data-structures]] and [[04-patterns/index|04-patterns]]: stated prerequisites, observable outcomes, a runnable lab whose expected output was generated from an actual run, practice with a *done when*, and a demonstrable finish line.

Several labs exist to **break** the algorithm rather than to show it working:

| Lesson | What the lab demonstrates |
| :--- | :--- |
| [[01-growth-and-asymptotic-notation\|complexity]] | the ratio per doubling *is* the complexity — 2.00x for $O(n)$, 4.01x for $O(n^2)$ — and growing an array by one instead of doubling makes append $O(n)$ |
| [[01-linear-and-binary-search\|searching]] | all three classic binary-search bugs failing: an infinite loop, a missed single element, and the JDK's nine-year overflow |
| [[08-leader-algorithm\|leader]] | the voting phase confidently returning a candidate that is not a majority |
| [[09-max-slice-algorithms\|max slice]] | `max(0, ...)` Kadane's answering a different question on all-negative input |
| [[10-greedy-algorithms\|greedy]] | greedy coin change failing on $\{1,3,4\}$ and $\{1,7,10\}$, and 0/1 knapsack failing on the rule that is optimal for the fractional version |
| [[12-math-and-geometry\|geometry]] | float slopes calling three points collinear when exact integer cross products say otherwise |

Where a lab claims an output, that output came from executing the code.

## Related

- [[dsa/index|dsa/]] — the parent course and full reading order
- [[02-data-structures/index|02-data-structures]] — what these operate on
- [[04-patterns/index|04-patterns]] — the problem-recognition layer above both
- [[COURSE-STANDARD|Course standard]] — the shape the converted folders follow

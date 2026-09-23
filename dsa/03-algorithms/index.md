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

1. [[01-complexity-analysis/index|Complexity Analysis]] — **[Beginner → Intermediate]** — a folder. $O$, $\Omega$ and $\Theta$ and why they are not interchangeable; best, average and worst case; space complexity; and **amortised analysis with all three methods** — aggregate, accounting and potential.

Everything in this course is quoted in the vocabulary that folder establishes, so it genuinely comes first — right after [[01-loops-and-what-they-cost|loops and what they cost]].

### Recursion and the techniques built on it

2. [[02-recursion/index|Recursion]] — **[Beginner → Advanced]** — a folder: the three questions that produce a recursive function; the call stack and why space is the depth; **recursion trees and recurrence relations**; and **the Master Theorem**, including the two famous recurrences it cannot solve.
3. [[03-divide-and-conquer|Divide and Conquer]] — **[Intermediate]** — split, solve, combine, and **why the combine step is the whole algorithm**; choosing $a$, $b$ and $f$ deliberately; why reducing the number of subproblems changes the *exponent* (Karatsuba, Strassen) while a cheaper combine changes at most a log factor; and a case where the technique applies and is still the wrong tool.

### Sorting and searching

4. [[04-sorting/index|Sorting]] — **[Beginner → Advanced]** — a folder: the $\Omega(n\log n)$ lower bound and what it actually forbids, the elementary sorts, merge, quick, and the non-comparison sorts (counting, radix, bucket) that beat the bound by not comparing.
5. [[05-searching/index|Searching]] — **[Beginner → Intermediate]** — a folder: linear and binary search over a collection, binary search on the answer, and state-space search — the frontier, the explored set, heuristics and tie-breaking.

### Techniques

6. [[06-dynamic-programming/index|Dynamic Programming]] — **[Intermediate → Advanced]** — a folder: the two properties that make DP apply (both *measured*, not asserted); state, transition and base case; memoisation versus tabulation and why the transition dictates the fill order; space optimisation; and the classic one- and two-dimensional problems with reconstruction.
7. [[10-greedy-algorithms/index|Greedy Algorithms]] — **[Intermediate → Advanced]** — a folder: when the locally best choice is provably right and the exchange argument that proves it; the coin-change trap; and the **selection and scheduling** family — hire-K-workers, where a group's cost is a product rather than a sum, and interval scheduling, where only one of three plausible sort keys is correct.
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
| [[02-amortized-analysis\|amortised analysis]] | a charge of **2** per append going into debt at $-510$ while a charge of 3 never does; and the potential function holding the amortised cost at a flat 3 while actual costs run 1, 2, 3, 1, 5 |
| [[01-recursion-fundamentals\|recursion]] | `getrecursionlimit()` reporting 1,000 while only **996** frames are usable; and naive Fibonacci making 242,785 calls for **26** distinct subproblems |
| [[03-the-master-theorem\|Master Theorem]] | the $n\log n$ gap case measuring doubling ratios of 2.55/2.49/2.44 — distinguishable from the wrong Case-3 answer by the numbers alone |
| [[03-divide-and-conquer\|divide and conquer]] | the $O(n\log n)$ max-subarray solution losing to Kadane's linear scan by ~20x at $n=64{,}000$ — applicable is not optimal |
| [[02-binary-search-on-the-answer\|binary search on the answer]] | the floor/ceil midpoint bug hanging at `hi == lo + 1`, and 300 random instances cross-checked against linear scan |
| [[03-state-space-search\|state-space search]] | tree search costing **60x** graph search by solution depth 10, because the state space is finite while the search tree is not |
| [[02-selection-and-scheduling\|greedy selection]] | hire-K greedy agreeing with brute force **400/400** while "take the K cheapest wages" is wrong on **130/400**; two plausible interval sort keys each failing on one input and tying on another |
| [[06-dynamic-programming/index\|dynamic programming]] | a reversed fill order returning **0** instead of 34 with no error; the rolling knapsack's upward loop returning **15** where the answer is 5; and merge sort's subproblem redundancy measured at exactly 1.0x |
| [[01-linear-and-binary-search\|searching]] | all three classic binary-search bugs failing: an infinite loop, a missed single element, and the JDK's nine-year overflow |
| [[08-leader-algorithm\|leader]] | the voting phase confidently returning a candidate that is not a majority |
| [[09-max-slice-algorithms\|max slice]] | `max(0, ...)` Kadane's answering a different question on all-negative input |
| [[01-when-greedy-works\|greedy]] | greedy coin change failing on $\{1,3,4\}$ and $\{1,7,10\}$, and 0/1 knapsack failing on the rule that is optimal for the fractional version |
| [[12-math-and-geometry\|geometry]] | float slopes calling three points collinear when exact integer cross products say otherwise |

Where a lab claims an output, that output came from executing the code.

## Question banks

One bank per lesson: micro-questions with the answers hidden behind toggles, for closed-book recall rather than reading. Method explained in [[dsa/02-data-structures/01-arrays-qb|the arrays bank]].

- [[03-divide-and-conquer-qb|Divide and Conquer]]
- [[07-number-theory-basics-qb|Number Theory Basics]]
- [[08-leader-algorithm-qb|The Leader Algorithm]]
- [[09-max-slice-algorithms-qb|Max Slice Algorithms]]
- [[11-bit-manipulation-qb|Bit Manipulation]]
- [[12-math-and-geometry-qb|Math & Geometry]]
- [[01-complexity-analysis/index|Complexity Analysis]] — banks for that folder's lessons
- [[02-recursion/index|Recursion]] — banks for that folder's lessons
- [[04-sorting/index|Sorting]] — banks for that folder's lessons
- [[05-searching/index|Searching]] — banks for that folder's lessons
- [[06-dynamic-programming/index|Dynamic Programming]] — banks for that folder's lessons
- [[10-greedy-algorithms/index|Greedy Algorithms]] — banks for that folder's lessons

---

## Related

- [[dsa/index|dsa/]] — the parent course and full reading order
- [[02-data-structures/index|02-data-structures]] — what these operate on
- [[04-patterns/index|04-patterns]] — the problem-recognition layer above both
- [[COURSE-STANDARD|Course standard]] — the shape the converted folders follow

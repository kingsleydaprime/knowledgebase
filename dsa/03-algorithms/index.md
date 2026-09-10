# Algorithms

**Procedures that operate on data**, as opposed to the ways of storing it in [[02-data-structures/index|02-data-structures]]. The rule for where a note goes: if it *stores*, it is a structure; if it *does*, it is an algorithm.

> **Read `01-algorithms` second**, right after [[01-loops-and-what-they-cost|loops and what they cost]] and before any data structure. Complexity analysis is the vocabulary every other note here is written in, and it sits in this folder only for filing reasons.

## Reading order

### The foundation

1. [[01-algorithms|Algorithms and Complexity Analysis]] — **[Beginner → Intermediate]** — $O$, $\Omega$ and $\Theta$ and why they are not interchangeable; best, average and worst case; amortised analysis

### Traversal — the two that everything else builds on

2. [[02-dfs|Depth-First Search]] — **[Intermediate]** — go deep, backtrack; the recursion and the explicit-stack forms; cycle detection colours
3. [[03-bfs|Breadth-First Search]] — **[Intermediate]** — go wide by level; why it gives shortest paths on unweighted graphs

### Sorting and searching

4. [[04-sorting/index|Sorting]] — **[Beginner → Advanced]** — a folder: the $\Omega(n\log n)$ lower bound, the elementary sorts, merge, quick, and the non-comparison sorts that beat the bound
5. [[05-searching|Searching]] — **[Beginner → Intermediate]** — linear, binary, and searching on the answer

### Graph algorithms

6. [[06-dijkstra|Dijkstra's Algorithm]] — **[Advanced]** — shortest paths with non-negative weights; BFS plus a [[08-heaps|min-heap]]
7. [[11-topological-sort|Topological Sort]] — **[Intermediate]** — ordering a DAG; Kahn's algorithm and the DFS variant
8. [[12-minimum-spanning-tree|Minimum Spanning Tree]] — **[Advanced]** — Prim's and Kruskal's, and why one wants a heap and the other a [[10-union-find|union-find]]

### Techniques

9. [[10-greedy-algorithms|Greedy Algorithms]] — **[Intermediate]** — when taking the locally best choice is provably right, and when it is not
10. [[09-max-slice-algorithms|Max Slice]] — **[Intermediate]** — Kadane's algorithm and the maximum-subarray family
11. [[08-leader-algorithm|Leader / Majority]] — **[Intermediate]** — Boyer–Moore voting in $O(1)$ space

### Number and bit work

12. [[07-number-theory-basics|Number Theory Basics]] — **[Intermediate]** — primes, sieves, GCD, modular arithmetic
13. [[13-bit-manipulation|Bit Manipulation]] — **[Intermediate]** — masks, shifts, and the tricks worth recognising
14. [[14-math-and-geometry|Math and Geometry]] — **[Intermediate]** — matrix rotation, spiral traversal, coordinate reasoning

## How these pair with the structures

| Algorithm | Wants |
| :--- | :--- |
| BFS | a [[07-stacks-and-queues|queue]] |
| DFS | a [[07-stacks-and-queues|stack]], or the call stack |
| Dijkstra, Prim | a [[08-heaps|min-heap]] |
| Kruskal | a sorted [[06-graphs/04-representations|edge list]] plus [[10-union-find|union-find]] |
| Topological sort | in-degree counts over an [[06-graphs/04-representations|adjacency list]] |
| Counting / radix sort | arrays as buckets |

## An honest note on this folder

**[[02-data-structures/index|02-data-structures]], [[04-patterns/index|04-patterns]] and the sorting folder here have been converted to [[COURSE-STANDARD|the course standard]]; the remaining notes in this folder have not.** They are accurate and useful, but they do not yet carry the full shape — stated prerequisites, observable outcomes, a verified runnable lab, practice with a *done when*. Converting them is tracked in [[BUILD-PLAN|the build plan]].

Where a note here has a runnable example, that example has been executed. Where it does not, it is prose and a complexity table.

## Related

- [[index|dsa/]] — the parent course and full reading order
- [[02-data-structures/index|02-data-structures]] — what these operate on
- [[04-patterns/index|04-patterns]] — the problem-recognition layer above both
- [[COURSE-STANDARD|Course standard]] — the shape the converted folders follow

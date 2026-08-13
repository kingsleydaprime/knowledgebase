# Data Structures & Algorithms

A map of the DSA notes in this folder, in the order they're meant to be read — each one builds on ideas from the notes before it. These are the *concepts*; the `pdfs/` folder alongside this one holds the original course material (Codility-style exercises on iterations, arrays, sorting, primes, dynamic programming, etc.) that these notes complement rather than replace.

## Structure

```
dsa/
├── 01-iterations.md, 02-data-types.md, 03-data-type-classification.md   # foundations
├── neetcode-150/
│   ├── README.md                # index: all 150 problems by topic → concept note + cheat-sheet
│   ├── interview-playbook.md    # UMPIRE process + reading constraints/complexity for the approach
│   └── questions/               # flat 001–150, each problem solved extensively
├── 04-data-structures/
│   ├── arrays, dynamic-arrays, hash-maps, linked-lists, graphs, stacks-and-queues
│   ├── heaps, tries, union-find
│   └── trees/
│       ├── trees.md
│       └── traversal.md        # companion note — tree traversal orders
├── 05-algorithms/
│   ├── algorithms.md            # Big-O, complexity analysis
│   ├── dfs, bfs, sorting, searching, dijkstra
│   ├── number-theory-basics, leader-algorithm, max-slice-algorithms, greedy-algorithms
│   └── topological-sort, minimum-spanning-tree, bit-manipulation, math-and-geometry
└── 06-patterns/                 # LeetCode patterns — a layer above both, see below
```

After cross-referencing this folder against the original Codility course PDFs in `pdfs/`, five notes were added for topics that had zero coverage anywhere: [[foundations/dsa/04-data-structures/07-stacks-and-queues|stacks-and-queues]], [[foundations/dsa/05-algorithms/07-number-theory-basics|number-theory-basics]] (GCD, primality, Sieve of Eratosthenes), [[foundations/dsa/05-algorithms/08-leader-algorithm|leader-algorithm]] (majority element / Boyer-Moore voting), [[foundations/dsa/05-algorithms/09-max-slice-algorithms|max-slice-algorithms]] (Kadane's algorithm), and [[foundations/dsa/05-algorithms/10-greedy-algorithms|greedy-algorithms]]. A few existing notes also picked up real depth from the same review: non-comparison sorts in [[foundations/dsa/05-algorithms/04-sorting|sorting]], the "guess expected complexity from constraint size" heuristic in [[foundations/dsa/05-algorithms/01-algorithms|algorithms]], and "binary search on the answer" in [[foundations/dsa/06-patterns/09-modified-binary-search|modified-binary-search]].

The rule for where a note goes: if it's a way of *storing* data, it's under `data-structures/` (with a further subfolder if that structure has its own companion notes, the way trees has traversal). If it's a *procedure* that operates on data structures — including ones that don't belong to just one structure, like Dijkstra working across a weighted graph — it's under `algorithms/`.

## Reading order

Tags mark roughly where each note sits on a Beginner → Advanced curve, within this folder specifically — useful for pacing yourself, not a strict gate (a "Beginner" tag just means "assumes the least prior context here").

**Foundations**
1. [[02-data-types|data-types]] — **[Beginner]** — what a type actually is, at the bit level
2. [[03-data-type-classification|data-type-classification]] — **[Beginner]** — primitive/composite, value/reference, mutable/immutable, static/dynamic, strong/weak

**Data structures**
3. [[01-arrays|arrays]] — **[Beginner]** — contiguous memory, O(1) indexing
4. [[02-dynamic-arrays|dynamic-arrays]] — **[Beginner]** — resizable arrays, amortized O(1) append
5. [[03-hash-maps|hash-maps]] — **[Beginner]** — hashing, collisions, average O(1) lookup
6. [[04-linked-lists|linked-lists]] — **[Intermediate]** — pointer-based sequences, O(1) insert/delete at a known node
7. [[01-trees|trees]] — **[Intermediate]** — hierarchical structures, BSTs, balance
   - [[02-traversal|traversal]] — **[Intermediate]** — visiting every node, pre/in/post/level-order (companion note, tree-specific)
8. [[06-graphs|graphs]] — **[Intermediate]** — the general case: vertices, edges, adjacency representations
9. [[foundations/dsa/04-data-structures/07-stacks-and-queues|stacks-and-queues]] — **[Beginner]** — LIFO/FIFO, array-based push/pop, the circular buffer trick
10. [[foundations/dsa/04-data-structures/08-heaps|heaps]] — **[Intermediate]** — priority queues, complete-tree-in-an-array, O(n) heapify, the two-heap median trick
11. [[foundations/dsa/04-data-structures/09-tries|tries]] — **[Intermediate]** — prefix trees, O(L) prefix queries a hash map can't do, trie + grid backtracking
12. [[foundations/dsa/04-data-structures/10-union-find|union-find]] — **[Advanced]** — disjoint sets, path compression + union by rank → O(α(n)), cycle detection

**Algorithms**
13. [[01-algorithms|algorithms]] — **[Beginner]** — what an algorithm is, Big-O, complexity analysis
14. [[02-dfs|dfs]] — **[Intermediate]** — depth-first search
15. [[03-bfs|bfs]] — **[Intermediate]** — breadth-first search
16. [[04-sorting|sorting]] — **[Intermediate]** — bubble/insertion/merge/quicksort, stability, Timsort, counting sort
17. [[05-searching|searching]] — **[Beginner]** — linear vs binary search
18. [[06-dijkstra|dijkstra]] — **[Advanced]** — shortest path in weighted graphs, BFS generalized with a min-heap
19. [[foundations/dsa/05-algorithms/07-number-theory-basics|number-theory-basics]] — **[Intermediate]** — primality testing, Sieve of Eratosthenes, factorization, GCD/LCM
20. [[foundations/dsa/05-algorithms/08-leader-algorithm|leader-algorithm]] — **[Intermediate]** — majority element via Boyer-Moore voting
21. [[foundations/dsa/05-algorithms/09-max-slice-algorithms|max-slice-algorithms]] — **[Intermediate]** — Kadane's algorithm, maximum subarray sum
22. [[foundations/dsa/05-algorithms/10-greedy-algorithms|greedy-algorithms]] — **[Advanced]** — locally-optimal choices, and why they aren't always globally correct
23. [[foundations/dsa/05-algorithms/11-topological-sort|topological-sort]] — **[Intermediate]** — ordering a DAG (Kahn's / DFS post-order), doubling as cycle detection
24. [[foundations/dsa/05-algorithms/12-minimum-spanning-tree|minimum-spanning-tree]] — **[Advanced]** — Prim's (heap) and Kruskal's (union-find), the cut property
25. [[foundations/dsa/05-algorithms/13-bit-manipulation|bit-manipulation]] — **[Intermediate]** — bitwise operators, XOR tricks, `x & (x-1)`, masks
26. [[foundations/dsa/05-algorithms/14-math-and-geometry|math-and-geometry]] — **[Intermediate]** — in-place matrix ops, fast exponentiation, grade-school arithmetic

Still unwritten and welcome here as standalone procedures: A*, Bellman-Ford, the KMP string match, and segment/Fenwick trees.

## Also already in this folder
- [[01-iterations|iterations]] — **[Beginner]** — for/while loop basics (Python)

## Next layer — LeetCode patterns

With the fundamentals above in place, [[foundations/dsa/06-patterns/README|patterns/]] covers the 15 reusable patterns that show up across problems — recognizing which pattern a problem is testing is most of the battle in an interview setting. Patterns sit above both `data-structures/` and `algorithms/` since most of them combine a structure with a procedure (e.g. a heap + a scanning pass for [[07-top-k-elements|top-k-elements]]).

## Putting it to work — NeetCode 150

[[foundations/dsa/neetcode-150/README|neetcode-150/]] holds all 150 problems from the [NeetCode 150](https://neetcode.io/practice) list — its README is the index (every problem → the concept note behind it, grouped by topic) and carries a **signal → tool** pattern cheat-sheet, and each problem is worked extensively in its own file in a flat `questions/` folder numbered 001–150 (**all 150 solved**). Start with the [[foundations/dsa/neetcode-150/interview-playbook|interview playbook]] for the meta-skill — the UMPIRE process (reword → clarify → examples → brute-force-then-optimize → code → test) and how to read a problem's constraints and stated complexity to guess the intended approach. Cross-referencing this folder against that list is what surfaced the gaps now filled by the [[foundations/dsa/04-data-structures/08-heaps|heaps]], [[foundations/dsa/04-data-structures/09-tries|tries]], [[foundations/dsa/04-data-structures/10-union-find|union-find]], [[foundations/dsa/05-algorithms/11-topological-sort|topological-sort]], [[foundations/dsa/05-algorithms/12-minimum-spanning-tree|MST]], [[foundations/dsa/05-algorithms/13-bit-manipulation|bit-manipulation]], and [[foundations/dsa/05-algorithms/14-math-and-geometry|math-and-geometry]] notes, plus the deeper 1-D/2-D worked recurrences in [[foundations/dsa/06-patterns/15-dynamic-programming|dynamic-programming]] — the same PDF-cross-reference methodology described above, applied to the interview-patterns layer.

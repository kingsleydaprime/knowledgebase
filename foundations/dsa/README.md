# Data Structures & Algorithms

A map of the DSA notes in this folder, in the order they're meant to be read — each one builds on ideas from the notes before it. These are the *concepts*; the `pdfs/` folder alongside this one holds the original course material (Codility-style exercises on iterations, arrays, sorting, primes, dynamic programming, etc.) that these notes complement rather than replace.

## Structure

```
dsa/
├── 01-iterations.md, 02-data-types.md, 03-data-type-classification.md   # foundations
├── 04-data-structures/
│   ├── arrays, dynamic-arrays, hash-maps, linked-lists, graphs, stacks-and-queues
│   └── trees/
│       ├── trees.md
│       └── traversal.md        # companion note — tree traversal orders
├── 05-algorithms/
│   ├── algorithms.md            # Big-O, complexity analysis
│   ├── dfs, bfs, sorting, searching, dijkstra
│   └── number-theory-basics, leader-algorithm, max-slice-algorithms, greedy-algorithms
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

**Algorithms**
10. [[01-algorithms|algorithms]] — **[Beginner]** — what an algorithm is, Big-O, complexity analysis
11. [[02-dfs|dfs]] — **[Intermediate]** — depth-first search
12. [[03-bfs|bfs]] — **[Intermediate]** — breadth-first search
13. [[04-sorting|sorting]] — **[Intermediate]** — bubble/insertion/merge/quicksort, stability, Timsort, counting sort
14. [[05-searching|searching]] — **[Beginner]** — linear vs binary search
15. [[06-dijkstra|dijkstra]] — **[Advanced]** — shortest path in weighted graphs, BFS generalized with a min-heap
16. [[foundations/dsa/05-algorithms/07-number-theory-basics|number-theory-basics]] — **[Intermediate]** — primality testing, Sieve of Eratosthenes, factorization, GCD/LCM
17. [[foundations/dsa/05-algorithms/08-leader-algorithm|leader-algorithm]] — **[Intermediate]** — majority element via Boyer-Moore voting
18. [[foundations/dsa/05-algorithms/09-max-slice-algorithms|max-slice-algorithms]] — **[Intermediate]** — Kadane's algorithm, maximum subarray sum
19. [[foundations/dsa/05-algorithms/10-greedy-algorithms|greedy-algorithms]] — **[Advanced]** — locally-optimal choices, and why they aren't always globally correct

More algorithms belong here as they're written up — A*, Union-Find, Bellman-Ford, topological sort as its own note, etc. — anything that's a standalone procedure rather than a way of storing data.

## Also already in this folder
- [[01-iterations|iterations]] — **[Beginner]** — for/while loop basics (Python)

## Next layer — LeetCode patterns

With the fundamentals above in place, [[foundations/dsa/06-patterns/README|patterns/]] covers the 15 reusable patterns that show up across problems — recognizing which pattern a problem is testing is most of the battle in an interview setting. Patterns sit above both `data-structures/` and `algorithms/` since most of them combine a structure with a procedure (e.g. a heap + a scanning pass for [[07-top-k-elements|top-k-elements]]).

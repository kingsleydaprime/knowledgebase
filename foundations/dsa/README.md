# Data Structures & Algorithms

A map of the DSA notes in this folder, in the order they're meant to be read — each one builds on ideas from the notes before it. These are the *concepts*; the `pdfs/` folder alongside this one holds the original course material (Codility-style exercises on iterations, arrays, sorting, primes, dynamic programming, etc.) that these notes complement rather than replace.

## Structure

```
dsa/
├── data-types.md, data-type-classification.md   # foundations — precede both of the below
├── data-structures/
│   ├── arrays.md, dynamic-arrays.md, hash-maps.md, linked-lists.md, graphs.md
│   └── trees/
│       ├── trees.md
│       └── traversal.md        # companion note — tree traversal orders
├── algorithms/
│   ├── algorithms.md            # Big-O, complexity analysis
│   ├── dfs.md, bfs.md, sorting.md, searching.md
│   └── (future: dijkstra.md, and other algorithms that don't belong to a single data structure)
└── patterns/                    # LeetCode patterns — a layer above both, see below
```

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

**Algorithms**
9. [[01-algorithms|algorithms]] — **[Beginner]** — what an algorithm is, Big-O, complexity analysis
10. [[02-dfs|dfs]] — **[Intermediate]** — depth-first search
11. [[03-bfs|bfs]] — **[Intermediate]** — breadth-first search
12. [[04-sorting|sorting]] — **[Intermediate]** — bubble/insertion/merge/quicksort, stability, Timsort
13. [[05-searching|searching]] — **[Beginner]** — linear vs binary search
14. [[06-dijkstra|dijkstra]] — **[Advanced]** — shortest path in weighted graphs, BFS generalized with a min-heap

More algorithms belong here as they're written up — A*, Union-Find, Bellman-Ford, topological sort as its own note, etc. — anything that's a standalone procedure rather than a way of storing data.

## Also already in this folder
- [[01-iterations|iterations]] — **[Beginner]** — for/while loop basics (Python)

## Next layer — LeetCode patterns

With the fundamentals above in place, [[foundations/dsa/06-patterns/README|patterns/]] covers the 15 reusable patterns that show up across problems — recognizing which pattern a problem is testing is most of the battle in an interview setting. Patterns sit above both `data-structures/` and `algorithms/` since most of them combine a structure with a procedure (e.g. a heap + a scanning pass for [[07-top-k-elements|top-k-elements]]).

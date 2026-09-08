# Data Structures & Algorithms

**How to store data, and how to operate on it without wasting time or memory.** The layer under every backend service, database query and rendering loop you'll ever write — and the one that interviews test directly.

**~39,900 words across 30 concept notes**, plus **~49,900 words** working all 150 problems in [[foundations/dsa/neetcode-150/README|neetcode-150/]]. `[reference]`.

> **The one idea:** every data structure is a **bet about which operation you'll do most**, paid for by making the others slower. An array buys O(1) indexing with O(n) insertion. A hash map buys O(1) lookup by destroying order. A heap buys O(1) access to the smallest by giving up on everything else. **There is no structure that is good at everything, and there cannot be one** — so the skill isn't memorising structures, it's recognising which operation your problem does in its inner loop, and picking the bet that makes *that* one cheap.

## What this is actually about

**A data structure is a decision about how to lay out data in memory.** That's it — memory is a flat, addressable line of bytes, and a data structure is a scheme for arranging your data along it, plus the rules for finding things again afterwards. Put elements side by side and you can compute any element's address instantly, but inserting means shifting everything after it. Scatter them and connect them with pointers and insertion is free, but finding the tenth element means walking past nine others. **Those two paragraphs are arrays and linked lists, and everything else in this folder is a more elaborate version of the same tradeoff.**

**An algorithm is a finite sequence of well-defined steps from input to output.** A recipe qualifies. What makes the subject non-trivial isn't finding *an* algorithm — brute force nearly always exists — it's that the obvious one is often unusably slow, and the gap is much wider than intuition suggests. Checking every pair in a million-element list is a trillion operations, about **11 days**. The right structure often takes the same problem to a fifth of a second. That gap, not elegance, is why this material exists.

The two halves are inseparable, which is why they're taught as one subject: **an algorithm's speed is usually determined by the structure it runs on**, not by how cleverly it's written. Dijkstra's algorithm is O(V²) with an array and O(E log V) with a heap — same algorithm, same code shape, different container. Choosing the structure *is* choosing the complexity.

### Why bother, when the library already has these?

You will almost never implement a hash map professionally. You will constantly **choose** one, and that choice is invisible in the code and decisive in production. Three things this material buys you that reaching for the default doesn't:

1. **Knowing which container to reach for**, and what it costs. The dict-versus-list decision is one character of diff and the difference between O(n) and O(n²).
2. **Reading your own code's performance** before it's in production, rather than after a customer reports a timeout.
3. **Recognising problem shapes.** "Find pairs summing to a target", "shortest route", "valid dependency order" are all solved problems, and knowing that is the difference between a twenty-minute task and a week of reinvention.

Interviews test it because it's the one body of knowledge shared across every specialism — and, less charitably, because it's easy to grade. That's a reason to be fluent, not a reason to pretend it's the whole of the job.

## Structure

```
dsa/
├── 01-loops-and-what-they-cost.md   # the on-ramp: counting iterations
├── 04-data-structures/
│   ├── arrays, dynamic-arrays, hash-maps, linked-lists, graphs, stacks-and-queues
│   ├── heaps, tries, union-find
│   └── 05-trees/  — trees.md + traversal.md
├── 05-algorithms/
│   ├── 01-algorithms.md          # complexity analysis — read this early
│   ├── dfs, bfs, sorting, searching, dijkstra
│   ├── number-theory-basics, leader-algorithm, max-slice-algorithms, greedy-algorithms
│   └── topological-sort, minimum-spanning-tree, bit-manipulation, math-and-geometry
├── 06-patterns/                     # the 15 LeetCode patterns — a layer above both
├── neetcode-150/                    # all 150 problems worked, + interview playbook
└── pdfs/                            # the original Codility course material
```

**The rule for where a note goes:** if it's a way of *storing* data, it's under `04-data-structures/` (with a subfolder when a structure has companion notes, as trees has traversal). If it's a *procedure* operating on data — including ones that don't belong to a single structure, like Dijkstra across a weighted graph — it's under `05-algorithms/`. Patterns sit above both, since most combine a structure with a procedure.

**Note on numbering:** the folder numbers order the *folders*; the reading order below is what actually matters and doesn't follow them exactly. Complexity analysis lives at `05-algorithms/01-algorithms.md` for filing reasons but should be read second.

## Reading order & University Course Approach

Every module in this folder is structured like a **University Course Lecture**: starting with **real-world motivation** and everyday physical analogies before moving into formal definitions, step-by-step visual diagrams, annotated code, and self-assessment practice questions.

Whether you are an absolute beginner or looking for deep computer science intuition, you can read these modules sequentially from top to bottom.

**Start here — the measuring system**

1. [[01-loops-and-what-they-cost|Loops and What They Cost]] — **[Beginner]** — counting iterations, why nested doesn't always mean O(n²), and **the hidden loops that make one-loop code quadratic**
2. [[foundations/dsa/05-algorithms/01-algorithms|Algorithms and Complexity Analysis]] — **[Beginner → Intermediate]** — **O, Ω and Θ and why they're not interchangeable**, best/average/worst as a separate axis, space complexity and the call stack, amortized vs average, recurrences, and reading a constraint to guess the intended complexity

Everything after this is quoted in the vocabulary those two establish, so they genuinely come first.

> **Prerequisite, not part of this course:** what a type actually is at the bit level, and why fixed-size types are what make array indexing O(1), now lives in [[foundations/programming-fundamentals/15-how-types-actually-work|how types actually work]]. Those two notes used to sit in this folder — they're type-system material rather than DSA, and they read better alongside the rest of the fundamentals. Worth a detour before [[01-arrays|arrays]] if "the same 32 bits mean different things depending on the type" isn't already obvious.

**Data structures**

3. [[01-arrays|arrays]] — **[Beginner]** — contiguous memory, O(1) indexing, row-major layout, **and why loop order alone can make a matrix scan several times slower**
4. [[02-dynamic-arrays|dynamic-arrays]] — **[Beginner]** — resizable arrays, and why doubling is what makes append amortized O(1)
5. [[03-hash-maps|hash-maps]] — **[Beginner]** — hashing, collisions, chaining vs open addressing, hash sets, **and what a hash map gives up to buy O(1)**
6. [[04-linked-lists|linked-lists]] — **[Intermediate]** — singly/doubly/circular, the sentinel trick, **and why they lose to arrays in practice despite the Big-O**
7. [[01-trees|trees]] — **[Intermediate]** — full/complete/perfect/balanced, BSTs, AVL and red-black rotations, **and the B+ trees under every database index**
   - [[02-traversal|traversal]] — **[Intermediate]** — pre/in/post/level-order (companion note)
8. [[06-graphs|graphs]] — **[Intermediate]** — directed/weighted/cyclic/bipartite, three representations, **and implicit graphs: the ones with no graph object at all**
9. [[foundations/dsa/04-data-structures/07-stacks-and-queues|stacks-and-queues]] — **[Beginner]** — LIFO/FIFO, the circular buffer trick
10. [[foundations/dsa/04-data-structures/08-heaps|heaps]] — **[Intermediate]** — priority queues, complete-tree-in-an-array, O(n) heapify, the two-heap median trick
11. [[foundations/dsa/04-data-structures/09-tries|tries]] — **[Intermediate]** — prefix trees, O(L) prefix queries a hash map can't do
12. [[foundations/dsa/04-data-structures/10-union-find|union-find]] — **[Advanced]** — disjoint sets, path compression + union by rank → O(α(n))

**Algorithms**

13. [[02-dfs|dfs]] — **[Intermediate]** — depth-first search
14. [[03-bfs|bfs]] — **[Intermediate]** — breadth-first search
15. [[04-sorting|sorting]] — **[Intermediate]** — bubble/insertion/merge/quicksort, stability, Timsort, counting sort
16. [[05-searching|searching]] — **[Beginner]** — linear vs binary search
17. [[06-dijkstra|dijkstra]] — **[Advanced]** — shortest path in weighted graphs, BFS generalized with a min-heap
18. [[foundations/dsa/05-algorithms/07-number-theory-basics|number-theory-basics]] — **[Intermediate]** — primality, Sieve of Eratosthenes, factorization, GCD/LCM
19. [[foundations/dsa/05-algorithms/08-leader-algorithm|leader-algorithm]] — **[Intermediate]** — majority element via Boyer-Moore voting
20. [[foundations/dsa/05-algorithms/09-max-slice-algorithms|max-slice-algorithms]] — **[Intermediate]** — Kadane's algorithm, maximum subarray sum
21. [[foundations/dsa/05-algorithms/10-greedy-algorithms|greedy-algorithms]] — **[Advanced]** — locally-optimal choices, and why they aren't always globally correct
22. [[foundations/dsa/05-algorithms/11-topological-sort|topological-sort]] — **[Intermediate]** — ordering a DAG, doubling as cycle detection
23. [[foundations/dsa/05-algorithms/12-minimum-spanning-tree|minimum-spanning-tree]] — **[Advanced]** — Prim's and Kruskal's, the cut property
24. [[foundations/dsa/05-algorithms/13-bit-manipulation|bit-manipulation]] — **[Intermediate]** — bitwise operators, XOR tricks, `x & (x-1)`, masks
25. [[foundations/dsa/05-algorithms/14-math-and-geometry|math-and-geometry]] — **[Intermediate]** — in-place matrix ops, fast exponentiation, grade-school arithmetic

Still unwritten and welcome here: A*, Bellman-Ford, the KMP string match, and segment/Fenwick trees.

## Next layer — LeetCode patterns

With the fundamentals above in place, [[foundations/dsa/06-patterns/README|patterns/]] covers the 15 reusable patterns that recur across problems — recognizing which pattern a problem is testing is most of the battle under time pressure. Patterns sit above both `data-structures/` and `algorithms/` because most combine a structure with a procedure (a heap plus a scanning pass for [[07-top-k-elements|top-k-elements]]).

## Putting it to work — NeetCode 150

[[foundations/dsa/neetcode-150/README|neetcode-150/]] holds all 150 problems from the [NeetCode 150](https://neetcode.io/practice) list — its README is the index (every problem → the concept note behind it, grouped by topic) with a **signal → tool** cheat-sheet, and each problem is worked in its own file in a flat `questions/` folder numbered 001–150 (**all 150 solved**). Start with the [[foundations/dsa/neetcode-150/interview-playbook|interview playbook]] for the meta-skill: the UMPIRE process (reword → clarify → examples → brute-force-then-optimize → code → test), and reading a problem's constraints to guess the intended approach.

## How this folder was built

The `pdfs/` folder holds the original Codility course material these notes were written against. Cross-referencing the notes against those PDFs surfaced five topics with zero coverage, since written: [[foundations/dsa/04-data-structures/07-stacks-and-queues|stacks-and-queues]], [[foundations/dsa/05-algorithms/07-number-theory-basics|number-theory-basics]], [[foundations/dsa/05-algorithms/08-leader-algorithm|leader-algorithm]], [[foundations/dsa/05-algorithms/09-max-slice-algorithms|max-slice-algorithms]], and [[foundations/dsa/05-algorithms/10-greedy-algorithms|greedy-algorithms]]. The same pass deepened [[04-sorting|sorting]] with non-comparison sorts, [[foundations/dsa/05-algorithms/01-algorithms|algorithms]] with the constraint-size heuristic, and [[foundations/dsa/06-patterns/09-modified-binary-search|modified-binary-search]] with "binary search on the answer."

Running the same cross-reference against the NeetCode 150 is what surfaced the [[foundations/dsa/04-data-structures/08-heaps|heaps]], [[foundations/dsa/04-data-structures/09-tries|tries]], [[foundations/dsa/04-data-structures/10-union-find|union-find]], [[foundations/dsa/05-algorithms/11-topological-sort|topological-sort]], [[foundations/dsa/05-algorithms/12-minimum-spanning-tree|MST]], [[foundations/dsa/05-algorithms/13-bit-manipulation|bit-manipulation]] and [[foundations/dsa/05-algorithms/14-math-and-geometry|math-and-geometry]] gaps, plus the worked 1-D/2-D recurrences in [[foundations/dsa/06-patterns/15-dynamic-programming|dynamic-programming]].

## Related
- [[foundations/programming-fundamentals/README|programming fundamentals]] — the on-ramp, if the code here isn't readable yet
- [[foundations/theory-of-computation/README|theory of computation]] — one level up: what's provably impossible or intractable, rather than merely slow
- [[databases/README|databases]] — where B+ trees, hashing and sorting do their production work

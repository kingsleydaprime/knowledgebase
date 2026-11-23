# Data Structures — University-Style Teaching Notes

The eleven core data structures, written to [[COURSE-STANDARD|the course standard]]: prerequisites, observable outcomes, a terminology table, the mechanism worked through by hand, a complete runnable lab, independent practice with hidden answers, and a demonstrable finish line.

This folder is about *how each structure works and what it costs*. The companion folder [[dsa/04-patterns/index|04-patterns]] is about recognising which structure or technique a problem calls for — several patterns there link back here rather than re-deriving the mechanics.

Every lab in this folder has been run and its output checked against the documented "Expected output".

## The structures

Ordered so each builds on the last: dynamic arrays assume arrays, graph searching uses stacks and queues, heaps assume trees, and tries assume both trees and hash maps.

1. [[01-arrays|01 — Arrays]] — contiguous memory, O(1) indexing, and why insertion in the middle is O(n)
2. [[02-dynamic-arrays|02 — Dynamic Arrays]] — geometric growth, and the amortised argument that makes `append` O(1)
3. [[03-hash-maps|03 — Hash Maps & Hash Sets]] — hashing, collision resolution, load factor, and when O(1) degrades
4. [[04-linked-lists|04 — Linked Lists]] — pointer-based nodes, O(1) splicing, and the cost of losing random access
5. [[05-stacks-and-queues|05 — Stacks and Queues]] — LIFO and FIFO, and the problems whose shape each one matches
6. [[06-trees/01-trees|01 — Trees]] — hierarchy, height vs. size, and why an unbalanced BST degenerates to a list
   - [[06-trees/04-traversal/index|Tree Traversal]] — pre-order, in-order, post-order, level-order, and what each one is *for*
7. [[07-heaps|07 — Heaps & Priority Queues]] — the heap property, sift-up/sift-down, and O(log n) extreme-value access
8. [[08-tries|08 — Tries / Prefix Trees]] — shared prefixes, and trading memory for prefix queries
9. [[09-graphs/index|Graphs]] — vertices and edges, adjacency list vs. matrix, and the space/time tradeoff between them
10. [[10-union-find|10 — Union-Find / Disjoint Set Union]] — dynamic connectivity, path compression, and union by rank

## Question banks

One bank per lesson: micro-questions with the answers hidden behind toggles, for closed-book recall rather than reading. Method explained in [[dsa/02-data-structures/01-arrays-qb|the arrays bank]].

- [[01-arrays-qb|Arrays]]
- [[02-dynamic-arrays-qb|Dynamic Arrays]]
- [[03-hash-maps-qb|Hash Maps & Hash Sets]]
- [[04-linked-lists-qb|Linked Lists]]
- [[05-stacks-and-queues-qb|Stacks and Queues]]
- [[07-heaps-qb|Heaps & Priority Queues]]
- [[08-tries-qb|Tries / Prefix Trees]]
- [[10-union-find-qb|Union-Find]]
- [[06-trees/index|Trees]] — banks for that folder's lessons
- [[09-graphs/index|Graphs]] — banks for that folder's lessons

---

## Related

- [[dsa/index|DSA notes]] — the parent folder
- [[dsa/04-patterns/index|04-patterns]] — the 15 recurring problem-solving patterns
- [[01-growth-and-asymptotic-notation|03-algorithms]] — sorting, searching, and graph algorithms built on these structures

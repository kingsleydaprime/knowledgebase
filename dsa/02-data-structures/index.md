# Data Structures — University-Style Teaching Notes

The eleven core data structures, written to [[COURSE-STANDARD|the course standard]]: prerequisites, observable outcomes, a terminology table, the mechanism worked through by hand, a complete runnable lab, independent practice with hidden answers, and a demonstrable finish line.

This folder is about *how each structure works and what it costs*. The companion folder [[dsa/04-patterns/index|04-patterns]] is about recognising which structure or technique a problem calls for — several patterns there link back here rather than re-deriving the mechanics.

Every lab in this folder has been run and its output checked against the documented "Expected output".

## The structures

Ordered so each builds on the last — dynamic arrays assume arrays, heaps assume trees, tries assume both trees and hash maps.

1. [[01-arrays|Arrays]] — contiguous memory, O(1) indexing, and why insertion in the middle is O(n)
2. [[02-dynamic-arrays|Dynamic Arrays]] — geometric growth, and the amortised argument that makes `append` O(1)
3. [[03-hash-maps|Hash Maps & Hash Sets]] — hashing, collision resolution, load factor, and when O(1) degrades
4. [[04-linked-lists|Linked Lists]] — pointer-based nodes, O(1) splicing, and the cost of losing random access
5. [[05-trees/01-trees|Trees]] — hierarchy, height vs. size, and why an unbalanced BST degenerates to a list
   - [[05-trees/02-traversal|Tree Traversal]] — pre-order, in-order, post-order, level-order, and what each one is *for*
6. [[06-graphs/index|Graphs]] — vertices and edges, adjacency list vs. matrix, and the space/time tradeoff between them
7. [[07-stacks-and-queues|Stacks and Queues]] — LIFO and FIFO, and the problems whose shape each one matches
8. [[08-heaps|Heaps & Priority Queues]] — the heap property, sift-up/sift-down, and O(log n) extreme-value access
9. [[09-tries|Tries / Prefix Trees]] — shared prefixes, and trading memory for prefix queries
10. [[10-union-find|Union-Find]] — dynamic connectivity, path compression, and union by rank

## Related

- [[dsa/index|DSA notes]] — the parent folder
- [[dsa/04-patterns/index|04-patterns]] — the 15 recurring problem-solving patterns
- [[dsa/03-algorithms/01-algorithms|03-algorithms]] — sorting, searching, and graph algorithms built on these structures

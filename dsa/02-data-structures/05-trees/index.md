# Trees

**Hierarchy: the structure for data that branches.** Four lessons plus a traversal folder, written to [[COURSE-STANDARD|the course standard]].

> **Why this is a folder.** "Tree" is a shape, not one structure. A dozen different things are trees, built for different jobs, and the word alone tells you almost nothing. The lessons separate the general idea from the particular structure this course is built on, so that "binary search tree" never has to carry all the meaning at once.

## Reading order

1. [[01-trees|Trees]] — **[Intermediate]** — what a tree is, the vocabulary, the height-versus-depth trap, and a catalogue of **the kinds of tree** with what each is for
2. [[02-binary-trees|Binary Trees]] — **[Intermediate]** — at most two children; the five shapes (full, perfect, complete, balanced, degenerate) each with an implementation; and why a complete tree needs no pointers
3. [[03-binary-search-trees|Binary Search Trees]] — **[Intermediate]** — the ordering rule, search, insert and delete, the ADT, self-balancing, and why every cost is $O(h)$ rather than $O(\log n)$
4. [[04-traversal/index|Traversal]] — **[Intermediate]** — a folder: the three depth-first orders, and level-order

## The one idea that runs through all of it

**A tree's cost is its height, and its height is not guaranteed.**

Every binary search tree operation is $O(h)$. When the tree is balanced, $h \approx \log_2 n$ and a million items are 20 comparisons away. When it is degenerate, $h = n$ and the same structure is a [[../04-linked-lists|linked list]] with extra steps.

Degeneracy is not a rare accident — **inserting already-sorted data causes it every time**, and sorted input is the most common input there is. That single fact is why self-balancing trees exist, and why the lab in lesson 3 builds the same keys two ways and measures the difference.

## Where the other tree-shaped structures live

Two structures in this folder are trees but have their own lessons, because what makes them interesting is not their treeness:

- [[../08-heaps|Heaps]] — a complete binary tree with a much weaker ordering rule, stored in a flat array.
- [[../09-tries|Tries]] — a tree where the **path** spells a word rather than any node holding one.

And [[../06-graphs/03-subgraphs-trees-and-forests|the graphs folder]] defines a tree without a root at all — connected and acyclic — which is where the $n-1$ edge count and the one-path-between-any-two-nodes property actually come from.

## Related

- [[../index|02-data-structures]] — the parent folder
- [[../06-graphs/index|Graphs]] — the general case; a tree is a graph with no cycles
- [[databases/index|databases/]] — where B-trees and B+ trees take these ideas to disk

# Trees — Question Bank

Micro-questions over [[01-trees|the trees module]]. Answer in a full sentence before opening the toggle. Format explained in [[dsa/02-data-structures/01-arrays-qb|the arrays bank]].

---

## A. Why trees exist

**1. What is the limitation of linear structures that trees fix?**

<details><summary>Answer</summary>

Arrays and linked lists store things in **one line**. Plenty of real data is not a line but a hierarchy — things containing things — and forcing a hierarchy into a line loses the structure.

</details>

**2. Give three real-world examples of trees.**

<details><summary>Answer</summary>

A file system (folders containing folders), the DOM of a web page, and a company org chart.

</details>

**3. What is a tree, informally?**

<details><summary>Answer</summary>

A collection of nodes connected by edges, starting from a single root, where every node has exactly one parent except the root, and nothing loops back.

</details>

---

## B. The vocabulary

**4. What is a node?**

<details><summary>Answer</summary>

One item in the tree — a value plus pointers to the nodes beneath it.

</details>

**5. What is an edge?**

<details><summary>Answer</summary>

The link between two nodes; the line drawn between a parent and a child.

</details>

**6. What is the root?**

<details><summary>Answer</summary>

The single node at the very top, the one with **no parent**. A tree has exactly one, and it is where every traversal begins.

</details>

**7. What is a parent?**

<details><summary>Answer</summary>

A node that points directly down to another. Every node has exactly one parent, except the root, which has none.

</details>

**8. What is a child?**

<details><summary>Answer</summary>

A node directly below a parent.

</details>

**9. What are siblings?**

<details><summary>Answer</summary>

Nodes sharing the same parent.

</details>

**10. What is a leaf?**

<details><summary>Answer</summary>

A node with no children — the end of a branch. Also called a terminal node.

</details>

**11. What is an internal node?**

<details><summary>Answer</summary>

Any node that is not a leaf, i.e. one with at least one child.

</details>

**12. What is an ancestor?**

<details><summary>Answer</summary>

Any node on the path from the root down to a given node.

</details>

**13. What is a descendant?**

<details><summary>Answer</summary>

Any node reachable by moving downwards from a given node.

</details>

**14. What is a subtree, and what does it make possible?**

<details><summary>Answer</summary>

A node together with all of its descendants. **Every node is the root of its own subtree** — which is what makes tree algorithms naturally recursive.

</details>

**15. What is the degree of a node?**

<details><summary>Answer</summary>

How many children it has. A leaf has degree 0.

</details>

**16. What is a level?**

<details><summary>Answer</summary>

How far down a node sits. The root is at level 0, its children at level 1, and so on.

</details>

---

## C. Height versus depth

**17. Define depth.**

<details><summary>Answer</summary>

How far down a node is from the root — count edges **root → node**. The root has depth 0.

</details>

**18. Define height.**

<details><summary>Answer</summary>

The longest path from a node down to a leaf — count edges **node → leaf**. A leaf has height 0.

</details>

**19. What is the height of the tree?**

<details><summary>Answer</summary>

The height of the root node.

</details>

**20. Give the memory trick for telling them apart.**

<details><summary>Answer</summary>

**Depth** measures how deep you sink down from the surface (the root). **Height** measures how tall a tower is built up from the ground (a leaf).

</details>

**21. In the reference tree A→(B,C), B→(D,E), C→F — give depth of D and height of B.**

<details><summary>Answer</summary>

Depth of D = 2 (A→B→D). Height of B = 1 (B→D). Height of the whole tree = 2.

</details>

**22. Can a node have the same height and depth?**

<details><summary>Answer</summary>

Yes — for example a leaf at depth 0, which is a single-node tree, has both equal to 0. In general they measure opposite directions and are unrelated.

</details>

---

## D. The formal definition

**23. Give the formal definition of a tree.**

<details><summary>Answer</summary>

A connected, acyclic graph. With $n$ nodes it has exactly $n - 1$ edges.

</details>

**24. Why exactly $n - 1$ edges?**

<details><summary>Answer</summary>

Every node except the root is the child end of exactly one edge — one edge per node, minus the parentless root.

</details>

**25. What are the two consequences of having no cycles?**

<details><summary>Answer</summary>

1. There is **exactly one unique path** between the root and any node.
2. Trees are **inherently recursive** — any node can be viewed as the root of a smaller tree.

</details>

**26. Why is almost every tree algorithm written recursively?**

<details><summary>Answer</summary>

Because solving a problem on a tree means solving the identical problem on its left and right subtrees. The structure is self-similar, so the code is too.

</details>

---

## E. The kinds of tree

**27. What is a binary tree?**

<details><summary>Answer</summary>

Every node has **at most two** children, called left and right.

</details>

**28. What is an n-ary tree? A general tree?**

<details><summary>Answer</summary>

N-ary: up to $N$ children per node — a file system is one. General: any number of children, no limit — the DOM is one.

</details>

**29. What is a binary search tree?**

<details><summary>Answer</summary>

A binary tree with a rule added: everything in a node's left subtree is smaller than it, everything in the right subtree is larger. That rule is what makes a tree searchable.

</details>

**30. What is an AVL tree?**

<details><summary>Answer</summary>

A BST that rebalances itself after every insertion and deletion, keeping height close to $\log n$. Strictly balanced: fast lookups, slightly more expensive modifications.

</details>

**31. What is a red-black tree, and why is it what libraries actually use?**

<details><summary>Answer</summary>

Another self-balancing BST, with looser balance rules than AVL. Rebalancing is cheaper and lookups slightly slower — a better trade for general use, which is why Java's `TreeMap` and C++'s `std::map` are red-black trees.

</details>

**32. What is a B-tree, and why is its shape wide and shallow?**

<details><summary>Answer</summary>

Each node holds **many** keys and has **many** children. The wide, shallow shape means fewer disk reads to reach any key, which is why almost every database index is a B-tree.

</details>

**33. What does a B+ tree change, and why do databases prefer it?**

<details><summary>Answer</summary>

All the actual data lives in the leaves, and the leaves are linked in a chain. That chain makes **range queries** very fast — "everything between these two values" — which is what databases mostly do.

</details>

**34. What is a trie?**

<details><summary>Answer</summary>

A tree where the **path spells a word** rather than any node holding one. Built for prefix questions. See [[09-tries|tries]].

</details>

**35. How is a heap's rule weaker than a BST's, and why is that deliberate?**

<details><summary>Answer</summary>

Each parent is merely ordered relative to its children, with no rule between siblings. The weakness makes the rule cheap to maintain, which is the whole point. See [[08-heaps|heaps]].

</details>

**36. What is a segment tree for?**

<details><summary>Answer</summary>

Storing a summary of a range in each node, so questions like "what is the sum between positions 5 and 900?" are answered in $O(\log n)$ while still allowing updates.

</details>

**37. What is a Fenwick tree, and what is its trade against a segment tree?**

<details><summary>Answer</summary>

Also called a binary indexed tree. It answers the same range questions with less memory and much shorter code, at the cost of being harder to reason about.

</details>

**38. What is a suffix tree for?**

<details><summary>Answer</summary>

Storing every suffix of a string, making substring search extremely fast. Heavily used in bioinformatics for DNA matching.

</details>

**39. What is a k-d tree for?**

<details><summary>Answer</summary>

It splits **space** rather than a list, answering "which stored point is nearest to this one?" — nearest-neighbour search in graphics and machine learning.

</details>

**40. Why does this course concentrate on binary trees?**

<details><summary>Answer</summary>

Because that is where the core ideas live: recursion over a hierarchy, the relationship between height and cost, and the fact that **balance is what makes a tree fast**. The rest are variations once those are clear.

</details>

---

## F. Boundaries

**41. What does a tree degenerate into when it loses its balance?**

<details><summary>Answer</summary>

A [[04-linked-lists|linked list]] — every node with one child, height $n$, and every $O(\log n)$ claim collapsing to $O(n)$.

</details>

**42. How does the graphs folder define a tree differently?**

<details><summary>Answer</summary>

Without a root: a connected acyclic **graph**. Rootedness is something you add by choosing a node, not part of the underlying object. See [[06-graphs/03-subgraphs-trees-and-forests|trees and forests]].

</details>

**43. Summarise a tree in one sentence.**

<details><summary>Answer</summary>

A hierarchy with exactly one path to each node — self-similar, so recursion is the natural tool, and fast only as long as it stays short.

</details>

---

## Scorecard

| Pass | Date | Got it | Close | Blank | Questions missed |
| :--- | :--- | :----- | :---- | :---- | :--------------- |
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |

---

## Related

- [[01-trees|Trees]] — the module
- [[02-binary-trees-qb|Binary Trees — Question Bank]] — the next bank
- [[dsa/02-data-structures/04-linked-lists-qb|Linked Lists — Question Bank]] — what an unbalanced tree becomes

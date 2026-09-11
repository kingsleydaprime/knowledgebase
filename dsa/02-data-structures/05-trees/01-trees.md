# Module: Trees (Hierarchy, and the Shapes It Comes In)

**[Intermediate]** — what a tree is, the many kinds there are, and why this course concentrates on one of them.

## Before you start

- You know what a [[04-linked-lists|linked list]] is, and that following a pointer is how you move between nodes.
- You know what [[06-graphs/index|a graph]] is, or you can read this first and meet graphs later — a tree is a special kind of graph, and [[06-graphs/03-subgraphs-trees-and-forests|the graphs folder]] proves the connection.

**After this lesson you will be able to:**

1. Explain what makes a structure a tree, and why "no cycles" is the condition that matters.
2. Use the vocabulary — root, parent, child, leaf, subtree, height, depth — precisely.
3. Name the **main kinds of tree** and say what each one is for.
4. Say why this course focuses on binary trees, and what that leaves out.

**Study route:** read the terms, then the height-versus-depth trap, then the catalogue of tree types at the end.

---

## Why do we need trees?

Before diving into formal computer science definitions, let's understand why linear data structures (Arrays and Linked Lists) are not always enough.

### The Limitation of Linear Structures
- **Arrays**: Excellent for accessing elements by index ($O(1)$), but inserting or deleting elements in the middle requires shifting elements ($O(n)$).
- **Linked Lists**: Fast insertion and deletion ($O(1)$), but searching for an item requires walking link-by-link from the beginning ($O(n)$).

What if you need to organize data that naturally branches, or data that needs **both fast search and dynamic insertion**? That is where **Trees** come in.

### Real-World Examples of Trees
You interact with trees every single day when using software:

1. **Your Computer's File Explorer / Directory System**:
   - The main drive (`C:\` or `/`) is the top folder.
   - Folders contain subfolders, which contain files.
   
2. **Web Pages (The HTML Document Object Model - DOM)**:
   - The `<html>` tag contains `<head>` and `<body>`.
   - The `<body>` contains `<div>` tags, which contain `<p>` and `<a>` elements.

3. **Company Organizational Charts**:
   - The CEO is at the top.
   - Vice Presidents report to the CEO, Directors report to VPs, and Engineers report to Directors.

---

## What is a tree?

In computer science, a **Tree** is a collection of nodes connected by edges, organized in a parent-child hierarchy with **no loops or cycles**.

> **Fun Fact**: In real life, trees grow from the ground up. In computer science, we draw trees upside down, with the **Root at the top** and the **Leaves at the bottom**.

### Visualizing a Tree

```
                   [ Root ]
                      (A)
                     /   \
                   /       \
                 (B)       (C)
                /   \        \
              (D)   (E)      (F)  <-- Leaves
```


### Terms used with trees

1. **Node**: This is one item in the tree. It holds a value and pointers to the nodes beneath it. In the diagram above, `A` through `F` are all nodes.

2. **Edge**: This is the link between two nodes — the line drawn between `A` and `B`.

3. **Root**: This is the single node at the very top, the one with **no parent**. Node `A` is the root. A tree has exactly one, and it is where every traversal begins.

4. **Parent**: This is a node that points directly down to another. `A` is the parent of `B` and `C`. Every node has exactly one parent, except the root, which has none.

5. **Child**: This is a node directly below a parent. `B` and `C` are the children of `A`.

6. **Siblings**: These are nodes sharing the same parent. `B` and `C` are siblings, and so are `D` and `E`.

7. **Leaf**: This is a node with **no children** — the end of a branch. `D`, `E` and `F` are leaves. It is also called a **terminal node**.

8. **Internal node**: This is any node that is not a leaf, meaning it has at least one child. `A`, `B` and `C` are internal nodes.

9. **Ancestor**: This is any node on the path from the root down to a given node. The ancestors of `D` are `B` and `A`.

10. **Descendant**: This is any node you can reach by moving downwards from a given node. The descendants of `A` are every other node in the tree.

11. **Subtree**: This is a node together with all of its descendants. `B` with `D` and `E` forms a subtree rooted at `B`. **Every node is the root of its own subtree**, and that fact is what makes tree algorithms naturally recursive.

12. **Degree**: This is how many children a node has. A leaf has degree 0.

13. **Level**: This is how far down a node sits. The root is at level 0, its children at level 1, and so on.

## Height versus depth — the classic off-by-one trap

Two measurements describe the position of nodes inside a tree: **Depth** and **Height**. Computer science students often confuse them:

```
Level 0 (Root) --------> (A)            Height of Tree = 2
                        /   \
Level 1 -------------> (B)   (C)        Depth of B = 1
                      /   \    \
Level 2 ------------> (D) (E)  (F)      Depth of D = 2, Height of D = 0
```

- **Depth (or Level)**: How far down a node is from the root.
  - **Rule**: Count edges from **Root $\rightarrow$ Node**.
  - Root `A` has **Depth 0**. Node `B` has **Depth 1**. Node `D` has **Depth 2**.
- **Height**: The longest path from a node down to a leaf.
  - **Rule**: Count edges on the longest path from **Node $\rightarrow$ Leaf**.
  - Leaf `D` has **Height 0**. Node `B` has **Height 1** (path: `B -> D`). Root `A` has **Height 2** (path: `A -> B -> D`).
  - **Height of the Tree** = Height of the Root node (here, 2).

> [!TIP]
> **Memory Trick**: **Depth** measures how deep you sink down from the surface (Root). **Height** measures how tall a tower is built up from the ground (Leaf).

---

## The formal definition, and why trees are recursive

Formally, a tree with $n$ nodes is a connected, acyclic graph with exactly **$n - 1$ edges**.

### Why "No Cycles" Matters
Because there are no loops (cycles) and every node except the root has exactly **one parent**:
1. There is **exactly one unique path** between the root and any node.
2. **Trees are inherently recursive**: Any node in a tree can be viewed as the root of a smaller tree (its subtree).

This is why almost every tree algorithm (traversals, searches, insertions) is written using **recursion**! Solving a problem on a tree simply means solving the identical problem on its left and right subtrees.

---

## The kinds of tree

"Tree" is a shape, not a single structure. Many different things are trees, built for very different jobs. Here are the ones worth knowing by name.

### Trees grouped by how many children a node may have

1. **Binary tree**: Every node has **at most two** children, called the left child and the right child. This is the kind this course concentrates on, and [[02-binary-trees|the next lesson]] covers it properly.

2. **N-ary tree**: Every node may have up to **N** children. A file system is an n-ary tree — a folder can hold any number of items.

3. **General tree**: Every node may have **any** number of children, with no limit. The DOM in a web page is one of these.

### Trees that keep their data in order

4. **Binary search tree**: This is a binary tree with a rule added — everything in a node's left subtree is smaller than it, and everything in the right subtree is larger. That rule is what turns a tree into a searchable structure, and it is [[03-binary-search-trees|lesson 3]].

5. **AVL tree**: This is a binary search tree that **rebalances itself** after every insertion and deletion, keeping its height close to $\log n$. It is strictly balanced, which makes lookups fast and modifications slightly more expensive.

6. **Red-black tree**: This is another self-balancing binary search tree, with looser balance rules than an AVL tree. Rebalancing is cheaper, lookups are slightly slower, and it is what most standard libraries actually use — Java's  and C++'s  are red-black trees.

7. **B-tree**: This is a self-balancing tree where each node holds **many** keys and has **many** children, rather than one key and two children. The wide, shallow shape means fewer disk reads to reach any key, which is why almost every database index is a B-tree.

8. **B+ tree**: This is a B-tree variant where all the actual data lives in the leaves, and the leaves are linked together in a chain. That chain makes range queries — "everything between these two values" — very fast, which is why it, rather than the plain B-tree, is what databases most often use.

### Trees built for one particular job

9. **Trie**: This is a tree where the **path spells a word** rather than any node holding one. It is built for prefix questions, and it is [[09-tries|its own lesson]].

10. **Heap**: This is a tree with a much weaker rule than a binary search tree — each parent is merely ordered relative to its children, with no rule between siblings. That weakness is deliberate and makes it cheap to maintain. It is [[08-heaps|its own lesson]] too.

11. **Segment tree**: This stores a summary of a range in each node, so questions like "what is the sum between positions 5 and 900?" can be answered in (\log n)$ while still allowing updates.

12. **Fenwick tree**: Also called a **binary indexed tree**. It answers the same sort of range question as a segment tree, using less memory and much shorter code, at the cost of being harder to reason about.

13. **Suffix tree**: This stores every suffix of a string, which makes substring searching extremely fast. It is heavily used in bioinformatics for matching DNA sequences.

14. **k-d tree**: This splits space rather than a list, so it can answer "which stored point is nearest to this one?" It underlies nearest-neighbour search in graphics and machine learning.

### What this course covers

**This course focuses on binary trees**, and within them on binary search trees, because they are where the core ideas live: recursion over a hierarchy, the relationship between height and cost, and the fact that **balance is what makes a tree fast**. Once those are clear, the others are variations rather than new subjects.

Heaps and tries have their own lessons here because they are used constantly in practice. B-trees and B+ trees appear in [[databases/index|databases]], where the reason for their shape — minimising disk reads — actually makes sense. Segment trees, Fenwick trees, suffix trees and k-d trees are specialist tools, worth knowing exist so that you recognise the problem shape when you meet it.

## Before moving on

You can define a tree, use the vocabulary without hesitating, tell height from depth, and name the main kinds of tree and what each is for.

**Recap:** a tree is a connected structure with no cycles and exactly one root; every node has one parent except the root; a leaf has no children; every node is the root of its own subtree, which is why tree algorithms are naturally recursive; **depth** counts downwards from the root and **height** counts upwards from the deepest leaf; trees come in many kinds, and this course concentrates on binary trees because that is where the core ideas live.

**Next:** [[02-binary-trees|Binary Trees]] — at most two children, and the five shapes worth naming.

## Related

- [[index|the trees folder]] — the rest of this course
- [[02-binary-trees|Binary Trees]] — the next lesson, and where this course goes
- [[06-graphs/03-subgraphs-trees-and-forests|Graphs: trees and forests]] — the same object, defined without a root
- [[04-linked-lists|Linked Lists]] — what a tree degenerates into when it loses its balance

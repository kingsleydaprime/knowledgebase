# Module: Trees — Hierarchical Data Structures

Welcome to the **Trees** course module. In linear data structures like Arrays and Linked Lists, elements follow one after another in a straight line. In this module, we introduce **hierarchical data structures**, where elements branch out in parent-child relationships.

---

## 1. Why Do We Need Trees? (Real-World Motivation)

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

## 2. What Is a Tree? (Intuition & Visual Anatomy)

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

### Key Terminology Demystified

| Term | Plain-English Definition | Example from Diagram Above |
| :--- | :--- | :--- |
| **Node** | An individual container holding data and pointers to other nodes. | `A`, `B`, `C`, `D`, `E`, `F` |
| **Edge** | The connection/link between two nodes. | Line between `A` and `B` |
| **Root** | The absolute top node of the tree. It has **no parent**. | Node `A` |
| **Parent** | A node that points directly down to a child node. | Node `A` is parent to `B` and `C` |
| **Child** | A node directly connected to a parent node above it. | `B` and `C` are children of `A` |
| **Siblings** | Nodes that share the exact same parent node. | `B` and `C` are siblings; `D` and `E` are siblings |
| **Leaf (Terminal Node)** | A node that has **zero children** (the end of a branch). | Nodes `D`, `E`, and `F` |
| **Internal Node** | Any node that is not a leaf (i.e., has at least one child). | Nodes `A`, `B`, `C` |
| **Ancestor** | Any node on the path from the root down to a given node. | Ancestors of `D` are `B` and `A` |
| **Descendant** | Any node reachable by moving downward from a given node. | Descendants of `A` are `B`, `C`, `D`, `E`, `F` |
| **Subtree** | A node and all of its descendants. (Every node is the root of its own subtree). | `B-D-E` forms a subtree rooted at `B` |

---

## 3. Height vs. Depth (The Classic Off-By-One Trap)

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

## 4. Formal Definition & The Recursive Nature of Trees

Formally, a tree with $n$ nodes is a connected, acyclic graph with exactly **$n - 1$ edges**.

### Why "No Cycles" Matters
Because there are no loops (cycles) and every node except the root has exactly **one parent**:
1. There is **exactly one unique path** between the root and any node.
2. **Trees are inherently recursive**: Any node in a tree can be viewed as the root of a smaller tree (its subtree).

This is why almost every tree algorithm (traversals, searches, insertions) is written using **recursion**! Solving a problem on a tree simply means solving the identical problem on its left and right subtrees.

---

## 5. Binary Trees: Definition and Common Shapes

A **Binary Tree** is the most widely used variation of a tree. The rule is simple: **Every node can have AT MOST two children**, conventionally named `left` and `right`.

### Python Implementation of a Tree Node
```python
class TreeNode:
    """Represents a single node in a Binary Tree."""
    def __init__(self, val=0, left=None, right=None):
        self.val = val        # The value stored in this node
        self.left = left      # Reference to left child (TreeNode or None)
        self.right = right    # Reference to right child (TreeNode or None)
```

### The 5 Standard Shapes of Binary Trees

Understanding these shapes is critical because a tree's shape directly dictates its performance ($O(\log n)$ vs $O(n)$).

#### 1. Full (Proper) Binary Tree
Every node has **either 0 or 2 children**. No node has only 1 child.
```
       1
      / \
     2   3
    / \
   4   5
```
*Where it's used*: Arithmetic expression trees (e.g. `(4 + 5) * 3`), where operators (`+`, `*`) take 2 operands, and numbers take 0.

#### 2. Complete Binary Tree
Every level is completely filled, except possibly the last level, which is filled **strictly from left to right**.
```
       1
      / \
     2   3
    / \  /
   4  5 6
```
*Where it's used*: **Heaps** and Priority Queues! Because there are no gaps, a complete binary tree can be stored efficiently in a flat Array without using pointers.

#### 3. Perfect Binary Tree
All internal nodes have 2 children, and **all leaves are at the exact same depth**.
```
       1
      / \
     2   3
    / \ / \
   4  5 6  7
```
*Formula*: A perfect binary tree of height $h$ has total nodes $n = 2^{h+1} - 1$. For height 2, $n = 2^3 - 1 = 7$ nodes.

#### 4. Balanced Binary Tree
A tree where the height of the left and right subtrees of *every node* differs by at most 1.
```
       1
      / \
     2   3
    /
   4
```
*Why it matters*: Keeps tree height bounded to $O(\log n)$, guaranteeing fast searches.

#### 5. Degenerate (Pathological) Binary Tree
Every node has only 1 child. The tree degrades into a single straight line.
```
   1
    \
     2
      \
       3
        \
         4
```
*Why it's dangerous*: Structurally identical to a **Linked List**. Height becomes $n-1$, and operations slow down from $O(\log n)$ to $O(n)$.

---

## 6. Binary Search Trees (BSTs)

A **Binary Search Tree (BST)** is a binary tree with a special ordering rule called the **BST Invariant**:

> **The BST Invariant**: For every node $X$:
> - All values in $X$'s **left subtree** must be strictly **smaller** than $X$'s value.
> - All values in $X$'s **right subtree** must be strictly **larger** than $X$'s value.

### Visualizing a Valid BST

```
            (8)
          /     \
        (3)     (10)
       /   \        \
     (1)   (6)      (14)
          /   \     /
        (4)   (7) (13)
```
Notice:
- Left of `8`: `{1, 3, 4, 6, 7}` (all $< 8$).
- Right of `8`: `{10, 13, 14}` (all $> 8$).

### How Searching Works in a BST ($O(\log n)$)

Searching a BST mimics **Binary Search** on a sorted array:
1. Start at the root.
2. If `target == current.val`, you found it!
3. If `target < current.val`, go **left** (discard the entire right half of the tree).
4. If `target > current.val`, go **right** (discard the entire left half of the tree).

#### Python Implementation of BST Search

```python
def bst_search(node: TreeNode, target: int) -> TreeNode:
    """Recursively search for target in a Binary Search Tree."""
    # Base Case: target not found (None) or target found
    if node is None or node.val == target:
        return node
    
    # If target is smaller than current node, search left subtree
    if target < node.val:
        return bst_search(node.left, target)
    
    # Otherwise, target is larger, search right subtree
    return bst_search(node.right, target)
```

### Two Essential BST Properties to Remember

1. **Inorder Traversal of a BST yields SORTED order!**
   - If you visit `Left Subtree -> Root -> Right Subtree`, you will visit the values in strictly ascending order: `1, 3, 4, 6, 7, 8, 10, 13, 14`.
2. **The BST invariant applies to ENTIRE subtrees, not just immediate children!**
   - *Common Bug*: Only checking `node.left.val < node.val` is NOT enough. A node deep inside the left subtree could still be greater than the root!

---

## 7. Self-Balancing Trees & Production Use

What happens if you insert already sorted data (`1, 2, 3, 4, 5`) into a plain BST?
- `1` becomes root. `2` goes right of `1`. `3` goes right of `2`...
- You get a **Degenerate Tree** (Linked List), and search time degrades to $O(n)$!

To prevent this, production software uses **Self-Balancing Binary Search Trees**, which perform mathematical re-arrangements called **Tree Rotations** to keep height at $O(\log n)$.

```
   Right Rotation on Node 5:
        (5)                   (3)
       /   \                 /   \
     (3)   (D)    -->      (A)   (5)
    /   \                       /   \
  (A)   (C)                   (C)   (D)
```

### Types of Self-Balancing Trees

1. **AVL Trees**:
   - Enforces strict balance: height difference between left and right subtrees $\le 1$.
   - *Best for*: Read-heavy workloads where fast lookup is critical.
2. **Red-Black Trees**:
   - Uses node colors (Red/Black) and rules to ensure the longest path is at most $2\times$ the shortest path.
   - Requires fewer rotations during insertions/deletions than AVL trees.
   - *Where it's used*: Java `TreeMap`, C++ `std::map`, Linux kernel process scheduler.
3. **B-Trees & B+ Trees**:
   - Nodes hold **hundreds of keys** and have **hundreds of children** instead of just 2.
   - *Why*: Reduces tree height to just 3-4 levels for billions of records, minimizing expensive **Disk Reads/Seeks**.
   - *Where it's used*: **Every major database index** (PostgreSQL, MySQL InnoDB, SQLite) and Filesystem (ext4, NTFS).

---

## 8. Summary of Complexity

| Structure / Tree Type | Average Search | Worst Case Search | Average Insert | Worst Case Insert |
| :--- | :--- | :--- | :--- | :--- |
| **Unbalanced BST** | $O(\log n)$ | $O(n)$ (degenerate) | $O(\log n)$ | $O(n)$ |
| **AVL Tree** | $O(\log n)$ | $O(\log n)$ | $O(\log n)$ | $O(\log n)$ |
| **Red-Black Tree** | $O(\log n)$ | $O(\log n)$ | $O(\log n)$ | $O(\log n)$ |
| **B+ Tree (Disk)** | $O(\log n)$ | $O(\log n)$ | $O(\log n)$ | $O(\log n)$ |

---

## 9. Check Your Understanding (University Self-Assessment)

Try answering these questions to verify what you've learned:

1. **Question**: A binary tree has a root node $A$. Node $A$ has left child $B$ and right child $C$. Node $B$ has left child $D$. What is the **Depth** of $D$ and what is the **Height** of $A$?
   - <details><summary>Click for Answer</summary><b>Answer:</b> Depth of D is <b>2</b> (path: A -> B -> D). Height of A is <b>2</b> (longest path to leaf D: A -> B -> D).</details>

2. **Question**: Why does a database like PostgreSQL use a B+ Tree instead of a standard Binary Search Tree?
   - <details><summary>Click for Answer</summary><b>Answer:</b> Database records live on disk. Reading from disk is millions of times slower than RAM. A B+ Tree has hundreds of keys per node, keeping the tree height to 3–4 levels, requiring only 3–4 disk seeks instead of ~30 seeks for a BST.</details>

3. **Question**: What traversal order on a Binary Search Tree produces values in sorted order?
   - <details><summary>Click for Answer</summary><b>Answer:</b> <b>Inorder Traversal</b> (Left Subtree -> Root -> Right Subtree).</details>

---

## Related Modules
- [[02-traversal|Tree Traversal]] — Pre-order, In-order, Post-order, and Level-order walkthroughs
- [[04-linked-lists|Linked Lists]] — The 1-child linear precursor to trees
- [[06-graphs|Graphs]] — Generalizing trees to allow cycles and multiple parents
- [[08-heaps|Heaps]] — Priority queues implemented as complete binary trees in flat arrays
- [[databases/README|Databases]] — Practical application of B+ Trees in indexing

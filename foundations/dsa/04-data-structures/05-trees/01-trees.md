# Trees

A tree is a hierarchical structure: one root node, and every other node has exactly one parent, forming branches with no cycles. It's what you get when you take a [[04-linked-lists|linked list]] and let each node point to more than one "next" — a linked list is really a tree where every node has at most one child.

Formally it's a connected, acyclic [[06-graphs|graph]] with exactly `n-1` edges. That constraint is the source of every property below: **no cycles means recursion terminates, and one parent means there's exactly one path between any two nodes.**

## Terminology

- **Root** — the top node, no parent. **Leaf** — a node with no children. **Internal node** — any node that isn't a leaf.
- **Parent / child** — a direct connection one level apart. **Siblings** — nodes sharing a parent. **Ancestor / descendant** — the transitive versions.
- **Height** of a node — edges on the longest path *down* to a leaf. The **height of the tree** is the root's height. A single node has height 0.
- **Depth** (or **level**) of a node — edges from the root *down* to it. The root is depth 0. Height counts down, depth counts up — mixing them is a routine off-by-one.
- **Degree** — the number of children a node has.
- **Subtree** — any node plus all its descendants, which is itself a valid tree. **This is why almost every tree algorithm is recursive**: the problem restated on a child is the identical problem on a smaller input.

**Height is the number that matters.** Nearly every tree operation walks one root-to-leaf path, so its cost is O(height). All the machinery below exists to keep height near log n rather than n.

## Shapes of binary tree

A **binary tree** is the common special case: every node has **at most two children**, conventionally `left` and `right`.

```python
class TreeNode:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None
```

The shape vocabulary gets used loosely in conversation and precisely in problem statements, so it's worth pinning down:

**Full** (or *proper*) — every node has either 0 or 2 children. Never exactly one.

```
      1           Nodes have two children or none.
     / \          Common in expression trees: an operator
    2   3         takes two operands, a literal takes none.
   / \
  4   5
```

**Complete** — every level is full except possibly the last, which fills **left to right** with no gaps.

```
      1           This is the shape a heap maintains, and
     / \          the reason a heap can live in a flat array
    2   3         with no pointers at all: children of index
   / \  /         i sit at 2i+1 and 2i+2, with no holes.
  4  5 6
```

**Perfect** — every internal node has two children and all leaves are at the same depth. A perfect tree of height `h` has exactly `2^(h+1) - 1` nodes.

```
      1           The maximally dense shape. Rare in practice
     / \          (n has to be exactly 2^k - 1), but it's the
    2   3         baseline the others are measured against.
   / \ / \
  4  5 6  7
```

**Balanced** — height is O(log n). The usual strict definition (AVL's) is that for every node, the heights of its two subtrees differ by at most 1.

**Degenerate** (or *pathological*) — every node has one child. Structurally a linked list, and the failure mode every balancing scheme exists to prevent.

```
  1
   \
    2       Height n-1 instead of log n.
     \      Every operation is O(n).
      3
       \
        4
```

Every perfect tree is complete; every complete tree is balanced; **balanced does not imply complete**. Getting these confused is a common interview stumble.

**N-ary trees** drop the two-child limit — each node keeps a list of children instead of `left`/`right`. Filesystems, the DOM, org charts, and JSON are all n-ary. Most binary-tree algorithms port over by swapping `for child in node.children` for the two explicit recursive calls.

## Binary Search Trees (BSTs)

A binary tree with one extra rule: for every node, **everything in its left subtree is smaller and everything in its right subtree is larger.** That single invariant is what makes search fast — at each node you discard half the remaining tree, the same idea as [[05-searching|binary search]] on a sorted array, expressed as pointers instead of index arithmetic.

```python
def bst_search(node, target):
    if node is None or node.value == target:
        return node
    if target < node.value:
        return bst_search(node.left, target)
    return bst_search(node.right, target)
```

```
           8
         /   \
        3     10
       / \      \
      1   6      14
         / \     /
        4   7  13
```

Two consequences worth memorising:

- **Inorder traversal of a BST yields sorted order.** This is the "trick" behind a startling number of tree problems — validating a BST, finding the kth smallest, spotting two swapped nodes.
- **The invariant is about entire subtrees, not immediate children.** Checking only `node.left.value < node.value` is the single most common BST bug: a node deep in the left subtree can still exceed the root and break the tree while every parent-child pair looks fine. Validation has to carry a `(min, max)` range down the recursion.

## When BSTs go wrong, and the trees that fix it

| Operation | Balanced BST | Degenerate (worst case) |
|---|---|---|
| Search | O(log n) | O(n) |
| Insert | O(log n) | O(n) |
| Delete | O(log n) | O(n) |
| Min / max | O(log n) | O(n) |
| Inorder (all nodes) | O(n) | O(n) |

That O(log n) **assumes balance, and a plain BST does nothing to maintain it.** Insert already-sorted data one item at a time and every new node goes right, producing the degenerate tree above — every operation O(n), and you've built an expensive linked list. Sorted input isn't exotic; it's what you get from a database dump, a sorted file, or auto-increment IDs.

Self-balancing trees do extra work on insert and delete to keep height at O(log n) regardless of input order. The mechanism is the **rotation** — a local rearrangement of three nodes that changes height without breaking the BST invariant:

```
    right rotation on 5
        5                 3
       / \               / \
      3   D     ->      A   5
     / \                   / \
    A   C                 C   D

  A < 3 < C < 5 < D holds before and after.
```

**AVL trees** — strictly balanced: every node's subtree heights differ by at most 1, enforced by rotating on the way back up from each insert or delete. Tightest height, so the fastest lookups; the strictness means more rotations on write. Choose when reads dominate writes.

**Red-Black trees** — each node is red or black, with rules (no red node has a red parent; every root-to-leaf path has the same number of black nodes) that guarantee the longest path is at most twice the shortest. Looser than AVL, so taller trees and slightly slower lookups, but **far fewer rotations per write**. This is the pragmatic default and what you're actually using: Java's `TreeMap`, C++'s `std::map`, and the Linux kernel's process scheduler are all red-black trees.

**B-trees and B+ trees** — the ones that matter most in production, and the reason this section exists. They aren't binary: **each node holds many keys and has many children**, so a node is sized to fill one disk page or block.

The motivation is that the bottleneck isn't comparisons, it's **disk reads**. A binary tree over 10⁹ records is ~30 levels deep, so a lookup is ~30 random disk seeks. A B-tree with a few hundred keys per node is 3–4 levels deep over the same data — **3 seeks instead of 30**, because each read pulls in hundreds of keys at once. Height reduction is the entire game.

**Practically every database index and filesystem is a B+ tree**: Postgres, MySQL's InnoDB, SQLite, ext4, NTFS. B+ trees additionally keep all values in the leaves and link the leaves together, which makes range scans (`WHERE created_at BETWEEN ...`) a linear walk instead of a repeated descent — the reason range queries on an indexed column are fast.

| Tree | Balance rule | Best at | Where you'll meet it |
|---|---|---|---|
| **Plain BST** | none | teaching | your own code, and only with random input |
| **AVL** | subtree heights differ ≤ 1 | read-heavy workloads | in-memory indexes, databases with rare writes |
| **Red-Black** | longest path ≤ 2× shortest | mixed read/write | `TreeMap`, `std::map`, Linux scheduler |
| **B / B+ tree** | many keys per node, fixed depth | disk and page-based storage | **every database index**, filesystems |

**Other trees worth knowing by name:** [[08-heaps|heaps]] (a complete binary tree ordered parent-vs-child rather than left-vs-right — priority, not search), [[09-tries|tries]] (branching on characters of a key, for prefix queries), segment and Fenwick trees (range queries over a mutable array — the answer to the "prefix sums can't handle updates" problem in [[01-prefix-sum|prefix sum]]), and Merkle trees (nodes are hashes of their children, so any change propagates to the root — the basis of git commits, blockchains, and rsync).

## Where trees actually show up

- **Database indexes and filesystems** — B+ trees, as above. This is the highest-impact one by far.
- **The DOM** — an n-ary tree; every CSS selector match and DOM query is a tree traversal.
- **Compilers** — source parses into an abstract syntax tree, then every optimisation pass is a tree walk. See [[foundations/compilers/README|compilers]].
- **Git** — commits form a DAG, but each commit's snapshot is a Merkle tree of directories and blobs.
- **Routing, autocomplete, decision trees, scene graphs** — anywhere data is naturally hierarchical or needs ordered access.

## Traversal

Visiting every node has its own standard orders — preorder, inorder, postorder, level-order — covered in [[02-traversal|traversal]], since the same idea generalises to graphs.

## Gotchas

- **Balance is not automatic.** A plain BST silently degrades to O(n) on sorted or adversarial insertion order. If you need the guarantee, you need a self-balancing tree — or just use the language's built-in ordered map, which already is one.
- **Validating a BST needs a range, not a parent comparison.** Pass `(min, max)` bounds down; comparing each node only to its immediate parent accepts invalid trees.
- **Height vs depth**, and whether a single node has height 0 or 1. Conventions differ between sources — state yours before you start counting.
- **Recursion depth is the tree's height**, so a degenerate tree blows the call stack where a balanced one is fine. O(log n) stack space in theory, O(n) in the failure case.
- **Complete ≠ balanced ≠ full ≠ perfect** — see the shapes above.
- **Deleting from a BST has three cases**, and the two-child case is the one people botch: replace the node with its inorder successor (leftmost node of the right subtree), then delete *that*.

## Related
- [[02-traversal|traversal]] — pre/in/post/level-order, and picking the right one
- [[06-graphs|graphs]] — a tree is a connected acyclic graph; graphs drop both constraints
- [[04-linked-lists|linked lists]] — the one-child degenerate case, which is also the BST failure mode
- [[08-heaps|heaps]] — a complete binary tree with a different ordering invariant
- [[09-tries|tries]] — trees branching on key characters
- [[05-searching|searching]] — binary search is the array version of a BST descent
- [[10-binary-tree-traversal-pattern|binary tree traversal pattern]] — choosing an order per problem
- [[databases/README|databases]] — where B+ trees do their real work

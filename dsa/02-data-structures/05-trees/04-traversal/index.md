# Traversal

**Visiting every node in a tree, and the fact that the order is a choice.**

A tree holds its data in a shape, not in a sequence. So the moment you want to *do* something to every node — print them, sum them, free them, write them to a file — you have to pick an order to meet them in. **There are four standard answers, they all cost $O(n)$, and they are not interchangeable.** Choosing the wrong one gives you code that nearly works, which is the most expensive kind.

## The lessons

1. [[01-depth-first-traversals|Depth-First Traversals]] — **[Intermediate]** — pre-order, in-order and post-order: the three orders that go deep before going wide. Each one recursively **and** iteratively with an explicit stack, including the two standard tricks for iterative post-order
2. [[02-level-order-traversal|Level-Order Traversal]] — **[Intermediate]** — the one that is not depth-first: a queue instead of a stack, and the level-by-level sweep that falls out of it

## The thread through both

**The three depth-first orders are the same algorithm with the visit moved.** Pre-order visits the node before its subtrees, in-order between them, post-order after. That is the entire difference, and everything else — which problems each one solves, which is awkward to write iteratively — follows from it.

**How you choose between them is not a matter of taste.** It is decided by which way the information flows:

1. If a node's answer depends on what is **above** it — its depth, the path taken to reach it — you need the answer before you descend, so go **top-down with pre-order**.
2. If a node's answer depends on what is **below** it — its height, the size of its subtree, whether it is balanced — you need the children's answers first, so go **bottom-up with post-order**.
3. If you want the values of a [[../03-binary-search-trees|binary search tree]] in sorted order, that is **in-order**, and it is the property the whole structure exists to provide.
4. If you care about distance from the root — the shallowest node matching something, or a level-by-level view — you need **level-order**, and a queue.

**Recursion is a stack you did not have to write.** Both lessons make that concrete: the iterative versions do exactly the same work as the recursive ones, with the bookkeeping moved from the call stack into a list you control. It matters because the call stack is small and fixed, and a list is not — which is why a 3,000-node chain crashes one version and not the other.

## Related

- [[../02-binary-trees|Binary Trees]] — the structure being walked
- [[../03-binary-search-trees|Binary Search Trees]] — where in-order earns its place
- [[../../07-stacks-and-queues|Stacks and Queues]] — the stack and the queue these are built on
- [[01-depth-first-search|Depth-First Search]] · [[02-breadth-first-search|Breadth-First Search]] — the same two ideas on a general graph, where cycles mean you also need a visited set
- [[../index|the trees folder]]

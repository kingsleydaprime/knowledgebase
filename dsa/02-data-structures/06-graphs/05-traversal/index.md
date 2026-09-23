# Traversal

**Visiting every vertex of a graph, and the fact that the order is a choice — and that the choice leaves evidence behind.**

A graph, unlike a [[05-trees/01-trees|tree]], has no root, no top, no natural first element, and — the part that changes everything — **no guarantee that you will not come back to where you started.** So traversing a graph needs one thing tree traversal does not: a record of where you have already been. Everything else in this folder follows from that.

> **Why this folder mirrors [[04-traversal/index|the tree traversal folder]] but is not the same material.** Tree traversal is about *order*: the same walk with the visit moved to a different moment. Graph traversal is about *order plus state*: which vertices are done, which are still open, and what the search learns from meeting one of each. The extra state is the whole difficulty, and it is also where cycle detection, topological sort and connected components come from.

## The lessons

1. [[01-depth-first-search|Depth-First Search]] — **[Intermediate]** — go deep, backtrack. The recursive form and the explicit-stack form, pre- and post-order on a graph, counting connected components, cycle detection in both graph kinds — and a demonstration of the recursive version dying on a 5,000-vertex path where the iterative one is fine.
2. [[02-breadth-first-search|Breadth-First Search]] — **[Intermediate]** — go wide by level, with a queue. Why the first path it finds has the fewest edges, path reconstruction from a parent map, and a lab where BFS returns the **heavier** of two equal-length paths because it never looks at weight.
3. [[03-traversal-trees-and-edge-classification|Traversal Trees and Edge Classification]] — **[Intermediate]** — what the search *leaves behind*: discovery and finish times, the parenthesis theorem, tree/back/forward/cross edges, and the proof that a back edge and a directed cycle are the same thing.

## The thread through all three

**Both searches are the same algorithm with a different container.** Take vertices out of a stack and you get DFS; take them out of a queue and you get BFS. Nothing else changes — same visited set, same $O(V+E)$ cost, same loop. That is worth internalising before the differences, because it means the differences all trace to one line of code.

**The visited set is not an optimisation, it is what makes the algorithm terminate.** On a tree you can omit it and still finish, because there is exactly one path to every node. On a graph with a cycle, omitting it is an infinite loop. This is the single most common way graph code fails.

**One bit of state is not always enough.** "Visited" merges two genuinely different situations — *still on the current path* and *finished and left behind* — and on a directed graph, telling them apart is the difference between detecting a real cycle and rejecting a valid dependency order. Lesson 3 is about the extra state that fixes this, and about how much structure falls out of it.

**Which one to reach for:**

1. If you need the path with the **fewest edges**, you need **BFS**. DFS will happily return a fifty-hop route when a one-hop route exists, and no amount of tweaking fixes that.
2. If you need to know whether *any* path exists, or to touch everything once, either works — use **DFS**, because it is shorter to write and uses $O(d)$ memory on a deep graph where BFS uses $O(\text{width})$.
3. If a vertex's answer depends on the answers of everything reachable from it — subtree sizes, "can I reach a dead end from here", topological position — you need **post-order DFS**, so the children finish first.
4. If the edges have **weights**, neither one is correct. BFS counts edges, not cost. That is [[02-dijkstra|Dijkstra]], which is BFS with the queue replaced by a [[08-heaps|min-heap]].
5. If you need to know *why* the graph has the structure it has — cycles, components, valid orderings — you need the **timestamps and edge classification** of lesson 3.

## What is verified

Every lab in this folder was executed and its expected output generated from that run:

| Lesson | What the lab demonstrates |
| :--- | :--- |
| [[01-depth-first-search\|DFS]] | recursive DFS dying with `RecursionError` on a 5,000-vertex path where the iterative form is fine |
| [[02-breadth-first-search\|BFS]] | BFS returning the heavier of two equal-length paths, because it never looks at weight |
| [[03-traversal-trees-and-edge-classification\|traversal trees]] | the parenthesis theorem checked over all 30 ordered pairs; back-edge count invariant under changing the start vertex while the forward/cross split is not; undirected DFS producing exactly zero forward and cross edges |

## Question banks

One bank per lesson: micro-questions with the answers hidden behind toggles, for closed-book recall rather than reading. Method explained in [[dsa/02-data-structures/01-arrays-qb|the arrays bank]].

- [[01-depth-first-search-qb|Depth-First Search]]
- [[02-breadth-first-search-qb|Breadth-First Search]]
- [[03-traversal-trees-and-edge-classification-qb|Traversal Trees & Edge Classification]]

---

## Related

- [[06-graphs/index|the graphs folder]] — the vocabulary these are written in
- [[06-algorithms/index|graph algorithms]] — what you build on top of a traversal
- [[04-traversal/index|tree traversal]] — the same two ideas without cycles, where the visited set is unnecessary
- [[07-stacks-and-queues|Stacks and Queues]] — the stack and the queue that separate the two searches
- [[11-dfs-pattern|DFS pattern]] · [[12-bfs-pattern|BFS pattern]] — the problem-recognition layer above

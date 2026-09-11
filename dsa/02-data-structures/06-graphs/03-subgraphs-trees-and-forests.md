# Module: Subgraphs, Trees and Forests

**[Intermediate]** — the pieces of a graph, and the exact point at which a graph becomes a tree.

## Before you start

- You know paths, cycles and connectivity — [[02-paths-cycles-and-connectivity|paths, cycles and connectivity]].
- You have met trees as a data structure — [[05-trees/01-trees|trees]]. This lesson explains where they come from.

**After this lesson you will be able to:**

1. Distinguish **subgraph, induced subgraph** and **spanning subgraph**.
2. Define a **tree** and a **forest** as graphs, and prove that several very different-looking definitions describe the same thing.
3. Build a **spanning tree**, and say why every connected graph has at least one.
4. Explain the relationship between the graph-theory tree and the rooted tree of the data-structures course.

**Study route:** read the terms, then the tree definitions, attempt the prediction, then run the lab. Block 2 checks four definitions against each other on every small graph.

---

## Why this exists

You have a big graph and want a piece of it: the servers in one datacentre, the roads inside a city, the part of a dependency graph one package touches. That is a **subgraph** — and there are three different notions, which get confused.

Then there is the other direction. A **tree** appeared in this course as a data structure with a root, parents and children. In graph theory a tree is something much barer: a connected graph with no cycles. No root, no ordering, no children. The two are related, and knowing exactly how is the point of the last section — it explains why a tree has $n-1$ edges, why there is exactly one path between any two nodes, and why adding a single edge anywhere creates exactly one cycle.

## Terms used for pieces of a graph

$H$ is a **subgraph** of $G$ when its vertices all come from $G$, its edges all come from $G$, and every edge it keeps still has both of its endpoints present. That last condition is the one people forget: you cannot keep an edge whose endpoint you threw away, because an edge with only one end is not a thing.

There are four worth naming. The two special ones — induced and spanning — vary opposite things, which is the distinction people mix up.

1. **Subgraph**: This is any piece of a graph that is still a graph. You may delete whatever you like — vertices, edges, or both — as long as no edge is left dangling. Think of it as "delete anything".

2. **Induced subgraph**: This is what you get when you pick a set of vertices and then keep **every** edge of the original graph that has both of its ends inside that set. You have no choice about the edges at all — picking the vertices decides them for you. Think of it as "delete only vertices". It is written $G[S]$, where $S$ is the set of vertices you picked.

3. **Spanning subgraph**: This is what you get when you keep **every** vertex and delete only edges. The word **spanning** always means "touches every vertex", and it will come back in a moment with spanning trees. Think of it as "delete only edges".

4. **Clique**: This is an induced subgraph in which every pair of vertices is joined by an edge — a group where everyone is connected to everyone. Finding the largest clique in a graph is NP-hard, which is worth knowing before you try.

## Trees and forests, as graphs

A **forest** is a graph with no cycles. A **tree** is a **connected** forest. So a forest is a disjoint union of trees, one per connected component.

Note what is absent: no root, no parent, no children, no left and right. A graph-theoretic tree is just "connected and acyclic". Everything else is added later.

### The equivalent definitions

This is the theorem worth knowing. For a graph $G$ with $n$ vertices, **all of the following say the same thing**:

1. $G$ is connected and has no cycles.
2. $G$ is connected and has exactly $n - 1$ edges.
3. $G$ has no cycles and has exactly $n - 1$ edges.
4. There is **exactly one** path between every pair of vertices.
5. $G$ is connected, and removing any edge disconnects it — every edge is a bridge.
6. $G$ has no cycles, and adding any new edge creates **exactly one** cycle.

Six descriptions, one object. That is unusual and useful: whichever is easiest to check in your situation, you get the other five for free.

The intuition behind $n-1$: start with $n$ isolated vertices, so $n$ components. Every edge you add without creating a cycle must join two different components, dropping the count by one. To get from $n$ components to $1$ takes exactly $n-1$ such edges.

Definition 4 is the one that connects to data structures. **Exactly one path** between any two nodes is precisely what makes a tree navigable without a visited set — you can never come back to where you started, so there is nothing to guard against.

> [!TIP]
> **Predict before running the lab.** A connected graph has 7 vertices and 9 edges. Is it a tree? How many edges would you have to remove to make it one, and how many different results might you get? Decide before opening the answers.

### Spanning trees

A **spanning tree** of a connected graph is a spanning subgraph that is a tree: all $n$ vertices, $n-1$ edges, no cycles.

Every connected graph has at least one — run BFS (breadth-first search) or DFS (depth-first search) from any vertex and keep only the edges by which you first reached each vertex. That produces $n-1$ edges (one per vertex except the start) and cannot contain a cycle, because each edge reaches a previously-unseen vertex.

Most connected graphs have many. Cayley's formula says the complete graph $K_n$ has $n^{n-2}$ of them — $K_4$ has $16$, $K_5$ has $125$. Choosing the cheapest is the [[12-minimum-spanning-tree|minimum spanning tree]] problem.

## How this relates to the trees folder

The [[05-trees/01-trees|trees data structure]] adds three things to the graph-theory tree:

1. **A root**: One vertex is singled out and called the root. That gives every edge a direction — away from the root — which is what finally makes the words "parent" and "child" mean something.

2. **An order on the children**: Once a node's children are put in a definite order, "left" and "right" become meaningful. A binary search tree needs this; a graph-theoretic tree has no such notion.

3. **Values and an invariant**: The nodes carry data, and a rule is imposed on how that data is arranged — the BST (binary search tree) ordering property, or the heap property, and so on.

**Vocabulary correspondence:**

| Graph theory | Rooted tree |
| :--- | :--- |
| Vertex | Node |
| Degree | Children count $+\ 1$ for the parent (root has no parent) |
| Degree-1 vertex | Leaf (if not the root) |
| Path length | Depth difference |
| Longest path | Related to the **diameter** |
| — | Root, parent, child, sibling, subtree, level, height — all need the rooting |

## Worked example — runnable

**Runnable example:** save as `trees_and_forests.py` in any empty directory and run `python3 trees_and_forests.py`. Standard library only; writes no files.

```python
"""Subgraphs, and the equivalent characterisations of a tree."""
from collections import defaultdict, deque
from itertools import combinations


def build(edges):
    adj = defaultdict(set)
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    return adj


def vertices(adj):
    return sorted(adj)


def induced(adj, keep):
    keep = set(keep)
    return {v: (adj[v] & keep) for v in sorted(keep)}


def spanning_subgraph(adj, edges_to_keep):
    out = {v: set() for v in adj}
    for u, v in edges_to_keep:
        out[u].add(v)
        out[v].add(u)
    return out


def edge_list(adj):
    return sorted({tuple(sorted((u, v))) for u in adj for v in adj[u]})


def is_connected(adj):
    if not adj:
        return True
    start = vertices(adj)[0]
    seen, q = {start}, deque([start])
    while q:
        for w in adj[q.popleft()]:
            if w not in seen:
                seen.add(w)
                q.append(w)
    return len(seen) == len(adj)


def has_cycle(adj):
    seen = set()
    for start in vertices(adj):
        if start in seen:
            continue
        stack = [(start, None)]
        seen.add(start)
        while stack:
            v, parent = stack.pop()
            for w in adj[v]:
                if w == parent:
                    continue
                if w in seen:
                    return True
                seen.add(w)
                stack.append((w, v))
    return False


def count_paths(adj, a, b, visited=None):
    """Every simple path from a to b - exponential, fine for tiny graphs."""
    visited = visited or {a}
    if a == b:
        return 1
    total = 0
    for w in adj[a]:
        if w not in visited:
            total += count_paths(adj, w, b, visited | {w})
    return total


def bfs_spanning_tree(adj, start):
    tree_edges, seen, q = [], {start}, deque([start])
    while q:
        v = q.popleft()
        for w in sorted(adj[v]):
            if w not in seen:
                seen.add(w)
                tree_edges.append(tuple(sorted((v, w))))
                q.append(w)
    return tree_edges


def all_spanning_trees(adj):
    n, es = len(adj), edge_list(adj)
    found = []
    for combo in combinations(es, n - 1):
        cand = spanning_subgraph(adj, combo)
        if is_connected(cand) and not has_cycle(cand):
            found.append(combo)
    return found


if __name__ == "__main__":
    G = build([("A", "B"), ("A", "C"), ("B", "C"), ("C", "D"), ("D", "E")])
    print("Block 1 - three kinds of subgraph")
    print(f"  G: vertices {vertices(G)}, edges {edge_list(G)}")
    ind = induced(G, ["A", "B", "C"])
    print(f"  induced on {{A,B,C}}: edges {edge_list(ind)}  <- ALL edges among them, no choice")
    assert edge_list(ind) == [("A", "B"), ("A", "C"), ("B", "C")]
    span = spanning_subgraph(G, [("A", "B"), ("B", "C"), ("C", "D"), ("D", "E")])
    print(f"  spanning subgraph:   vertices {vertices(span)}, edges {edge_list(span)}")
    assert set(vertices(span)) == set(vertices(G))
    print("  induced = drop vertices; spanning = drop edges, keep every vertex")

    print()
    print("Block 2 - six definitions of a tree, checked against each other")
    tests = {
        "path A-B-C":       [("A", "B"), ("B", "C")],
        "triangle":         [("A", "B"), ("B", "C"), ("C", "A")],
        "star":             [("A", "B"), ("A", "C"), ("A", "D")],
        "two components":   [("A", "B"), ("C", "D")],
        "G above":          [("A", "B"), ("A", "C"), ("B", "C"), ("C", "D"), ("D", "E")],
        "single vertex":    [],
    }
    print("   graph              conn  acyclic  n-1 edges  unique paths  -> tree?")
    for name, es in tests.items():
        g = build(es) if es else {"A": set()}
        n, m = len(g), len(edge_list(g))
        conn, acyc = is_connected(g), not has_cycle(g)
        right_m = (m == n - 1)
        uniq = all(count_paths(g, a, b) == 1 for a, b in combinations(vertices(g), 2))
        if len(vertices(g)) < 2:
            uniq = True
        d1, d2, d3, d4 = conn and acyc, conn and right_m, acyc and right_m, conn and uniq
        print(f"   {name:18} {str(conn):5} {str(acyc):8} {str(right_m):10} {str(uniq):13}"
              f"  -> {d1}")
        assert d1 == d2 == d3 == d4, (name, d1, d2, d3, d4)
    print("  every definition agrees on every graph: they describe the same object")

    print()
    print("Block 3 - a tree has exactly one path between any two vertices")
    tree = build([("A", "B"), ("B", "C"), ("B", "D"), ("D", "E")])
    for a, b in [("A", "E"), ("C", "E"), ("A", "C")]:
        print(f"    paths {a} -> {b}: {count_paths(tree, a, b)}")
        assert count_paths(tree, a, b) == 1
    print("  adding ONE edge creates exactly one cycle:")
    plus = build(edge_list(tree) + [("A", "E")])
    print(f"    after adding A-E: acyclic? {not has_cycle(plus)},"
          f" paths A->E now {count_paths(plus, 'A', 'E')}")
    assert has_cycle(plus)
    assert count_paths(plus, "A", "E") == 2

    print()
    print("Block 4 - every connected graph has a spanning tree")
    st = bfs_spanning_tree(G, "A")
    print(f"  BFS from A gives {st}")
    print(f"    edges: {len(st)} = n-1 = {len(G)-1}")
    tree_g = spanning_subgraph(G, st)
    assert len(st) == len(G) - 1
    assert is_connected(tree_g) and not has_cycle(tree_g)
    print(f"    connected {is_connected(tree_g)}, acyclic {not has_cycle(tree_g)} -> a tree")
    print("  the start vertex changes which tree you get:")
    for s in vertices(G):
        print(f"    from {s}: {bfs_spanning_tree(G, s)}")

    print()
    print("Block 5 - how many spanning trees? Cayley says K_n has n^(n-2)")
    for n in (2, 3, 4, 5):
        kn = build([(chr(65 + i), chr(65 + j)) for i in range(n) for j in range(i + 1, n)])
        found = all_spanning_trees(kn)
        print(f"  K{n}: {len(found):3} spanning trees   n^(n-2) = {n ** (n - 2):3}")
        assert len(found) == n ** (n - 2)
    print(f"  G above has {len(all_spanning_trees(G))} spanning trees "
          f"(it has one cycle, so removing any one of its 3 edges works)")
    assert len(all_spanning_trees(G)) == 3

    print()
    print("trees_and_forests: passed")
```

Expected output:

```
Block 1 - three kinds of subgraph
  G: vertices ['A', 'B', 'C', 'D', 'E'], edges [('A', 'B'), ('A', 'C'), ('B', 'C'), ('C', 'D'), ('D', 'E')]
  induced on {A,B,C}: edges [('A', 'B'), ('A', 'C'), ('B', 'C')]  <- ALL edges among them, no choice
  spanning subgraph:   vertices ['A', 'B', 'C', 'D', 'E'], edges [('A', 'B'), ('B', 'C'), ('C', 'D'), ('D', 'E')]
  induced = drop vertices; spanning = drop edges, keep every vertex

Block 2 - six definitions of a tree, checked against each other
   graph              conn  acyclic  n-1 edges  unique paths  -> tree?
   path A-B-C         True  True     True       True           -> True
   triangle           True  False    False      False          -> False
   star               True  True     True       True           -> True
   two components     False True     False      False          -> False
   G above            True  False    False      False          -> False
   single vertex      True  True     True       True           -> True
  every definition agrees on every graph: they describe the same object

Block 3 - a tree has exactly one path between any two vertices
    paths A -> E: 1
    paths C -> E: 1
    paths A -> C: 1
  adding ONE edge creates exactly one cycle:
    after adding A-E: acyclic? False, paths A->E now 2

Block 4 - every connected graph has a spanning tree
  BFS from A gives [('A', 'B'), ('A', 'C'), ('C', 'D'), ('D', 'E')]
    edges: 4 = n-1 = 4
    connected True, acyclic True -> a tree
  the start vertex changes which tree you get:
    from A: [('A', 'B'), ('A', 'C'), ('C', 'D'), ('D', 'E')]
    from B: [('A', 'B'), ('B', 'C'), ('C', 'D'), ('D', 'E')]
    from C: [('A', 'C'), ('B', 'C'), ('C', 'D'), ('D', 'E')]
    from D: [('C', 'D'), ('D', 'E'), ('A', 'C'), ('B', 'C')]
    from E: [('D', 'E'), ('C', 'D'), ('A', 'C'), ('B', 'C')]

Block 5 - how many spanning trees? Cayley says K_n has n^(n-2)
  K2:   1 spanning trees   n^(n-2) =   1
  K3:   3 spanning trees   n^(n-2) =   3
  K4:  16 spanning trees   n^(n-2) =  16
  K5: 125 spanning trees   n^(n-2) = 125
  G above has 3 spanning trees (it has one cycle, so removing any one of its 3 edges works)

trees_and_forests: passed
```

Block 2 is the theorem made concrete: four of the six definitions computed independently on six different graphs, and they agree every time. Block 5 confirms Cayley's formula up to $K_5$ by exhaustive search.

## Common pitfalls and traps

- **Confusing induced with spanning.** Induced keeps all edges among the chosen vertices; spanning keeps all vertices and drops edges. They vary opposite things.
- **Assuming a tree needs a root.** In graph theory it does not. Rooting is an extra choice, and any vertex will do.
- **Thinking $n-1$ edges implies a tree.** Only with connectedness *or* acyclicity as well. A triangle plus an isolated vertex has 4 vertices and 3 edges and is not a tree.
- **Forgetting a forest can be a single tree.** "Forest" means acyclic; connected forests are trees. A tree is a forest.
- **Assuming the spanning tree is unique.** It usually is not, and which one you get depends on the traversal and the start vertex — block 4 shows five different trees from one graph.
- **Using Cayley's formula on non-complete graphs.** $n^{n-2}$ counts spanning trees of $K_n$ only. For a general graph use Kirchhoff's matrix-tree theorem.

## Check your understanding

1. A tree has 12 vertices. How many edges?
2. A forest has 15 vertices and 3 components. How many edges?
3. Is a graph with 5 vertices and 4 edges necessarily a tree?
4. How many spanning trees does a cycle on $n$ vertices have?
5. Why does adding any edge to a tree create exactly one cycle?

<details><summary>Answers — open only after an attempt</summary>

1. $12 - 1 = 11$.
2. Each component with $k$ vertices has $k-1$ edges, so the total is $15 - 3 = 12$.
3. **No.** It could be a triangle plus a separate single edge — 5 vertices, 4 edges, disconnected and containing a cycle. The count alone is not enough; you need connectedness or acyclicity too.
4. **$n$.** Removing any single edge from the cycle leaves a path, which is a spanning tree, and there are $n$ edges to choose from.
5. Because a tree already has exactly one path between the endpoints of the new edge. The new edge gives a second route between them, and those two routes together form exactly one cycle. No more, because any additional cycle would need a second pre-existing path, which a tree does not have.

**And the prediction from the tree definitions:** it is **not** a tree — a tree on 7 vertices has exactly 6 edges, and this has 9. You must remove $9 - 6 = 3$ edges, each breaking a cycle without disconnecting the graph. There are generally **many** possible results: the graph has several spanning trees, and which one you get depends on which edges you drop.
</details>

## Practice — independent task

Implement `count_spanning_trees(graph)` two ways and check them against each other.

1. **Brute force:** enumerate all $\binom{m}{n-1}$ edge subsets and count the trees. Correct, and useless past about 20 edges — measure where it becomes too slow on your machine and report the number.
2. **Kirchhoff's matrix-tree theorem:** build the Laplacian $L = D - A$ ($D$ the degree matrix, $A$ the adjacency matrix), delete any one row and column, and take the determinant of what remains. That is the spanning tree count.
3. Assert the two agree on every graph small enough for brute force, including $K_3$ through $K_6$, cycles, paths and trees.
4. Verify **Cayley's formula** with the fast method for $n$ up to 8 or so: $K_n$ should give $n^{n-2}$.
5. Note something interesting: the theorem says "delete **any** one row and column". Verify that the determinant is the same whichever you delete, and say what that tells you about the Laplacian.

**Edge cases:** a disconnected graph (spanning tree count is 0 — does your Laplacian method give that?); a single vertex; a graph with a self-loop (which should not affect the count — check your Laplacian handles it).

**Done when:** both methods agree everywhere brute force is feasible, Cayley's formula checks out to $n=8$, and you can state what the disconnected case gives and why.

## Before moving on

You can distinguish the three subgraph kinds, state and use the tree characterisations, build a spanning tree, and explain how the graph tree relates to the rooted one.

**Recap:** subgraph = any sub-piece; **induced** = pick vertices, keep all their edges; **spanning** = keep all vertices, drop edges; forest = acyclic, tree = connected acyclic; a tree on $n$ vertices has $n-1$ edges, exactly one path between any pair, every edge a bridge, and adding any edge makes exactly one cycle; every connected graph has a spanning tree, usually many; $K_n$ has $n^{n-2}$.

**Next:** [[04-representations|Representations]] — the five ways to store all of this, and how to choose.

## Related

- [[05-trees/01-trees|Trees (data structure)]] — what rooting adds
- [[12-minimum-spanning-tree|Minimum Spanning Tree]] — choosing the cheapest spanning tree
- [[10-union-find|Union-Find]] — the structure Kruskal's algorithm needs
- [[02-discrete-math/07-graph-theory|Discrete maths: graph theory]] — proofs of the characterisations

# Module: What a Graph Is

**[Beginner]** — vertices, edges, and the vocabulary that every later graph result is stated in.

## Before you start

- You know what an array and a hash map are — [[01-arrays|arrays]], [[03-hash-maps|hash-maps]].
- Helpful: [[02-discrete-math/07-graph-theory|discrete maths: graph theory]], which proves what this course uses.

**After this lesson you will be able to:**

1. Define **vertex, edge, incident, adjacent** and **degree**, and use them precisely.
2. Distinguish **simple graph, multigraph, self-loop** and **parallel edges**, and say which your code assumes.
3. Classify any graph along the four dimensions: **directed/undirected, weighted/unweighted, cyclic/acyclic, connected/disconnected**.
4. State and verify the **handshake lemma**.

**Study route:** read 1–4, attempt the prediction in section 3, then run the lab.

---

## 1. Why this exists

A graph is the structure you reach for when **the relationships matter as much as the things**. Cities and roads. Users and follows. Tasks and dependencies. Web pages and links.

Arrays and trees both impose a shape: an array is a line, a tree is a hierarchy with one path between any two nodes. A graph imposes nothing — any node may connect to any other, in either direction, possibly more than once. That freedom is why graphs model so much, and why the vocabulary has to be exact: without agreed terms, "is there a path?" is four different questions.

This lesson is almost entirely definitions. That is deliberate. Nearly every confusion later in this folder traces back to a term used loosely here.

## Terms used in graphs

These are all the words the rest of this folder is written in. None of them are hard, but they are used precisely, so it is worth reading them once slowly.

1. **Vertex**: This is also known as a **node**. This is a point in a graph that can be connected to other points by edges. If the graph is a map, a vertex is a city.

2. **Edge**: This is also known as an **arc** or a **link**. This is a connection or line between two vertices. If a vertex is a city, an edge is a road between two cities.

3. **Endpoints**: An endpoint is one of the two vertices that are connected by a particular edge. Every edge has exactly two of them, and that fact is used more often than you would expect.

4. **Incident**: This is the relationship between a vertex and an edge. If a vertex is an endpoint of an edge, then the vertex and the edge are incident to each other.

5. **Adjacent**: This is also called being **neighbours**. Adjacent vertices are two nodes that are connected by the same edge, and adjacent edges are two edges that connect to the same vertex.

6. **Degree**: The degree of a vertex is the number of edges connected to it. It is written $\deg(v)$. A self-loop is the one exception worth remembering — it counts **twice**, because both of its ends are attached to the same vertex.

7. **In-degree and out-degree**: In-degree is the number of edges coming in to a vertex, and out-degree is the number of edges leaving it. These only mean something in a directed graph, where edges have a direction.

8. **Self-loop**: This is an edge that connects a vertex to itself. A web page that links to itself is a self-loop.

9. **Parallel edges**: These are multiple edges that connect the same pair of vertices. Two separate roads between the same two towns are parallel edges.

10. **Simple graph**: This is a graph with no self-loops and no parallel edges. Most algorithms quietly assume they are given one of these, so it is worth checking that your input really is simple before trusting them.

11. **Multigraph**: This is a graph where parallel edges and self-loops are both allowed. Road networks and circuit diagrams are usually multigraphs.

12. **Weighted graph**: This is a graph where each edge carries a number. That number might be a distance, a cost, a capacity, or a travel time, depending on what you are modelling.

13. **Order and size**: The order of a graph is the number of vertices, written $\lvert V\rvert$. The size is the number of edges, written $\lvert E\rvert$. These are often shortened to $n$ and $m$.

14. **Dense and sparse**: A dense graph has a number of edges close to the maximum possible number of edges. A sparse graph has relatively few edges compared to its number of vertices. Which one you have decides how you should store the graph, which is the whole subject of [[04-representations|lesson 4]].

**Incident and adjacent are not interchangeable.** *Incident* relates an edge to a vertex. *Adjacent* relates two vertices to each other. Textbooks are strict about this and so are exam questions.

## 3. The four dimensions

Every graph question starts by fixing these four. Get one wrong and the algorithm you choose is wrong.

| Dimension        | Options                         | What it changes                             |
| :--------------- | :------------------------------ | :------------------------------------------ |
| **Direction**    | Undirected / directed (digraph) | Whether an edge can be traversed both ways  |
| **Weight**       | Unweighted / weighted           | Whether BFS suffices or you need Dijkstra   |
| **Cycles**       | Cyclic / acyclic                | Whether you need a visited set to terminate |
| **Connectivity** | Connected / disconnected        | Whether one traversal reaches everything    |

An undirected edge $\{u,v\}$ means $u$ and $v$ are mutually adjacent. A directed edge $(u,v)$ means you can go from $u$ to $v$ and says **nothing** about the reverse. "Following" on social media is directed; "friendship" on most platforms is undirected.

### The handshake lemma

The handshaking lemma states that in any undirected graph, the sum of all the vertex degrees is exactly twice the total number of edges. It's a fundamental principle because each edge connects exactly two vertices

$$
\sum_{v \in V} \deg(v) = 2\lvert E\rvert
$$

Every edge contributes exactly two edge-ends — one at each endpoint — so summing degrees counts every edge twice. A self-loop contributes both ends to the same vertex, which is why it adds $2$ to that vertex's degree.

An immediate consequence: **the number of odd-degree vertices is always even.** The total is even, and the even-degree vertices contribute an even amount, so the odd ones must pair up.

> [!TIP]
> **Predict before running the lab.** A simple undirected graph has $6$ vertices. What is the largest possible number of edges? And could such a graph have exactly three vertices of odd degree? Decide before opening the answers.

## 4. Worked example — runnable

**Runnable example:** save as `graph_basics.py` in any empty directory and run `python3 graph_basics.py`. Standard library only; writes no files.

```python
"""Vertices, edges, degree, and the handshake lemma."""
from collections import defaultdict


class Graph:
    """A multigraph: parallel edges and self-loops are allowed and counted."""

    def __init__(self, directed=False):
        self.directed = directed
        self.adj = defaultdict(list)      # vertex -> list of neighbours (with repeats)
        self.edges = []                   # the edge list, as recorded

    def add_vertex(self, v):
        self.adj.setdefault(v, [])
        return self

    def add_edge(self, u, v):
        self.add_vertex(u); self.add_vertex(v)
        self.edges.append((u, v))
        self.adj[u].append(v)
        if not self.directed and u != v:
            self.adj[v].append(u)
        elif not self.directed and u == v:
            self.adj[u].append(v)         # a self-loop adds TWO ends at u
        return self

    def degree(self, v):
        return len(self.adj[v])

    def in_degree(self, v):
        return sum(1 for a, b in self.edges if b == v)

    def out_degree(self, v):
        return sum(1 for a, b in self.edges if a == v)

    def has_self_loop(self):
        return any(u == v for u, v in self.edges)

    def parallel_edges(self):
        seen, dupes = set(), set()
        for u, v in self.edges:
            key = (u, v) if self.directed else tuple(sorted((u, v)))
            if key in seen:
                dupes.add(key)
            seen.add(key)
        return sorted(dupes)

    def is_simple(self):
        return not self.has_self_loop() and not self.parallel_edges()

    def adjacent(self, u, v):
        return v in self.adj[u]

    def incident_edges(self, v):
        return [e for e in self.edges if v in e]


if __name__ == "__main__":
    print("Block 1 - a small undirected graph")
    g = Graph()
    for u, v in [("A", "B"), ("A", "C"), ("B", "C"), ("C", "D")]:
        g.add_edge(u, v)
    print(f"  vertices {sorted(g.adj)}   |V| = {len(g.adj)}, |E| = {len(g.edges)}")
    for v in sorted(g.adj):
        print(f"    deg({v}) = {g.degree(v)}   neighbours {sorted(g.adj[v])}")
    print(f"  A and B adjacent?  {g.adjacent('A', 'B')}")
    print(f"  A and D adjacent?  {g.adjacent('A', 'D')}")
    print(f"  edges incident to C: {g.incident_edges('C')}")
    assert g.adjacent("A", "B") and not g.adjacent("A", "D")
    assert len(g.incident_edges("C")) == 3

    print()
    print("Block 2 - the handshake lemma")
    total = sum(g.degree(v) for v in g.adj)
    print(f"  sum of degrees = {total},  2|E| = {2 * len(g.edges)}")
    assert total == 2 * len(g.edges)
    odd = [v for v in sorted(g.adj) if g.degree(v) % 2 == 1]
    print(f"  odd-degree vertices: {odd}  (there are {len(odd)}, an even number)")
    assert len(odd) % 2 == 0

    print()
    print("  it holds for self-loops too, because a loop adds TWO ends:")
    loopy = Graph().add_edge("X", "X").add_edge("X", "Y")
    for v in sorted(loopy.adj):
        print(f"    deg({v}) = {loopy.degree(v)}")
    print(f"    sum {sum(loopy.degree(v) for v in loopy.adj)} = 2|E| = {2*len(loopy.edges)}")
    assert loopy.degree("X") == 3
    assert sum(loopy.degree(v) for v in loopy.adj) == 2 * len(loopy.edges)

    print()
    print("Block 3 - simple graph vs multigraph")
    multi = Graph()
    for u, v in [("P", "Q"), ("P", "Q"), ("Q", "R"), ("R", "R")]:
        multi.add_edge(u, v)
    for name, gr in [("g    ", g), ("multi", multi)]:
        print(f"  {name}: simple={gr.is_simple()}  self-loop={gr.has_self_loop()}"
              f"  parallel={gr.parallel_edges()}")
    assert g.is_simple()
    assert not multi.is_simple()
    print("  most algorithms assume SIMPLE - check your input before trusting them")

    print()
    print("Block 4 - direction changes the degree question")
    d = Graph(directed=True)
    for u, v in [("A", "B"), ("B", "C"), ("C", "A"), ("A", "C")]:
        d.add_edge(u, v)
    print("    vertex   in   out")
    for v in sorted(d.adj):
        print(f"      {v}      {d.in_degree(v)}    {d.out_degree(v)}")
    tot_in = sum(d.in_degree(v) for v in d.adj)
    tot_out = sum(d.out_degree(v) for v in d.adj)
    print(f"  total in = {tot_in}, total out = {tot_out}, |E| = {len(d.edges)}")
    assert tot_in == tot_out == len(d.edges)
    print("  in a digraph each edge contributes ONE in and ONE out, so both totals are |E|")
    print(f"  A->B exists: {d.adjacent('A','B')};  B->A exists: {d.adjacent('B','A')}")
    assert d.adjacent("A", "B") and not d.adjacent("B", "A")

    print()
    print("Block 5 - how many edges can a simple graph have?")
    print("    |V|   max edges = V(V-1)/2   a 'complete' graph")
    for n in (2, 3, 4, 6, 10):
        print(f"   {n:5}   {n*(n-1)//2:18}")
    complete6 = Graph()
    vs = list(range(6))
    for i in range(6):
        for j in range(i + 1, 6):
            complete6.add_edge(i, j)
    print(f"  built K6: |E| = {len(complete6.edges)}, every degree = "
          f"{sorted({complete6.degree(v) for v in complete6.adj})}")
    assert len(complete6.edges) == 15
    assert all(complete6.degree(v) == 5 for v in complete6.adj)
    print("  density decides representation: K6 is dense, a road network is sparse")

    print()
    print("graph_basics: passed")
```

Expected output:

```
Block 1 - a small undirected graph
  vertices ['A', 'B', 'C', 'D']   |V| = 4, |E| = 4
    deg(A) = 2   neighbours ['B', 'C']
    deg(B) = 2   neighbours ['A', 'C']
    deg(C) = 3   neighbours ['A', 'B', 'D']
    deg(D) = 1   neighbours ['C']
  A and B adjacent?  True
  A and D adjacent?  False
  edges incident to C: [('A', 'C'), ('B', 'C'), ('C', 'D')]

Block 2 - the handshake lemma
  sum of degrees = 8,  2|E| = 8
  odd-degree vertices: ['C', 'D']  (there are 2, an even number)

  it holds for self-loops too, because a loop adds TWO ends:
    deg(X) = 3
    deg(Y) = 1
    sum 4 = 2|E| = 4

Block 3 - simple graph vs multigraph
  g    : simple=True  self-loop=False  parallel=[]
  multi: simple=False  self-loop=True  parallel=[('P', 'Q')]
  most algorithms assume SIMPLE - check your input before trusting them

Block 4 - direction changes the degree question
    vertex   in   out
      A      1    2
      B      1    1
      C      2    1
  total in = 4, total out = 4, |E| = 4
  in a digraph each edge contributes ONE in and ONE out, so both totals are |E|
  A->B exists: True;  B->A exists: False

Block 5 - how many edges can a simple graph have?
    |V|   max edges = V(V-1)/2   a 'complete' graph
       2                    1
       3                    3
       4                    6
       6                   15
      10                   45
  built K6: |E| = 15, every degree = [5]
  density decides representation: K6 is dense, a road network is sparse

graph_basics: passed
```

## Common pitfalls and traps

- **Counting a self-loop once.** It contributes **two** to the degree, and the handshake lemma fails if you count it once.
- **Using "adjacent" for an edge and a vertex.** Vertices are adjacent to vertices; edges are _incident_ to vertices.
- **Assuming a graph is simple.** If your input may contain duplicate edges or self-loops, most textbook algorithms need guarding. Check, or normalise on load.
- **Assuming undirected means "both directions stored".** In an adjacency list it usually does — every undirected edge appears twice. Forgetting that doubles or halves your edge count.
- **Confusing $\lvert E\rvert$ with the adjacency list's total length.** For an undirected simple graph the list holds $2\lvert E\rvert$ entries.

## Check your understanding

1. A graph has degrees $3, 3, 2, 2, 2$. How many edges?
2. Can a simple graph have degrees $4, 3, 3, 2, 2$? Why?
3. What is the maximum number of edges in a simple directed graph on $n$ vertices, allowing both directions but no self-loops?
4. Explain the difference between incident and adjacent in one sentence each.
5. Why does a self-loop add 2 to the degree?

<details><summary>Answers — open only after an attempt</summary>

1. Sum of degrees $= 12 = 2\lvert E\rvert$, so $\lvert E\rvert = 6$.
2. Sum $= 14$, so $\lvert E\rvert = 7$ — an integer, so the handshake lemma is satisfied. And the maximum degree $4$ is at most $n - 1 = 4$. So **yes**, such a simple graph can exist.
3. $n(n-1)$ — every ordered pair of distinct vertices, which is twice the undirected maximum.
4. An edge is **incident** to the two vertices it joins. Two vertices are **adjacent** when an edge joins them.
5. Because degree counts _edge-ends_ at a vertex, and a self-loop has both of its ends at the same vertex.

**And the prediction from section 3:** the maximum is $\binom{6}{2} = 15$ edges — the complete graph $K_6$, where every pair is joined. And **no**, it cannot have exactly three odd-degree vertices: the degree sum must be even, so odd-degree vertices always come in pairs.
</details>

## Practice — independent task

Implement `degree_sequence(graph)` and `is_graphical(sequence)`.

1. `degree_sequence` returns the degrees sorted descending — a basic fingerprint of a graph's shape.
2. `is_graphical` decides whether a given sequence of non-negative integers can be the degree sequence of some **simple** graph. Implement the **Erdős–Gallai** condition, or the **Havel–Hakimi** algorithm (repeatedly remove the largest degree $d$ and subtract 1 from the next $d$ entries).
3. Assert the two necessary conditions first: the sum is even, and no degree exceeds $n-1$. Show a sequence that passes both and is still not graphical, proving they are not sufficient.
4. When a sequence _is_ graphical, **construct** a graph realising it, and verify with `degree_sequence`.
5. Test on: $(3,3,2,2,2)$, $(4,3,3,2,2)$, $(5,1,1,1,1,1)$, $(3,3,3,1)$, and $(1,1)$.

**Edge cases:** the empty sequence; all zeros; a single vertex with degree 0; a sequence containing a negative number.

**Done when:** every graphical sequence is realised by a graph you built, every non-graphical one is rejected with the reason, and you can give a sequence that satisfies both necessary conditions yet is not graphical.

## Before moving on

You can define every term in the terms list without hesitating, state the handshake lemma and why odd-degree vertices come in pairs, and classify a graph along all four dimensions.

**Recap:** vertices and edges; edges are _incident_, vertices are _adjacent_; degree counts edge-ends, and a self-loop counts twice; simple = no loops, no parallel edges; the four dimensions are direction, weight, cycles, connectivity; $\sum\deg(v) = 2\lvert E\rvert$; a simple graph on $n$ vertices has at most $\binom{n}{2}$ edges.

**Next:** [[02-paths-cycles-and-connectivity|Paths, Cycles and Connectivity]] — what it means to get from one vertex to another, and the four different things "connected" can mean.

## Related

- [[02-discrete-math/07-graph-theory|Discrete maths: graph theory]] — the proofs behind these facts
- [[04-representations|Representations]] — how to store all of this
- [[05-trees/01-trees|Trees]] — the special case with no cycles

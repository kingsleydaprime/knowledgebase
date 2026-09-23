# Subgraphs, Trees and Forests — Question Bank

Micro-questions over [[03-subgraphs-trees-and-forests|the subgraphs and trees module]]. Answer in a full sentence before opening the toggle. Format explained in [[dsa/02-data-structures/01-arrays-qb|the arrays bank]].

---

## A. Subgraphs

**1. When is $H$ a subgraph of $G$?**

<details><summary>Answer</summary>

When its vertices all come from $G$, its edges all come from $G$, and **every edge it keeps still has both endpoints present**.

</details>

**2. Which condition do people forget, and why does it matter?**

<details><summary>Answer</summary>

The dangling-edge condition. You cannot keep an edge whose endpoint you threw away — an edge with only one end is not a thing.

</details>

**3. Summarise a plain subgraph in three words.**

<details><summary>Answer</summary>

"Delete anything" — vertices, edges, or both, as long as nothing dangles.

</details>

**4. What is an induced subgraph?**

<details><summary>Answer</summary>

Pick a set of vertices $S$; keep **every** edge of $G$ with both ends inside $S$. You have no choice about the edges — picking the vertices decides them. Written $G[S]$.

</details>

**5. Summarise an induced subgraph in three words.**

<details><summary>Answer</summary>

"Delete only vertices."

</details>

**6. What is a spanning subgraph?**

<details><summary>Answer</summary>

Keep **every** vertex and delete only edges.

</details>

**7. Summarise a spanning subgraph in three words.**

<details><summary>Answer</summary>

"Delete only edges."

</details>

**8. What does the word "spanning" always mean?**

<details><summary>Answer</summary>

**Touches every vertex.** Same meaning in "spanning subgraph" and "spanning tree".

</details>

**9. Induced vs spanning — what is the distinction people mix up?**

<details><summary>Answer</summary>

They vary **opposite** things. Induced fixes the edges once you choose the vertices; spanning fixes the vertices and lets you choose the edges.

</details>

**10. What is a clique, and what is the catch?**

<details><summary>Answer</summary>

An induced subgraph where every pair of vertices is joined — everyone connected to everyone. Finding the **largest** clique is NP-hard, which is worth knowing before you try.

</details>

---

## B. Trees and forests as graphs

**11. What is a forest?**

<details><summary>Answer</summary>

A graph with no cycles.

</details>

**12. What is a tree, graph-theoretically?**

<details><summary>Answer</summary>

A **connected** forest.

</details>

**13. How does a forest relate to trees?**

<details><summary>Answer</summary>

A forest is a disjoint union of trees, one per connected component.

</details>

**14. What is conspicuously absent from the graph-theoretic definition?**

<details><summary>Answer</summary>

No root, no parent, no children, no left and right. Just "connected and acyclic" — everything else is added later.

</details>

---

## C. The six equivalent definitions

**15. State all six equivalent definitions of a tree on $n$ vertices.**

<details><summary>Answer</summary>

1. Connected and has no cycles.
2. Connected and has exactly $n-1$ edges.
3. Has no cycles and has exactly $n-1$ edges.
4. There is **exactly one** path between every pair of vertices.
5. Connected, and removing any edge disconnects it — every edge is a bridge.
6. Has no cycles, and adding any new edge creates **exactly one** cycle.

</details>

**16. Why is having six equivalent definitions useful?**

<details><summary>Answer</summary>

Whichever is easiest to check in your situation, you get the other five for free.

</details>

**17. Give the intuition for why a tree has exactly $n-1$ edges.**

<details><summary>Answer</summary>

Start with $n$ isolated vertices, so $n$ components. Every edge added without creating a cycle must join two different components, dropping the count by one. Going from $n$ components to 1 takes exactly $n-1$ such edges.

</details>

**18. Which definition connects to data structures, and how?**

<details><summary>Answer</summary>

Definition 4. **Exactly one path** between any two nodes is precisely what makes a tree navigable **without a visited set** — you can never come back to where you started, so there is nothing to guard against.

</details>

**19. A connected graph has 7 vertices and 9 edges. Is it a tree?**

<details><summary>Answer</summary>

No. A tree on 7 vertices has exactly 6 edges; 9 is three too many, so it contains cycles.

</details>

**20. How many edges must you remove to make it one, and how many different results are possible?**

<details><summary>Answer</summary>

Three — down to $n-1 = 6$. Many different results are possible: you must break every cycle, and which edges you drop determines which spanning tree you end up with.

</details>

---

## D. Spanning trees

**21. What is a spanning tree?**

<details><summary>Answer</summary>

A spanning subgraph that is a tree: all $n$ vertices, $n-1$ edges, no cycles.

</details>

**22. Does every connected graph have one, and how do you build it?**

<details><summary>Answer</summary>

Yes. Run BFS or DFS from any vertex and keep only the edges by which you **first reached** each vertex.

</details>

**23. Why does that construction always work?**

<details><summary>Answer</summary>

It produces $n-1$ edges — one per vertex except the start — and cannot contain a cycle, because each kept edge reaches a previously-unseen vertex.

</details>

**24. How many spanning trees does the complete graph $K_n$ have?**

<details><summary>Answer</summary>

$n^{n-2}$, by **Cayley's formula**. $K_4$ has 16; $K_5$ has 125.

</details>

**25. What is the problem of choosing the cheapest one called?**

<details><summary>Answer</summary>

The [[06-minimum-spanning-tree|minimum spanning tree]] problem.

</details>

---

## E. Back to the trees folder

**26. What three things does the tree *data structure* add to the graph-theory tree?**

<details><summary>Answer</summary>

1. **A root** — one vertex singled out.
2. **An order on the children** — which makes "left" and "right" meaningful.
3. **Values and an invariant** — data plus a rule about how it is arranged.

</details>

**27. What does rooting actually do to the edges?**

<details><summary>Answer</summary>

It gives every edge a direction — away from the root — which is what finally makes the words "parent" and "child" mean something.

</details>

**28. Map graph-theory *degree* onto rooted-tree vocabulary.**

<details><summary>Answer</summary>

Degree = number of children $+ 1$ for the parent, with the root having no parent.

</details>

**29. Which rooted-tree words have no graph-theory counterpart at all?**

<details><summary>Answer</summary>

Root, parent, child, sibling, subtree, level, height — all of them need the rooting first.

</details>

**30. What does a degree-1 vertex correspond to?**

<details><summary>Answer</summary>

A leaf — provided it is not the root.

</details>

**31. Summarise the lesson in one sentence.**

<details><summary>Answer</summary>

A tree is "connected and acyclic" six different ways, and everything you know about tree *data structures* comes from choosing a root and an order on top of that.

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

- [[03-subgraphs-trees-and-forests|Subgraphs, Trees and Forests]] — the module
- [[02-paths-cycles-and-connectivity-qb|Paths, Cycles and Connectivity — Question Bank]] — the previous bank
- [[05-trees/01-trees|Trees (data structure)]] — the same object, rooted

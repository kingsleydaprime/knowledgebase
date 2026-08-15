# Sets, Relations and Functions

**[Beginner → Intermediate]** — The vocabulary for describing structure, and the mathematical object a relational database is named after.

## Sets

**An unordered collection of distinct elements.** No duplicates, no order.

$$A = \{1, 2, 3\} \qquad \{1,2,3\} = \{3,1,2\} = \{1,1,2,3\}$$

**That's exactly a `HashSet`** — the language feature is the mathematical object.

**Set-builder notation**, which you also already use:

$$\{x \in \mathbb{Z} \mid x > 0 \wedge x \text{ is even}\}$$

*"The set of integers $x$ such that $x$ is positive and even."* Compare:

```python
{x for x in ints if x > 0 and x % 2 == 0}
```

**Python's set comprehension is set-builder notation with ASCII.** The syntax was borrowed deliberately.

**The standard sets:** $\mathbb{N}$ naturals, $\mathbb{Z}$ integers, $\mathbb{Q}$ rationals, $\mathbb{R}$ reals, $\emptyset$ the empty set.

### Operations

| Operation | Notation | SQL / code |
|---|---|---|
| Union | $A \cup B$ | `UNION` |
| Intersection | $A \cap B$ | `INTERSECT` |
| Difference | $A \setminus B$ | `EXCEPT` |
| Complement | $\bar{A}$ | `NOT IN` |
| Cartesian product | $A \times B$ | `CROSS JOIN` |
| Power set | $\mathcal{P}(A)$ | all subsets |

**Cardinality** $|A|$ is the number of elements.

**Two facts worth carrying:**

$$|\mathcal{P}(A)| = 2^{|A|}$$

**The power set of an $n$-element set has $2^n$ elements** — because each element is independently in or out, one binary choice each. This is why brute-forcing "try every subset" is exponential and why subset problems are hard. → [[foundations/theory-of-computation/07-complexity-classes|Complexity Classes]]

$$|A \times B| = |A| \cdot |B|$$

**Set operations obey the same algebra as logic** — union is $\vee$, intersection is $\wedge$, complement is $\neg$. **De Morgan's laws hold verbatim:**

$$\overline{A \cup B} = \bar{A} \cap \bar{B}$$

That's not a coincidence: both are Boolean algebras. → [[foundations/discrete-math/02-logic|Logic]]

### Infinite sets and countability

A genuinely surprising corner, and it matters for [[foundations/theory-of-computation/06-decidability|decidability]].

**Two sets have the same size if a bijection exists between them.** That definition is uncontroversial for finite sets and produces strange results for infinite ones.

**Countably infinite** — same size as $\mathbb{N}$. **The integers are countable** (list them $0, 1, -1, 2, -2, \ldots$), and so are **the rationals**, despite being dense.

**The reals are not.** **Cantor's diagonal argument:** suppose you could list every real in $[0,1]$. Construct a new number whose $n$th digit differs from the $n$th digit of the $n$th number on your list. It differs from every entry, so it wasn't on the list. Contradiction.

> **Why a programmer should care.** **Programs are countable** — each is a finite string, and finite strings over a finite alphabet are countable. **Functions from $\mathbb{N}$ to $\{0,1\}$ are uncountable.**
>
> **So there are strictly more problems than programs.** Most functions are not computable, and not because we haven't found the algorithm — no algorithm exists. **That's a counting argument, and it's the cleanest way to see why undecidability isn't surprising.**

## Relations

**A relation between $A$ and $B$ is a subset of $A \times B$** — a set of ordered pairs.

That's the whole definition, and it's more general than it sounds. "Less than" on integers is the set of pairs $(a,b)$ with $a < b$. "Is a parent of" is a set of pairs of people.

> **A database table *is* a relation.** Rows are tuples, the table is a subset of the product of its column domains. **This is literally where "relational database" comes from** — Codd's 1970 paper. `SELECT` is projection, `WHERE` is selection, `JOIN` is a restricted product. → [[databases/database-design-reference|Databases]]

### Properties

For a relation $R$ on a set $A$:

| Property | Means | Example |
|---|---|---|
| **Reflexive** | $aRa$ for all $a$ | $=$, $\leq$ |
| **Symmetric** | $aRb \Rightarrow bRa$ | $=$, "is a sibling of" |
| **Antisymmetric** | $aRb \wedge bRa \Rightarrow a=b$ | $\leq$, $\subseteq$ |
| **Transitive** | $aRb \wedge bRc \Rightarrow aRc$ | $=$, $<$, $\subseteq$ |

**These aren't trivia — two combinations define the two most important kinds of structure.**

### Equivalence relations

**Reflexive + symmetric + transitive.** Equality, "same remainder mod $n$", "same connected component".

> **An equivalence relation partitions its set** into disjoint **equivalence classes** covering everything. Partition and equivalence relation are two views of the same thing.

Where it shows up: **hashing** (buckets are classes under "same hash"), **modular arithmetic** ($\mathbb{Z}_n$ is the set of classes), **[[foundations/dsa/04-data-structures/10-union-find|union-find]]** (maintaining classes under merging), **type unification**, and **[[foundations/theory-of-computation/03-regular-languages|the Myhill–Nerode theorem]]**, where states of a minimal automaton *are* equivalence classes.

**And the `equals()` contract in Java or `Eq` in Rust is exactly these three axioms.** Violating transitivity — easy to do with a "fuzzy" comparison — breaks hash sets in ways that look like memory corruption.

### Partial orders

**Reflexive + antisymmetric + transitive.** $\leq$, $\subseteq$, divisibility, "depends on".

**"Partial" because some elements are incomparable.** Under $\subseteq$, $\{1,2\}$ and $\{2,3\}$ have no relationship. In a **total order**, everything is comparable.

**Where it matters:**

- **Dependency graphs.** A build's task order is a partial order, and [[foundations/dsa/05-algorithms/11-topological-sort|topological sort]] extends it to a total order — that's exactly what topological sorting *is*
- **Version constraints**, semver ranges
- **Happens-before in [[architecture/04-distributed-systems/03-time-and-ordering|distributed systems]]** — the canonical partial order. Concurrent events are simply *incomparable*, and Lamport's whole point is that physical time forces a false total order onto a genuinely partial one
- **Lattices** — partial orders where every pair has a least upper bound. The basis of [[architecture/04-distributed-systems/06-crdts-and-conflict-resolution|CRDTs]] and of dataflow analysis in [[foundations/compilers/07-optimisation|compilers]]

### Closures

The **transitive closure** of $R$ adds every pair reachable by a chain. Given "directly depends on", the transitive closure is "depends on, however indirectly".

**Computed by Floyd–Warshall or repeated traversal**, and it's what you want for full dependency resolution or reachability. → [[foundations/dsa/04-data-structures/06-graphs|Graphs]]

## Functions

**A function $f: A \to B$ is a relation where every element of $A$ maps to exactly one element of $B$.**

**"Exactly one" is the whole content.** A relation may pair 5 with three things; a function may not. This is why a function is *deterministic* — same input, same output — and why an impure function isn't a function in this sense.

**Domain** $A$, **codomain** $B$, **range** the subset actually hit.

### Injective, surjective, bijective

| | Means | Consequence |
|---|---|---|
| **Injective** (one-to-one) | distinct inputs → distinct outputs | **no collisions** |
| **Surjective** (onto) | every element of $B$ is hit | range = codomain |
| **Bijective** | both | **invertible** |

**Only bijections have inverses.** That's why:

- **Encryption must be bijective** — otherwise decryption is ambiguous → [[cybersecurity/05-cryptography/02-symmetric-encryption|Symmetric Encryption]]
- **Hash functions are deliberately not injective** — a fixed output size mapping arbitrary inputs *must* collide, by pigeonhole. **Collisions are mathematically guaranteed**; a good hash just makes them hard to find on purpose → [[cybersecurity/05-cryptography/03-hashing-and-integrity|Hashing]]
- **Lossless compression cannot shrink every input.** It's a bijection between the same two countable sets, so if some strings get shorter, others must get longer. **This is a proof, not an engineering limitation** — every "compresses any file by 50%" claim is provably false

**Composition** $(g \circ f)(x) = g(f(x))$ is associative — which is why function pipelines compose freely, and the observation that a monoid of endofunctions underlies a lot of functional programming.

## Where this pays off

**Databases** — the relational model, normalisation (functional dependencies are literally functions between attribute sets), and set operations as query operators.

**Type systems** — a type *is* a set of values, and a function type is a set of functions. Subtyping is $\subseteq$. → [[foundations/compilers/05-type-systems-and-checking|Type Systems]]

**Collections** — `Set`, `Map`, and the `equals`/`hashCode` contract as equivalence-relation axioms.

**Graphs** — a graph is a set of vertices plus a relation on them. → [[foundations/discrete-math/07-graph-theory|Graph Theory]]

**Distributed systems** — partial orders, lattices, and CRDT merge as a least-upper-bound operation.

---

## Related
- [[foundations/discrete-math/05-induction-and-recursion|Induction and Recursion]] — proving things about these structures
- [[foundations/discrete-math/07-graph-theory|Graph Theory]] — relations, drawn
- [[foundations/theory-of-computation/06-decidability|Decidability]] — where countability does real work
- [[foundations/discrete-math/README|Discrete maths map]]

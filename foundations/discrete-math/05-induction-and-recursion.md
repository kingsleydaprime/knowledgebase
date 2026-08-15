# Induction and Recursion

**[Intermediate]** — Two faces of one idea, and the single most important technique in this track for a programmer.

## The idea

**Recursion defines. Induction proves.** They have the same shape because they *are* the same shape.

| | Recursion | Induction |
|---|---|---|
| Base | `if (n == 0) return 1` | prove $P(0)$ |
| Step | `return n * fact(n-1)` | prove $P(k) \to P(k+1)$ |
| Gets you | a value for any $n$ | truth for all $n$ |

> **Write a recursive function and you've written the skeleton of an inductive proof.** Which is why recursive code is easier to reason about than a loop even when it's harder to write — the correctness argument comes with the structure.

## Weak induction

**To prove $P(n)$ for all $n \geq n_0$:**

1. **Base case:** prove $P(n_0)$
2. **Inductive step:** assume $P(k)$ (the *inductive hypothesis*), prove $P(k+1)$

> **Claim:** $1 + 2 + \cdots + n = \dfrac{n(n+1)}{2}$
>
> **Base ($n=1$):** LHS $=1$, RHS $=\frac{1\cdot2}{2}=1$. ✓
>
> **Step:** assume it holds for $k$. Then
> $$\underbrace{1+\cdots+k}_{\text{by hypothesis}} + (k+1) = \frac{k(k+1)}{2} + (k+1) = \frac{(k+1)(k+2)}{2}$$
> which is the formula at $k+1$. $\blacksquare$

**Two things people get wrong:**

**Assuming $P(k)$ is not circular.** You're proving the *implication* $P(k) \to P(k+1)$, and inside an implication you assume the antecedent. You are not assuming what you're proving.

**The base case is not a formality.** Without it the chain has nothing to start from — and you can "prove" false statements. *"All horses are the same colour"* is the classic fallacious induction, and it fails precisely at the step from one horse to two.

## Strong induction

Assume $P(j)$ for **all** $j \leq k$, not just $P(k)$.

**Use it when the step needs to reach further back than one.**

> **Claim:** Every integer $n \geq 2$ has a prime factorisation.
>
> **Step:** let $n > 2$. If $n$ is prime, done. Otherwise $n = ab$ with $1 < a, b < n$. **By strong induction both $a$ and $b$ factorise** — and note that $a$ and $b$ could be anywhere below $n$, so weak induction's single-step hypothesis wouldn't reach them. Multiply the factorisations. $\blacksquare$

**Weak and strong induction are logically equivalent** — each proves the other. **Strong is just more convenient**, and it's the natural fit for divide-and-conquer, where a problem of size $n$ becomes subproblems of size $n/2$.

## Structural induction

**The version that matters most in computing.** Induct over the *structure* of a recursively-defined object rather than over a number.

**A binary tree is either** empty, **or** a node with a left and right subtree. So:

- **Base:** prove $P(\text{empty})$
- **Step:** assume $P(L)$ and $P(R)$, prove $P(\text{node}(L, R))$

> **Claim:** a binary tree with $n$ nodes has $n+1$ null links.
>
> **Base:** empty tree — 0 nodes, 1 null link. ✓
>
> **Step:** a node with subtrees of $n_L$ and $n_R$ nodes has $n_L + n_R + 1$ nodes, and by hypothesis $(n_L+1) + (n_R+1) = n_L+n_R+2$ null links, which is (nodes) + 1. ✓ $\blacksquare$

**This is the workhorse for anything tree-shaped**, which is most of computing: ASTs, JSON, file systems, expression evaluation, [[foundations/compilers/04-asts-and-semantic-analysis|semantic analysis]], and type-soundness proofs.

**It works because algebraic data types are recursively defined**, and it's why [[languages/03-rust/06-structs-enums-and-pattern-matching|pattern matching]] on an enum feels like doing a proof: each arm is a case, and exhaustiveness checking is the compiler verifying you covered every constructor.

## Recurrence relations

A sequence defined in terms of earlier terms.

$$T(n) = 2T(n/2) + n, \qquad T(1) = 1$$

**That's merge sort**: split into two halves, recurse, merge in linear time. **Solving the recurrence gives you the complexity.**

### The Master Theorem

For $T(n) = a\,T(n/b) + f(n)$ — the shape of every divide-and-conquer algorithm:

| Case | Condition | Result |
|---|---|---|
| 1 | $f(n) = O(n^{\log_b a - \epsilon})$ | $T(n) = \Theta(n^{\log_b a})$ |
| 2 | $f(n) = \Theta(n^{\log_b a})$ | $T(n) = \Theta(n^{\log_b a}\log n)$ |
| 3 | $f(n) = \Omega(n^{\log_b a + \epsilon})$, regular | $T(n) = \Theta(f(n))$ |

**The intuition, which is more useful than the cases:** compare the work at the leaves ($n^{\log_b a}$) against the work at the root ($f(n)$). **Whichever dominates, wins**; if they're balanced, you pay a $\log n$ factor for the balance.

**Worked examples worth recognising instantly:**

| Recurrence | Solution | Algorithm |
|---|---|---|
| $T(n)=2T(n/2)+n$ | $\Theta(n\log n)$ | merge sort |
| $T(n)=2T(n/2)+1$ | $\Theta(n)$ | tree traversal |
| $T(n)=T(n/2)+1$ | $\Theta(\log n)$ | binary search |
| $T(n)=T(n-1)+n$ | $\Theta(n^2)$ | worst-case quicksort |
| $T(n)=2T(n-1)+1$ | $\Theta(2^n)$ | towers of Hanoi |

> **The two rows to compare are rows 1 and 2.** Same recursion, different combine cost, and the whole difference between $\Theta(n)$ and $\Theta(n\log n)$ comes from whether merging costs linear time. **That's the kind of thing you can't see by staring at code and can see immediately from the recurrence.** → [[foundations/dsa/05-algorithms/04-sorting|Sorting]]

**The Master Theorem doesn't cover everything** — unequal splits, non-polynomial $f$. Then use the **recursion tree method** (draw the levels, sum the work per level) or **substitution** (guess, verify by induction). The recursion tree is the most intuitive and is usually enough.

## Recursion in practice

**Where the maths meets the machine.**

**Every recursive call costs a stack frame.** Deep recursion overflows the stack — a hard limit around a few thousand frames in Python, more in C but still finite. → [[foundations/os/02-processes-and-threads|Processes and Threads]]

**Tail calls can be optimised away.** If the recursive call is the *last* operation, the frame can be reused, turning recursion into iteration. **Guaranteed in Scheme and functional languages, not guaranteed in C/C++, and absent in Python and the JVM by design.** Don't rely on it unless your language promises it. → [[foundations/compilers/07-optimisation|Optimisation]]

**Naive recursion can be exponentially wasteful.** Fibonacci recomputes the same subproblems:

$$T(n) = T(n-1) + T(n-2) + 1 \quad\Rightarrow\quad \Theta(\phi^n)$$

**Memoisation collapses it to $\Theta(n)$** by ensuring each subproblem is solved once. **That observation is the whole of dynamic programming** — overlapping subproblems plus optimal substructure. → [[foundations/dsa/06-patterns/15-dynamic-programming|Dynamic Programming]]

**Any recursion can be made iterative** with an explicit stack. Sometimes clearer, sometimes much worse. Use recursion when the *data* is recursive.

## Well-founded recursion

**Why does recursion terminate?** Because each call is on something "smaller", and you can't descend forever.

**Formally:** the recursion must be on a **well-founded** partial order — one with no infinite descending chains. $\mathbb{N}$ under $<$ is well-founded; $\mathbb{Z}$ is not, and $\mathbb{R}$ under $<$ on $[0,1]$ is not (you can always halve).

**The practical rule:** identify what decreases and what its floor is. If you can't name it, you may not have termination — **the same variant argument as a loop**, because it's the same argument. → [[foundations/discrete-math/03-proof-techniques|Proof Techniques]]

**And this is why total-functional languages (Coq, Agda, Lean) reject recursion they can't prove terminating.** They must — a non-terminating function would let you "prove" anything, since an infinite loop inhabits every type. It's the Curry–Howard correspondence enforcing itself.

## Where induction shows up

**Loop invariants** — induction on iterations. → [[foundations/discrete-math/03-proof-techniques|Proof Techniques]]

**Algorithm correctness** — every divide-and-conquer proof is strong induction.

**Type soundness** — "well-typed programs don't go wrong" is proved by structural induction on typing derivations. → [[foundations/compilers/05-type-systems-and-checking|Type Systems]]

**Compiler correctness** — induction over the AST.

**Protocol safety** — "this invariant holds in every reachable state" is induction over execution steps. **This is precisely what TLA+ checks**, and what Raft's safety proof does. → [[architecture/04-distributed-systems/08-raft-in-depth|Raft]]

**Recursive data structures** — trees, lists, grammars, JSON. Define recursively, prove structurally.

---

## Related
- [[foundations/discrete-math/03-proof-techniques|Proof Techniques]] — the other methods
- [[foundations/dsa/06-patterns/15-dynamic-programming|Dynamic Programming]] — recursion plus memoisation
- [[foundations/dsa/05-algorithms/01-algorithms|Algorithms]] — where these complexities land
- [[foundations/discrete-math/README|Discrete maths map]]

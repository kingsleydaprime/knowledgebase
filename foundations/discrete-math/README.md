# Discrete Mathematics

The mathematics of things you can count. Logic, proof, sets, induction, counting, graphs and number theory — the one maths course that turns out to be load-bearing for programmers, because **computers are discrete machines**.

**~11,300 words across 8 notes.** Built August 2026 to close a gap found by auditing a standard CS syllabus against this vault. `[reference]`.

> **The pitch:** you have been using all of this for years without the vocabulary. `a && !b` is propositional logic. A loop invariant is induction. A `HashSet` is a set, a database table is a *relation* in the literal mathematical sense, and a dependency graph is a graph. **This track gives names to things you already do**, and the names let you reuse fifty years of results instead of re-deriving them badly.

## Reading order

**02–05 are the core and build in order.** Logic gives the language, proof gives the method, sets give the objects, induction ties them together. **06–08 are applications** and can be read in any order after that.

1. [[foundations/discrete-math/01-why-discrete-math|Why Discrete Math]] — **[Beginner]** — continuous vs discrete, where it's already showing up in your code, and the honest case for and against learning it
2. [[foundations/discrete-math/02-logic|Logic]] — **[Beginner]** — propositions, De Morgan, quantifiers, and **why implication is true when the premise is false**
3. [[foundations/discrete-math/03-proof-techniques|Proof Techniques]] — **[Beginner → Intermediate]** — direct, contrapositive, contradiction, cases, counterexample, and **loop invariants as induction in disguise**
4. [[foundations/discrete-math/04-sets-relations-and-functions|Sets, Relations and Functions]] — **[Beginner → Intermediate]** — the vocabulary of structure, equivalence relations and partial orders, and **why there are more problems than programs**
5. [[foundations/discrete-math/05-induction-and-recursion|Induction and Recursion]] — **[Intermediate]** — weak, strong and structural induction; recurrences and the Master Theorem. **The most important note here**
6. [[foundations/discrete-math/06-combinatorics-and-counting|Combinatorics and Counting]] — **[Intermediate]** — permutations, combinations, pigeonhole, and **the birthday bound that halves your hash's security**
7. [[foundations/discrete-math/07-graph-theory|Graph Theory]] — **[Intermediate]** — the most reusable modelling tool in the subject, and **why "shortest path" is easy while "longest path" is NP-hard**
8. [[foundations/discrete-math/08-number-theory-and-modular-arithmetic|Number Theory and Modular Arithmetic]] — **[Intermediate]** — GCD, primes, modular exponentiation, and **RSA stated completely in eight lines**

## The things worth carrying

1. **$p \to q$ is equivalent to its contrapositive, not its converse.** Confusing a statement with its converse is the most common reasoning error there is → [[foundations/discrete-math/02-logic|02]]
2. **Quantifier order changes the claim.** "For every input there's a fast algorithm" and "there's an algorithm fast on every input" are different questions → [[foundations/discrete-math/02-logic|02]]
3. **Disproving $\forall$ takes one counterexample; proving it takes an argument.** That asymmetry is why finding a bug is easy and proving correctness is hard → [[foundations/discrete-math/03-proof-techniques|03]]
4. **A loop invariant is an inductive proof.** If you can't name the quantity that decreases, you may not have termination → [[foundations/discrete-math/05-induction-and-recursion|05]]
5. **There are more problems than programs** — programs are countable, functions aren't. Undecidability stops being surprising → [[foundations/discrete-math/04-sets-relations-and-functions|04]]
6. **Pigeonhole proves that lossless compression can't shrink every input** and that hash collisions are guaranteed. Both in one line → [[foundations/discrete-math/06-combinatorics-and-counting|06]]
7. **An $n$-bit hash gives $n/2$ bits of collision resistance.** The birthday bound is why SHA-1 fell → [[foundations/discrete-math/06-combinatorics-and-counting|06]]
8. **"Is this a graph problem?" is one of the highest-value questions in problem solving.** The answer is yes more often than expected → [[foundations/discrete-math/07-graph-theory|07]]
9. **Primality testing is easy; factoring is hard.** That single gap is the foundation of RSA — and it's conjectured, not proved → [[foundations/discrete-math/08-number-theory-and-modular-arithmetic|08]]

## Where this connects

| | |
|---|---|
| [[foundations/theory-of-computation/README\|theory of computation]] | **The direct sequel.** Countability, proof and logic are its prerequisites |
| [[foundations/dsa/README\|DSA]] | Recurrences give the complexities; graph theory gives the algorithms |
| [[cybersecurity/05-cryptography/README\|cryptography]] | Number theory, and the birthday bound on key sizes |
| [[foundations/compilers/05-type-systems-and-checking\|type systems]] | Curry–Howard: propositions are types, proofs are programs |
| [[databases/database-design-reference\|databases]] | The relational model is relations, literally |
| [[architecture/04-distributed-systems/03-time-and-ordering\|distributed systems]] | Happens-before is a partial order; quorums are a counting argument |

## The honest note

**`[reference]`, and this domain has an unusually sharp version of that problem.**

**Discrete maths is learned by doing proofs.** Reading a proof is to writing one what reading code is to writing it — you follow along, it all seems reasonable, and then a blank page defeats you. **Every note here shows worked proofs; none of them makes you do one.**

The gap is closable cheaply, and unlike most of this vault it needs no hardware:

- **Prove the things stated here without looking.** The sum formula, $\sqrt2$ irrational, the handshake lemma. An hour with paper
- **Verify a loop invariant** on real code you've written — binary search, or a partition step. Then check it actually holds by instrumenting it
- **[Project Euler](https://projecteuler.net)** for the number theory and combinatorics, since the answers are checkable
- **A proof assistant** — Lean's *Natural Number Game* is genuinely the best entry point available, and it will not let you skip a step
- **The books:** Rosen (standard, exhaustive), Lehman/Leighton/Meyer's *Mathematics for Computer Science* (MIT 6.042, free, better written), Velleman's *How to Prove It* (the one that actually teaches proof)

**What's missing from this track:** exercises, generating functions, deeper probability (it's in [[ai-ml/00-foundations/03-mathematics/03-probability-and-statistics/README|the ML maths notes]]), lattices and order theory in depth, formal proof systems and natural deduction, and any treatment of Boolean algebra as circuit minimisation.

→ [[PRIMETECHIE|Reading is not a rank.]]

## Related
- [[foundations/theory-of-computation/README|Theory of Computation]] — the direct continuation
- [[foundations/dsa/README|Data Structures & Algorithms]] — where this is already applied
- [[foundations/computer-architecture/README|Computer Architecture]] — the other half of the CS-theory gap this batch closed
- [[BUILD-PLAN|Build Plan]]

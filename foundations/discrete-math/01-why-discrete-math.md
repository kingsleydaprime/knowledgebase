# Why Discrete Math

**[Beginner]** — The mathematics of things you can count, and why it's the one maths course that turns out to be load-bearing for programmers.

**Source:** `[reference]` — see [[foundations/discrete-math/README|the domain note]].

## Continuous vs discrete

**Continuous mathematics** — calculus, analysis, differential equations — studies things that vary smoothly. Between any two real numbers there's another. Rates of change, limits, areas under curves.

**Discrete mathematics** studies things that come in separate, countable pieces. Integers, graphs, sets, logical propositions, finite structures. **No limits, no infinitesimals, no smoothness.**

> **Computers are discrete machines.** Finite memory, integer arithmetic, a finite instruction set, a countable number of states. **So the maths that describes them is discrete maths** — which is why this is the mathematics requirement in a CS degree while engineering degrees get calculus.

## Where it's already showing up

The honest pitch for this domain: **you have been using it for years without the vocabulary.**

| You already do | It's really |
|---|---|
| `if (a && !b \|\| c)` | propositional logic → [[foundations/discrete-math/02-logic\|02]] |
| Reasoning about a loop invariant | induction → [[foundations/discrete-math/05-induction-and-recursion\|05]] |
| A hash set, a SQL `JOIN`, a `UNIQUE` constraint | set theory → [[foundations/discrete-math/04-sets-relations-and-functions\|04]] |
| Big-O analysis | asymptotics and recurrences → [[foundations/discrete-math/05-induction-and-recursion\|05]] |
| A dependency graph, a router table, a social graph | graph theory → [[foundations/discrete-math/07-graph-theory\|07]] |
| "How many combinations does this password have?" | combinatorics → [[foundations/discrete-math/06-combinatorics-and-counting\|06]] |
| RSA, Diffie–Hellman, a hash function | number theory → [[foundations/discrete-math/08-number-theory-and-modular-arithmetic\|08]] |
| A type checker rejecting your program | logic, again |
| Normalising a database schema | relations, literally — that's where "relational" comes from |

**None of that is a stretched analogy.** A SQL `JOIN` *is* a relational operation in the mathematical sense. A relational database is named after the mathematical object.

## What this actually buys you

Being honest about the payoff, because "it's foundational" is not an argument.

**1. You can prove things instead of testing them.**

Tests sample the input space. **A proof covers all of it.** For most application code, tests are the right tool — but for a concurrency primitive, a consensus protocol, or a cryptographic construction, "we tested it a lot" is not good enough. [[architecture/04-distributed-systems/02-theoretical-limits|The distributed-systems impossibility results]] are proofs, and no amount of testing would have found them.

**2. You recognise the shape of a problem.**

"This is a graph reachability problem." "This is a bipartite matching." "This is the pigeonhole principle." **Recognising the shape lets you use a known solution instead of inventing a worse one**, and it's the difference between a hard problem and a solved one you didn't recognise.

**3. You can read the literature.**

Papers in algorithms, cryptography, databases, PL and distributed systems are written in this notation. Without it, the field's accumulated knowledge is behind a wall. → [[research/02-reading-papers|Reading Papers]]

**4. You know when something is impossible.**

**This is the most practically valuable one.** Knowing that a problem is NP-complete stops you looking for an efficient exact algorithm and starts you looking for an approximation. Knowing the halting problem is undecidable tells you why your linter can't catch everything. → [[foundations/theory-of-computation/README|Theory of Computation]]

> **The counter-argument, stated fairly:** most working programmers never explicitly use any of this and ship fine software. That's true. **The claim isn't that you can't work without it — it's that certain classes of problem are opaque without it**, and you won't know which ones you're missing.

## The pieces

**Logic** — how to state things precisely and reason validly. The foundation everything else sits on. → [[foundations/discrete-math/02-logic|02]]

**Proof** — how to establish that something is true for all cases. Direct, contradiction, contraposition, induction. → [[foundations/discrete-math/03-proof-techniques|03]]

**Sets, relations, functions** — the vocabulary for describing structure. → [[foundations/discrete-math/04-sets-relations-and-functions|04]]

**Induction and recursion** — the two faces of one idea, and the bridge between defining a structure and proving things about it. → [[foundations/discrete-math/05-induction-and-recursion|05]]

**Combinatorics** — counting without enumerating. → [[foundations/discrete-math/06-combinatorics-and-counting|06]]

**Graph theory** — the single most reusable modelling tool in the subject. → [[foundations/discrete-math/07-graph-theory|07]]

**Number theory** — divisibility, primes, modular arithmetic. Pure mathematics until 1977, then the basis of all public-key cryptography. → [[foundations/discrete-math/08-number-theory-and-modular-arithmetic|08]]

## A worked taste

To show what "recognising the shape" means, three problems that look unrelated and aren't.

**"In any group of 367 people, two share a birthday."**

Obvious. 367 people, 366 possible birthdays, so two must collide. **That's the pigeonhole principle**, and stated generally it proves things that aren't obvious at all — that lossless compression cannot shrink every input, for instance. → [[foundations/discrete-math/06-combinatorics-and-counting|06]]

**"Can this build succeed?"**

A build system has tasks with dependencies. **That's a directed graph**, and "can it succeed" means "is it acyclic". The build order is a topological sort. → [[foundations/dsa/05-algorithms/11-topological-sort|Topological Sort]]

**"Is this program correct?"**

For a loop, you find a property true before it starts, preserved by each iteration, and implying what you want at the end. **That's induction**, dressed as a loop invariant — and it's how you'd argue that binary search is correct rather than testing it on a few arrays.

**Same three tools, over and over.** The subject is small; the applications aren't.

## Reading this track

**02–05 are the core and build in order.** Logic gives you the language, proof gives you the method, sets give you the objects, induction ties them together.

**06–08 are the applications.** Combinatorics, graphs, and number theory can be read in any order once you have 02–05.

**Prerequisites:** none beyond high-school algebra. **This is genuinely the ground floor** — which is why it's the first-year course, and why it's a reasonable entry point even if the rest of the vault's maths (linear algebra, calculus) is unfamiliar.

**What this track is not:** a problem set. Discrete maths is learned by *doing proofs*, and reading proofs is to writing them what reading code is to writing it. The honest note in [[foundations/discrete-math/README|the README]] says more.

---

## Related
- [[foundations/discrete-math/02-logic|Logic]] — the next note, and the foundation
- [[foundations/theory-of-computation/README|Theory of Computation]] — where this leads directly
- [[foundations/dsa/README|Data Structures & Algorithms]] — where it's already being applied
- [[foundations/discrete-math/README|Discrete maths map]]

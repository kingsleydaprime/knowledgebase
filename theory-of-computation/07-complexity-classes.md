# Complexity Classes

**[Advanced]** — P, NP, and the most consequential open question in computer science. Also the most practically useful thing in this track.

## From possible to feasible

[[foundations/theory-of-computation/06-decidability|Decidability]] asks *can it be done at all*. **Complexity asks whether it can be done before the sun burns out.**

**A decidable problem taking $2^n$ steps is decidable and useless.** At $n=100$, $2^{100}$ operations exceeds the number of atomic events in the universe's history.

## P

> **P** — decidable by a deterministic Turing machine in **polynomial time**, $O(n^k)$ for some constant $k$.

**Sorting, shortest path, primality testing, linear programming, matrix multiplication, string matching.**

**Why polynomial is the dividing line**, since $n^{100}$ is hardly "fast":

**It's model-independent.** Turing machine, RAM model, your laptop — **all polynomially related.** So "polynomial" means the same thing in every model, which "under a million steps" does not. **That robustness is the actual justification.**

**It's closed under composition.** A polynomial algorithm calling a polynomial subroutine polynomially often is still polynomial. Exponential isn't stable like that.

**Empirically, natural problems in P have small exponents.** $n^{100}$ algorithms are constructed to make a point; real ones are $n$, $n\log n$, $n^2$, $n^3$.

**The honest caveat:** P is a theoretical convenience, not a practical guarantee. $n^3$ on $n=10^6$ is already infeasible, and an $O(n\log n)$ algorithm with a huge constant may lose to $O(n^2)$. **P vs NP is about asymptotic structure, not about whether your code is fast.** → [[foundations/dsa/05-algorithms/01-algorithms|Algorithms]]

## NP

> **NP** — decidable by a **nondeterministic** TM in polynomial time.
>
> **Equivalently, and more usefully: a *yes* answer has a proof that can be *verified* in polynomial time.**

**The verifier definition is the one to keep.** NP is the class of problems where **finding a solution may be hard, but checking one is easy.**

| Problem | Certificate | Verification |
|---|---|---|
| **SAT** | a satisfying assignment | plug in, evaluate |
| **Hamiltonian cycle** | the cycle | check it visits each vertex once |
| **Subset sum** | the subset | add it up |
| **Graph colouring** | the colouring | check adjacent pairs differ |
| **Factoring** | the factors | multiply |

> **"NP" means nondeterministic polynomial, not "non-polynomial".** A common and confusing misreading. **P ⊆ NP** — anything solvable quickly is verifiable quickly.

**The asymmetry to notice:** NP is about *yes* instances. A certificate proves a formula *is* satisfiable. **Proving it isn't** requires ruling out all $2^n$ assignments — that's **co-NP**, and whether NP = co-NP is also open.

## NP-complete

> **$B$ is NP-complete if $B \in$ NP and every problem in NP reduces to $B$ in polynomial time.**

**The hardest problems in NP.** And the crucial consequence:

$$\text{One NP-complete problem in P} \implies \text{P} = \text{NP}$$

**Cook–Levin (1971):** SAT is NP-complete. **Proved from scratch** by encoding an arbitrary NP machine's computation as a Boolean formula.

**Everything since reduces from SAT.** Karp's 1972 paper gave 21 problems, and thousands are now known:

- **3-SAT**, **CLIQUE**, **VERTEX COVER**, **INDEPENDENT SET**
- **HAMILTONIAN CYCLE**, **TSP** (decision version)
- **SUBSET SUM**, **KNAPSACK**, **BIN PACKING**
- **GRAPH COLOURING** ($k\geq3$)
- **Sudoku**, **Minesweeper**, **Tetris**, generalised to $n\times n$

> **They're all the same problem in disguise.** A polynomial algorithm for any one solves all of them. **That's what makes the class meaningful** — fifty years of collective failure on thousands of problems is the real evidence that P ≠ NP.

**Proving something NP-complete:** show it's in NP (exhibit a certificate), then reduce a known NP-complete problem *to* it. **Direction again** — known-hard → yours.

**NP-hard** — at least as hard as everything in NP, **not necessarily in NP itself.** The optimisation version of TSP ("find the shortest tour") is NP-hard but not in NP, because you can't verify optimality in polynomial time. **The halting problem is NP-hard too**, and undecidable.

## P vs NP

```
   If P ≠ NP (believed)        If P = NP
   ┌─────────────────┐         ┌─────────────┐
   │       NP        │         │             │
   │  ┌───────────┐  │         │  P = NP     │
   │  │  NPC      │  │         │             │
   │  └───────────┘  │         └─────────────┘
   │  ┌───┐          │
   │  │ P │          │
   └──┴───┴──────────┘
```

**Is verifying a solution fundamentally easier than finding one?**

**A Clay Millennium Prize problem. $1,000,000. Open since 1971.**

**Most researchers believe P ≠ NP**, on the evidence that thousands of people have failed at thousands of problems for fifty years.

**If P = NP** — and this is worth spelling out, because it shows what the question really asks:

- **Public-key cryptography collapses.** RSA, ECC, TLS. → [[cybersecurity/05-cryptography/04-asymmetric-encryption|Asymmetric Encryption]]
- **Every optimisation problem becomes tractable.** Logistics, scheduling, protein folding, chip layout
- **Mathematics changes character** — finding a proof of a given length becomes as easy as checking one
- **Machine learning changes** — finding the optimal model becomes feasible

> **The philosophical version:** P = NP would mean **creativity is mechanisable.** Recognising a good proof, a good design, a good solution would be equivalent to producing one. **The widespread belief that P ≠ NP is a belief that finding is genuinely harder than recognising** — which matches every intuition we have about hard work.

**And why it's hard to prove:** several barriers are themselves theorems. **Relativisation** (Baker–Gill–Solovay) shows oracle-based arguments can't settle it. **Natural proofs** (Razborov–Rudich) shows a broad class of circuit-complexity arguments can't either, assuming one-way functions exist. **Algebrization** rules out more. **The known techniques are provably insufficient**, which is unusual and discouraging.

**NP-intermediate:** if P ≠ NP, **Ladner's theorem** says problems exist that are in NP, not in P, and not NP-complete. **Factoring and graph isomorphism are the candidates** — no polynomial algorithm known, no NP-completeness proof either. (Graph isomorphism got a quasi-polynomial algorithm from Babai in 2015, strong evidence it's not NP-complete.)

## What to do with an NP-complete problem

**The practical payoff, and the reason this note is the most useful in the track.**

> **Recognising NP-completeness means: stop looking for an efficient exact general algorithm. It probably doesn't exist.**
>
> **Then pick a relaxation.** You must give up one of: *exact*, *efficient*, *general*. **The engineering question is which.**

**Give up "general" — exploit structure.**

Real instances aren't worst-case. **Modern SAT solvers routinely handle millions of variables** despite exponential worst cases, because real formulas have structure (CDCL, clause learning, good heuristics). **This is the most underrated option** — used for hardware verification, package dependency resolution, and symbolic execution.

Also: many NP-hard problems are polynomial on trees, on bounded-treewidth graphs, or with a fixed parameter (**FPT**: $O(f(k)\cdot n^c)$, feasible when $k$ is small).

**Give up "exact" — approximate.**

Some problems have guaranteed ratios: **vertex cover has a 2-approximation** (take both endpoints of a maximal matching), **metric TSP has 3/2** (Christofides).

**Some resist:** general TSP has no constant-factor approximation unless P=NP, and MAX-CLIQUE is hard to approximate within $n^{1-\epsilon}$. **The PCP theorem** established that inapproximability is itself provable, which is a striking result.

**Give up "efficient" — exponential, but smart.**

Branch and bound, ILP solvers (Gurobi, CPLEX), dynamic programming over subsets ($O(2^n n^2)$ for TSP beats $O(n!)$ dramatically). **Fine when $n$ is small.**

**Use heuristics with no guarantee.** Simulated annealing, genetic algorithms, local search, greedy. **Usually good, occasionally bad, no promises.** Often the right practical answer.

**Or change the problem.** The most valuable move and the most overlooked: **often the NP-hard formulation isn't what the business needs.** "Optimal delivery route" becomes "a good route in under a second" — and that's tractable. **Recognising that the hard constraint is negotiable is worth more than any algorithm.**

## Other classes

| Class | Meaning |
|---|---|
| **L / NL** | logarithmic space |
| **P** | polynomial time |
| **NP** | poly-time verifiable |
| **co-NP** | complement in NP |
| **PSPACE** | polynomial *space*, any time |
| **EXPTIME** | exponential time |

$$\text{L} \subseteq \text{NL} \subseteq \text{P} \subseteq \text{NP} \subseteq \text{PSPACE} \subseteq \text{EXPTIME}$$

**Almost every containment is open**, which is a slightly absurd state of affairs. **We do know $\text{P} \subsetneq \text{EXPTIME}$** (the time hierarchy theorem), so at least one of the intermediate inclusions is strict — **we just can't say which.**

**PSPACE-complete** problems include generalised games (Go, chess on $n\times n$), quantified Boolean formulas, and regular expression equivalence.

**Savitch's theorem:** $\text{NPSPACE} = \text{PSPACE}$. **Nondeterminism doesn't help for space** — a striking contrast with the open question for time, and a hint at why the time question is hard.

---

## Related
- [[foundations/theory-of-computation/08-beyond-p-vs-np|Beyond P vs NP]] — randomness, quantum, approximation
- [[foundations/theory-of-computation/06-decidability|Decidability]] — impossible rather than slow
- [[foundations/dsa/05-algorithms/01-algorithms|Algorithms]] — where complexity is applied
- [[foundations/theory-of-computation/README|Theory of computation map]]

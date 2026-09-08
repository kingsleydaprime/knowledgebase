# Semantics

**[Advanced]** — Saying what a program *means*, precisely enough to prove things about it.

## Why formalise meaning

**A language specified in English is ambiguous.** Real consequences:

**C's undefined behaviour** — the spec says a construct has no defined meaning, and compilers exploit that to delete your null checks. **A formal semantics makes exactly what's guaranteed unambiguous.** → [[languages/04-c/10-undefined-behaviour|Undefined Behaviour]]

**JavaScript's `==`** — the coercion rules are famously surprising *because* they were specified operationally without a guiding principle.

**Memory models** — "what can another thread observe?" is unanswerable without a formal semantics, which is why C++11 and Java both needed one written. → [[foundations/computer-architecture/11-multicore-and-memory-models|Memory Models]]

> **And you cannot prove a compiler correct without one.** "Correct" means *preserves meaning*, so meaning must be defined. **CompCert — a C compiler verified in Coq — required formalising a large subset of C first**, and that formalisation found real ambiguities in the standard.

## Operational semantics

**Define meaning by *how a program executes*** — a state machine.

**Small-step (structural)** — one reduction at a time:

$$\frac{e_1 \to e_1'}{e_1 + e_2 \to e_1' + e_2}
\qquad
\frac{e_2 \to e_2'}{v_1 + e_2 \to v_1 + e_2'}
\qquad
\overline{n_1 + n_2 \to n_1{+}n_2}$$

**Read the first two rules carefully — they *encode left-to-right evaluation order.*** You can only step $e_2$ once $e_1$ is a value $v_1$. **Change the rules and you change the language.**

**This is how you specify evaluation order formally**, and why languages that leave it unspecified (C's function arguments) have a genuinely non-deterministic semantics.

**Big-step (natural)** — straight to the final value:

$$\frac{e_1 \Downarrow n_1 \qquad e_2\Downarrow n_2}{e_1 + e_2 \Downarrow n_1 + n_2}$$

**Simpler, and it cannot distinguish non-termination from getting stuck** — both are just "no derivation exists". **Small-step can**, which is why type-soundness proofs use it.

**Small-step is the standard for language design.** It captures interleaving (essential for concurrency), distinguishes stuck from diverging, and supports progress/preservation proofs.

## Denotational semantics

**Map each program to a mathematical object** — its *denotation*.

$$[\![e]\!] : \text{Env} \to \text{Value}$$

$$[\![e_1 + e_2]\!]\rho = [\![e_1]\!]\rho + [\![e_2]\!]\rho$$

**Compositional: the meaning of a term is built from the meanings of its parts.** No execution, no steps — a program *is* a mathematical function.

**The difficulty is recursion.** What does $\text{let } f = \lambda x.\,f\,x$ denote? **Scott and Strachey solved it with domain theory:** values form a partially ordered set with a bottom element $\bot$ (non-termination), and recursive definitions are **least fixed points** of continuous functions.

> **$\bot$ is the key idea: non-termination is a *value*.** It's the least-defined one, and every recursive definition converges to a least fixed point in that order.
>
> **This is where lattices earn their keep**, and it's the same machinery as [[foundations/discrete-math/04-sets-relations-and-functions|partial orders]] and as dataflow analysis in compilers. → [[foundations/compilers/07-optimisation|Optimisation]]

**Denotational semantics is best for proving *equivalences*** — two programs are equal if their denotations are. **That's exactly what an optimisation must establish.**

## Axiomatic semantics

**Specify what *holds* before and after, not how it runs.**

**Hoare triples:**

$$\{P\}\ C\ \{Q\}$$

**"If $P$ holds and $C$ terminates, $Q$ holds."**

$$\{x = 5\}\quad x := x + 1 \quad\{x = 6\}$$

**The assignment rule runs backwards, which surprises people:**

$$\overline{\{Q[x := e]\}\ x := e\ \{Q\}}$$

**Substitute into the *postcondition* to get the precondition.** Weakest-precondition calculation works from the end of the program to the start.

**The while rule is the important one:**

$$\frac{\{I \wedge B\}\ C\ \{I\}}{\{I\}\ \text{while } B \text{ do } C\ \{I \wedge \neg B\}}$$

> **$I$ is the loop invariant, and this rule *is* [[foundations/discrete-math/05-induction-and-recursion|induction]]** — true before, preserved by each iteration, therefore true at the end.
>
> **Note the triple only promises partial correctness** — "if it terminates". **Termination is a separate obligation** requiring a variant: a quantity that strictly decreases and is bounded below. → [[foundations/discrete-math/03-proof-techniques|Proof Techniques]]

**Where this is used in practice:** design-by-contract (Eiffel, JML, Ada SPARK), and **verification tools** — Dafny, Why3, Frama-C, and the SMT-backed verifiers behind them. **`assert` statements are Hoare postconditions**, informally.

**Separation logic** (O'Hearn, Reynolds, ~2001) extends it to pointers and the heap, with a separating conjunction $P * Q$ meaning "$P$ and $Q$ hold on *disjoint* heap regions".

> **This was the breakthrough that made verifying pointer-manipulating programs tractable** — you can reason about a linked-list operation locally without describing the entire heap. **Facebook's Infer uses it** to find null-dereference and leak bugs at scale, which is a rare case of heavyweight PL theory shipping in a mainstream developer tool.

## Which to use

| | Best for |
|---|---|
| **Small-step operational** | **language definition**, type soundness, concurrency |
| Big-step operational | interpreters, simple specs |
| **Denotational** | **proving equivalences**, optimisation correctness |
| **Axiomatic** | **program verification**, contracts |

**They're complementary, and mature language definitions have several** — with proofs that they agree. **Standard ML has a complete formal definition** (Milner, Tofte, Harper), which is still unusual.

**Modern practice:** most languages are specified informally in English, with a formal semantics for the tricky parts. **JavaScript's spec is written in a pseudo-operational style; WebAssembly has a full formal semantics from the start** — a deliberate, and rare, decision. **Rust's semantics for `unsafe` code is still an active research problem** (the Stacked Borrows and Tree Borrows models), which is why Miri exists.

## Equivalence

**When are two programs the same?**

**Contextual (observational) equivalence** — $e_1 \approx e_2$ if **no program context can distinguish them.** The gold standard, and quantifying over all contexts makes it hard to prove directly.

**Logical relations** — the standard proof technique, defined by induction on types.

**Bisimulation** — for concurrent and stateful systems: two systems are equivalent if each can match the other's steps.

**Why it matters:** **every compiler optimisation is a claim of equivalence.** Constant folding, dead code elimination, inlining, loop transformations — **each must preserve observable behaviour**, and "observable" needs defining.

> **This is where UB does its work.** If a behaviour is *undefined*, the compiler is licensed to assume it never occurs — **so far more transformations become "equivalent"**, because programs exhibiting UB are outside what the semantics constrains. **UB is not a bug in the spec; it's a deliberate widening of the equivalence relation to enable optimisation.** → [[languages/04-c/10-undefined-behaviour|Undefined Behaviour]]

## Concurrency

**Sequential semantics doesn't extend cleanly.**

**Interleaving semantics** — concurrent execution is *some* interleaving of atomic steps. **Simple, and it assumes sequential consistency, which real hardware doesn't provide.** → [[foundations/computer-architecture/11-multicore-and-memory-models|Memory Models]]

**Weak memory models** must be specified formally, and it's genuinely difficult. **The C++11 memory model took years and had known bugs** (the "out-of-thin-air" problem, where a value appears from a self-justifying cycle, was unresolved for a decade).

**Process calculi** — CSP (Hoare) and the π-calculus (Milner) model concurrency as communication rather than shared state. **CSP directly inspired Go's channels and occam.** → [[languages/02-go/07-concurrency-patterns|Go concurrency]]

**Session types** — types describing a *protocol*: "send an Int, then receive a Bool, then close." **Protocol violations become type errors**, and it's an active area moving into practice (Rust and Scala libraries exist).

## Practical notes

**You don't need to write a formal semantics.** You need to **read one** when a spec is ambiguous, and to **know the vocabulary** when a language's behaviour surprises you.

**When behaviour surprises you, ask what the semantics actually promises.** Frequently the answer is "nothing" — evaluation order, integer overflow, data races. **Undefined and unspecified behaviour are the spec telling you not to rely on what you observed.**

**Loop invariants are the practically useful piece.** Being able to state one for a non-obvious loop is a real code-review skill, and it's Hoare logic informally applied.

**Use the verification tools where the stakes justify it** — Dafny, Frama-C, SPARK, TLA+ for protocols. **The cost is high and it's justified for consensus algorithms, crypto and safety-critical control.** → [[architecture/04-distributed-systems/15-testing-distributed-systems|Testing Distributed Systems]]

**Read the memory model** for any language you write concurrent code in.

---

## Related
- [[foundations/programming-language-theory/04-type-systems-formally|Type Systems Formally]] — soundness, proved against these semantics
- [[foundations/discrete-math/03-proof-techniques|Proof Techniques]] — loop invariants as induction
- [[languages/04-c/10-undefined-behaviour|Undefined Behaviour]] — semantics deliberately left open
- [[foundations/programming-language-theory/README|PL theory map]]

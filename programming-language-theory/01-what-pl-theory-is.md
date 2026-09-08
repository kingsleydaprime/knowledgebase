# What PL Theory Is

**[Intermediate]** — Studying languages as mathematical objects, and why it produced things you use daily.

**Source:** `[reference]` — see [[foundations/programming-language-theory/README|the domain note]].

## The question

**[[foundations/compilers/README|Compilers]] asks: how do I *implement* a language?**

**PL theory asks: what does a program *mean*, and what can I prove about it?**

**Both are needed and they're genuinely different.** A compiler engineer makes the language run. A PL theorist establishes that a type system is sound, that an optimisation preserves meaning, or that a construct is expressible at all.

> **The practical test of whether PL theory matters: every feature in the languages you use came from here, usually decades earlier.**
>
> Generics, type inference, garbage collection, closures, pattern matching, `Option`/`Result`, algebraic data types, async/await, borrow checking, lambdas in Java. **All were PL research results long before they were language features.**

## Why bother

**Being honest, since this was the last of five domains chosen and it's the most abstract.**

**1. It explains your language's design.** *Why does Rust's borrow checker reject this? Why does Java have type erasure? Why is `null` regretted? Why is `var` inference limited to local variables?* **These have principled answers, not arbitrary ones.**

**2. It predicts what's coming.** Effect systems, dependent types, linear types and gradual typing are in research languages now and will be in mainstream ones in a decade. **The pattern has held for forty years.**

**3. It tells you what's impossible.** Rice's theorem bounds what any type checker can do. **The soundness/completeness trade is a theorem, not an engineering shortfall.** → [[foundations/theory-of-computation/06-decidability|Decidability]]

**4. It gives you a vocabulary for design.** *Variance, parametricity, referential transparency, evaluation strategy* — precise names for things you already reason about vaguely.

**And the honest counter-argument:** you can be an excellent engineer without any of this. **The claim isn't necessity — it's that certain design questions are opaque without it**, and that the languages you'll use in ten years are being designed with it now.

## The three pillars

**Syntax** — what programs *look* like. Grammars and parsing. **Well understood, and mostly [[foundations/theory-of-computation/04-context-free-languages|solved]].** → [[foundations/compilers/03-parsing|Parsing]]

**Semantics** — what programs *mean*. **The hard and interesting part**, and the subject of note 03.

**Types** — what programs are *allowed* to mean. A static, decidable approximation of behaviour. Notes 04–06.

## Formalism, briefly

**The notation you'll meet**, and it's worth being able to read even if you never write it.

**Inference rules** — premises above the line, conclusion below:

$$\frac{\Gamma \vdash e_1 : \text{Int} \qquad \Gamma \vdash e_2 : \text{Int}}{\Gamma \vdash e_1 + e_2 : \text{Int}}$$

**Read: if in context $\Gamma$, $e_1$ has type Int and $e_2$ has type Int, then $e_1 + e_2$ has type Int.**

**$\Gamma$ (the context) maps variables to types.** $\vdash$ is "entails". **That's it** — a type system is a set of these rules, and type checking is finding a derivation.

**Judgements** are the statements being derived: $\Gamma \vdash e : \tau$ (typing), $e \to e'$ (evaluation), $\Gamma \vdash e_1 \equiv e_2$ (equivalence).

> **Once you can read an inference rule, most PL papers become accessible.** It's a small notational investment with a large payoff — and it's the same structure as the natural-deduction proofs in [[foundations/discrete-math/02-logic|logic]], which isn't a coincidence.

## The results worth knowing

**Even if you never read a paper, these five shaped what you use:**

**The lambda calculus is Turing-complete** (Church, 1936). **Three constructs — variables, abstraction, application — compute everything.** → [[foundations/programming-language-theory/02-lambda-calculus|Lambda Calculus]]

**Type soundness** — "well-typed programs don't go wrong" (Milner, 1978). **Progress and preservation**, and it's what a type system is *for*. → [[foundations/programming-language-theory/04-type-systems-formally|Type Systems]]

**Hindley–Milner inference** — full type inference without annotations, in near-linear time. **ML, Haskell, and the ancestor of every `var` and `auto` you write.** → [[foundations/programming-language-theory/05-type-inference|Type Inference]]

**Curry–Howard** — **propositions are types; proofs are programs.** Not an analogy. The basis of Coq, Lean and Agda. → [[foundations/programming-language-theory/06-curry-howard-and-proofs|Curry–Howard]]

**Parametricity** — "theorems for free" (Wadler, 1989). **A polymorphic type constrains behaviour so tightly that you can derive theorems from the signature alone.**

> **The parametricity example that lands:** a function of type `∀a. [a] -> [a]` **cannot inspect the elements** — it doesn't know what they are. So it can only rearrange, duplicate or drop them. **`reverse`, `tail`, `id` all fit; nothing that depends on the values can.**
>
> **The type alone tells you a great deal about the implementation**, which is why "make it more polymorphic" often makes code *easier* to reason about rather than harder.

## Where PL theory shows up

**In languages you use:**

| Feature | From |
|---|---|
| Generics / parametric polymorphism | System F (Girard, Reynolds, 1972) |
| `Option` / `Maybe`, `Result` | algebraic data types, ML |
| Pattern matching + exhaustiveness | ADTs and coverage checking |
| `var` / `auto` / type inference | Hindley–Milner |
| **Rust's borrow checker** | **linear and affine types** |
| async/await | monads and CPS |
| Traits / typeclasses | Wadler & Blott, 1989 |
| Null safety (Kotlin, Swift) | option types, finally |

**In tools:** type checkers, linters, static analysers, refactoring tools that preserve meaning, and **compiler optimisations that must provably preserve semantics.** → [[foundations/compilers/07-optimisation|Optimisation]]

**In verification:** Coq, Lean, Agda, Idris. **CompCert is a C compiler proven correct in Coq** — its output is proven to preserve the source's semantics, which is why it's used in avionics. **seL4** is a formally verified microkernel.

**In security:** information-flow types tracking whether secret data can reach public output — **making non-interference a type-checkable property.** → [[foundations/information-theory/07-where-information-theory-shows-up|Information leakage]]

## The paradigms, formally

**A useful reframing of a familiar list.**

**Imperative** — programs are state transformations. Semantics given by how the store evolves.

**Functional** — programs are expressions to evaluate. **Referential transparency**: an expression can be replaced by its value without changing meaning. **This is what enables aggressive optimisation and equational reasoning.**

**Logic** — programs are relations, and execution is proof search. Prolog.

**Object-oriented** — the formal account is messier than the others. **Subtyping, variance and inheritance interact in ways that took decades to get right** — and Java's covariant arrays, a known unsoundness, are the standard cautionary example. → [[foundations/programming-language-theory/04-type-systems-formally|Variance]]

## Reading this track

**02–03 are the foundations** — lambda calculus, then semantics. **04–06 are types**, and 06 is the payoff.

**07–08 are effects and where the field is going.**

**Prerequisites:** [[foundations/discrete-math/02-logic|logic]] and [[foundations/discrete-math/03-proof-techniques|proof by induction]] — **structural induction especially**, since every soundness proof is one. [[foundations/compilers/README|Compilers]] helps for grounding but isn't required.

---

## Related
- [[foundations/programming-language-theory/02-lambda-calculus|Lambda Calculus]] — the foundation
- [[foundations/compilers/README|Compilers]] — the implementation counterpart
- [[foundations/theory-of-computation/README|Theory of Computation]] — the sibling theory domain
- [[foundations/programming-language-theory/README|PL theory map]]

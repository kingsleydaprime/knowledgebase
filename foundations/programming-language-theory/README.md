# Programming Language Theory

Studying languages as mathematical objects — what a program *means*, and what you can prove about it. **The research pipeline that produced every feature in the languages you use.**

**~10,200 words across 7 notes.** Built August 2026. `[reference]`.

> **The one idea:** **[[foundations/compilers/README|Compilers]] asks how to *implement* a language. PL theory asks what a program *means* and what can be proved about it.** Both are needed, and the second is where generics, type inference, garbage collection, pattern matching, `Option`, async/await and the borrow checker all came from — usually decades before they shipped.

## Reading order

**02–03 are the foundations. 04–06 are types, and 06 is the payoff. 07 is where the field is going.**

1. [[foundations/programming-language-theory/01-what-pl-theory-is|What PL Theory Is]] — **[Intermediate]** — why formalise, inference-rule notation, the five results worth knowing, and **parametricity: theorems for free**
2. [[foundations/programming-language-theory/02-lambda-calculus|Lambda Calculus]] — **[Intermediate → Advanced]** — three constructs that compute everything, Church encodings, the Y combinator, evaluation strategies, and **why adding types removed Turing completeness**
3. [[foundations/programming-language-theory/03-semantics|Semantics]] — **[Advanced]** — operational, denotational and axiomatic. **Loop invariants as Hoare logic**, separation logic, and why UB is a widening of the equivalence relation
4. [[foundations/programming-language-theory/04-type-systems-formally|Type Systems Formally]] — **[Advanced]** — progress and preservation, **why Java's covariant arrays are knowingly unsound**, variance and PECS
5. [[foundations/programming-language-theory/05-type-inference|Type Inference]] — **[Advanced]** — Hindley–Milner, unification, the value restriction, and **why Java's `var` is far weaker than OCaml's `let`**
6. [[foundations/programming-language-theory/06-curry-howard-and-proofs|Curry–Howard and Proofs]] — **[Advanced]** — **propositions are types, proofs are programs.** Constructive logic, dependent types, proof assistants, and what actually transfers to daily work
7. [[foundations/programming-language-theory/07-effects-and-substructural-types|Effects and Substructural Types]] — **[Advanced]** — algebraic effects, **Rust's borrow checker as affine types**, session types, and where languages are heading

## The things worth carrying

1. **A sound decidable type checker *must* reject some correct programs.** Rice's theorem. It's not a design failing → [[foundations/programming-language-theory/04-type-systems-formally|04]]
2. **Soundness = progress + preservation.** "Doesn't get stuck" plus "the type stays true" → [[foundations/programming-language-theory/04-type-systems-formally|04]]
3. **The simply typed lambda calculus always terminates — and is no longer Turing-complete.** Types traded power for a guarantee → [[foundations/programming-language-theory/02-lambda-calculus|02]]
4. **PECS: producer extends, consumer super.** Mutable *and* covariant is unsound, which is exactly Java's array bug → [[foundations/programming-language-theory/04-type-systems-formally|04]]
5. **Full inference for rank-N polymorphism is undecidable**, which is why Java makes you write type parameters and ML doesn't → [[foundations/programming-language-theory/05-type-inference|05]]
6. **Propositions are types; proofs are programs.** `fst`, `const` and `curry` are proofs of tautologies → [[foundations/programming-language-theory/06-curry-howard-and-proofs|06]]
7. **A constructive proof carries an algorithm.** Which is why classical proof by contradiction is useless for programming → [[foundations/programming-language-theory/06-curry-howard-and-proofs|06]]
8. **Make illegal states unrepresentable.** The most transferable idea in the whole track → [[foundations/programming-language-theory/06-curry-howard-and-proofs|06]]
9. **Rust's ownership is affine types plus regions** — 1990s research, shipped 2015 → [[foundations/programming-language-theory/07-effects-and-substructural-types|07]]
10. **Function colouring is an effect system with poor polymorphism.** Algebraic effects are the fix → [[foundations/programming-language-theory/07-effects-and-substructural-types|07]]
11. **HM's worst practical flaw is error messages** — unification reports where the contradiction was *detected*, not where the mistake was → [[foundations/programming-language-theory/05-type-inference|05]]
12. **The bottleneck between theory and practice is ergonomics, not expressiveness.** GC took 30 years, generics 30, affine types 25 → [[foundations/programming-language-theory/07-effects-and-substructural-types|07]]

## Where this connects

| | |
|---|---|
| [[foundations/compilers/README\|compilers]] | **The implementation counterpart.** Theory here, machinery there |
| [[foundations/discrete-math/02-logic\|logic]] · [[foundations/discrete-math/03-proof-techniques\|proof]] | **The prerequisite**, and half of Curry–Howard |
| [[foundations/theory-of-computation/06-decidability\|decidability]] | Why type checkers must be conservative |
| [[languages/03-rust/03-ownership\|Rust]] | Where this theory most visibly shipped |
| [[languages/05-cpp/README\|C++]] · [[languages/01-java/README\|Java]] | Variance, erasure, move semantics — the design decisions explained |

## The honest note

**`[reference]`, and this is the most abstract domain in the vault** — the one where the gap between reading and doing is widest, and where the practical payoff is most indirect.

**Being straight about that:** you can be an excellent engineer without any of this. **The claim isn't necessity — it's that certain design questions are opaque without it**, and that the languages you'll use in ten years are being designed with it now.

**What would close the gap, and the first item is the one that matters:**

1. **Write a type checker.** [[build-your-own-x/04-your-own-language|Your own language]] with a type checker instead of a bare interpreter — **implement the inference rules from note 04 and watch them work.** A few hundred lines, and it makes the notation concrete permanently
2. **Implement Hindley–Milner.** Unification plus generalisation is ~200 lines and genuinely satisfying when it infers a type you didn't expect
3. **[*Software Foundations*](https://softwarefoundations.cis.upenn.edu)** — free, interactive, in Coq. **Proves the theorems in note 04 by making *you* prove them.** The best entry point into the subject by a distance
4. **Lean's [Natural Number Game](https://adam.math.hhu.de)** — a browser game that teaches proof, and it will not let you skip a step
5. **Write something in a dependently-typed language** — Idris, Agda, Lean. **Encode a length-indexed vector and feel `head` refuse to compile on an empty one**
6. **The books:** ***Types and Programming Languages*** (Pierce) — **the standard, and genuinely readable; if you read one, read TAPL**; *Practical Foundations for Programming Languages* (Harper) for depth; *Programming Language Foundations in Agda* (Wadler) — free, executable

**What's missing:** exercises, module systems and ML functors, object calculi formally, abstract interpretation, program synthesis, macro systems as a theory, concurrency calculi beyond a mention, and gradual typing's performance problem in depth.

→ [[PRIMETECHIE|Reading is not a rank.]]

## Related
- [[foundations/compilers/README|Compilers]] — the implementation side
- [[foundations/theory-of-computation/README|Theory of Computation]] — the sibling theory domain
- [[foundations/discrete-math/README|Discrete Mathematics]] — the prerequisite
- [[BUILD-PLAN|Build Plan]]

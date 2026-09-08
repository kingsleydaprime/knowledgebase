# Curry–Howard and Proofs

**[Advanced]** — Propositions are types; proofs are programs. Not an analogy — an isomorphism, and the basis of every proof assistant.

## The correspondence

> **A type is a proposition. A program of that type is a proof of it.**

**Discovered independently by Curry (1930s, combinatory logic) and Howard (1969, lambda calculus).**

| Logic | Types |
|---|---|
| proposition | type |
| **proof** | **program** |
| $A \wedge B$ (and) | $A \times B$ (**pair/tuple**) |
| $A \vee B$ (or) | $A + B$ (**sum/enum/`Either`**) |
| $A \Rightarrow B$ (implies) | $A \to B$ (**function**) |
| $\top$ (true) | `unit` |
| $\bot$ (false) | **the empty type** (`Void`, `!`) |
| $\neg A$ | $A \to \bot$ |
| $\forall x. P(x)$ | dependent function $\Pi$ |
| $\exists x. P(x)$ | dependent pair $\Sigma$ |
| **proof simplification** | **program evaluation** |

**The reading that makes it click:**

**"$A$ implies $B$" means: give me evidence of $A$ and I'll produce evidence of $B$.** That's a function $A \to B$.

**"$A$ and $B$" means: I have evidence of both.** That's a pair.

**"$A$ or $B$" means: I have evidence of one, and I know which.** That's a tagged union.

**Modus ponens** — from $A \Rightarrow B$ and $A$, conclude $B$ — **is function application.**

$$\frac{f : A \to B \qquad a : A}{f\,a : B}$$

> **This is not a resemblance. The inference rules of natural deduction and the typing rules of the lambda calculus are the same rules.** → [[foundations/programming-language-theory/02-lambda-calculus|Lambda Calculus]]

## Proving by programming

**To prove a proposition, write a program of that type.**

$$A \Rightarrow (B \Rightarrow A)$$

```haskell
proof :: a -> (b -> a)
proof x = \_ -> x        -- const
```

**`const` is a proof.** If you have an $A$, you can produce an $A$ from anything.

**Distribution:**

$$(A \wedge B) \Rightarrow A$$

```haskell
proof :: (a, b) -> a
proof = fst
```

> **The functions in your standard library are proofs of logical tautologies.** `fst`, `snd`, `const`, `curry`, `uncurry`, `flip` — **each has a type that is a valid propositional formula, and the implementation is its proof.**
>
> **And the converse: if you cannot implement a total function of some type, that proposition is not provable.** Try to write `a -> b`. You can't, because "$A$ implies $B$" for arbitrary $A$ and $B$ is false.

## Constructive logic

**The correspondence is with *intuitionistic* logic**, and the difference matters.

**The law of the excluded middle — $A \vee \neg A$ — is not provable.**

**Why: proving $A \vee B$ constructively means producing a tagged value — either `Left a` or `Right b`.** To prove $A \vee \neg A$ you'd need to *decide*, for arbitrary $A$, which one holds. **You can't.**

$$\text{Excluded middle} \quad\longleftrightarrow\quad \texttt{forall a. Either a (a -> Void)}$$

**No total program has that type.**

**Similarly, double-negation elimination ($\neg\neg A \Rightarrow A$) fails.** `((a -> Void) -> Void) -> a` isn't implementable.

> **The practical meaning: a constructive proof carries an algorithm.** Prove "there exists an $x$ with property $P$" and **you have produced an $x$** — the proof *is* the construction.
>
> **A classical proof by contradiction gives you existence with no witness.** For mathematics that's fine; **for programming it's useless**, because you cannot run it. → [[foundations/discrete-math/03-proof-techniques|Non-constructive proofs]]

**Classical reasoning is recoverable** — via continuations, remarkably. **`callcc` has the type of Peirce's law**, $((A\Rightarrow B)\Rightarrow A)\Rightarrow A$, which is equivalent to the excluded middle. **Control operators correspond to classical logic** (Griffin, 1990), which is a genuinely startling connection between exception handling and proof theory.

## Dependent types

**Types depending on *values* — where the correspondence becomes usable for real mathematics.**

```idris
Vec : Nat -> Type -> Type

append : Vec n a -> Vec m a -> Vec (n + m) a
head   : Vec (S n) a -> a        -- CANNOT be called on an empty vector
```

**`head` on an empty vector is a *type error*, not a runtime exception.** The length is in the type.

**And the quantifiers appear:**

**$\Pi$ (dependent function)** — $\forall x{:}A.\;B(x)$. The return type depends on the argument's *value*.

**$\Sigma$ (dependent pair)** — $\exists x{:}A.\;B(x)$. A value together with a proof about it.

```idris
sorted : (xs : List Nat) -> (ys : List Nat ** (IsSorted ys, Permutation xs ys))
```

> **That signature says: given a list, return a list *together with proofs* that it's sorted and is a permutation of the input.**
>
> **A function with that type cannot be wrong.** Returning the empty list wouldn't type-check. **The specification is the type, and the compiler verifies it.**

**The costs are real:** type checking becomes theorem proving (so inference is impossible and you write proofs by hand), proofs are often far longer than the code, and **the ergonomics remain poor** — which is why dependent types haven't reached mainstream languages despite forty years.

## Proof assistants

**Where this is used in practice.**

| System | Basis | Known for |
|---|---|---|
| **Coq / Rocq** | Calculus of Inductive Constructions | **CompCert, four colour theorem** |
| **Lean 4** | dependent type theory | **mathlib** — and it's also a real programming language |
| **Agda** | Martin-Löf type theory | dependently-typed programming |
| Idris | dependent types, pragmatic | practical DT programming |
| Isabelle/HOL | higher-order logic | seL4 |

**Landmark results:**

**The four colour theorem** — proved with computer assistance in 1976, and **fully verified in Coq in 2005** by Gonthier, settling the doubts about the original.

**The Feit–Thompson theorem** — a 255-page group theory proof, verified in Coq (2012).

**CompCert** — a C compiler **proven to preserve source semantics.** Used in avionics, and a Csmith study found bugs in every mainstream compiler tested **and none in CompCert's verified core.** → [[foundations/programming-language-theory/03-semantics|Semantics]]

**seL4** — a microkernel with a machine-checked proof of functional correctness, plus proofs of confidentiality and integrity.

**Lean's mathlib** is the notable current development: **a community-built library of formalised mathematics**, now over a million lines, with Fields Medallists actively involved. Terence Tao has formalised recent results in it. **Formal verification is moving from "a curiosity" to "a tool working mathematicians use"**, which was not true a decade ago.

## What you can take from this

**Being honest — you will probably never write a Coq proof. What transfers:**

**Types as specifications.** **Make illegal states unrepresentable** — the design principle that comes straight from this correspondence.

```rust
enum State {
    Disconnected,
    Connecting { started: Instant },
    Connected { session: SessionId },
}
```

**Versus three booleans and an optional session ID**, where most combinations are invalid and every function must handle them. **The enum makes the invalid states not exist**, and the compiler enforces it.

**Sum types are underused.** `Option`/`Result`/`Either` are the logical disjunction, and **languages without them force you to encode "or" as null, exceptions or sentinel values** — all of which the type system can't check. → [[languages/03-rust/07-option-and-result|Option and Result]]

**The empty type has uses.** Rust's `!` (never) types a function that doesn't return; a `Result<T, Infallible>` says the error case is impossible. **`Void` in a type means "this cannot happen", checked.**

**Parametricity constrains behaviour.** A more polymorphic signature is a *stronger* statement about what the function can do. → [[foundations/programming-language-theory/01-what-pl-theory-is|Theorems for free]]

**Total functions are proofs; partial ones aren't.** A function that can throw, loop forever, or return null **is not a proof of its type** — which is precisely why proof assistants require totality.

## The honest limits

**Formal verification is expensive.** seL4 took roughly 20 person-years for ~10,000 lines of C. **That ratio is only justified where failure is catastrophic** — kernels, crypto, avionics, medical devices.

**A proof is only as good as its specification.** **Proving code matches a wrong spec proves nothing useful**, and specifications are where the real thinking is.

**The trusted computing base remains.** You trust the proof checker, the axioms, and the hardware. **Small, but not zero.**

**Extraction gaps.** Coq extracts to OCaml, and the extraction itself is generally unverified.

> **Which is why the interesting direction isn't full verification — it's *lightweight* methods that get some of the benefit cheaply:** refinement types checked by SMT (Liquid Haskell, F*), property-based testing, model checking, and **richer type systems in ordinary languages.** Rust's borrow checker is the best current example: **a substructural type system, from this lineage, that mainstream programmers use without knowing the theory.** → [[foundations/programming-language-theory/07-effects-and-substructural-types|Substructural Types]]

---

## Related
- [[foundations/programming-language-theory/04-type-systems-formally|Type Systems Formally]] — soundness
- [[foundations/discrete-math/02-logic|Logic]] — the other half of the correspondence
- [[foundations/discrete-math/03-proof-techniques|Proof Techniques]] — constructive vs classical
- [[foundations/programming-language-theory/README|PL theory map]]

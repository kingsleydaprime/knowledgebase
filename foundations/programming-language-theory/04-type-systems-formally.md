# Type Systems Formally

**[Advanced]** — What soundness actually means, why variance is confusing, and the theorem behind "well-typed programs don't go wrong".

> **[[foundations/compilers/05-type-systems-and-checking|Compilers: Type Systems]] covers the implementation.** This note is the theory — what a type system *guarantees* and how that's proved.

## What a type system is

**A decidable, static, conservative approximation of runtime behaviour.**

**Each word is doing work:**

**Decidable** — checking always terminates. **Forced, because a compiler must halt.**

**Static** — before execution.

**Conservative** — **it rejects some correct programs.** Unavoidable, by Rice's theorem: "does this program go wrong" is undecidable, so any decidable checker must err somewhere. → [[foundations/theory-of-computation/06-decidability|Decidability]]

> **This is the answer to "why does the type checker reject my obviously-correct code?"** It's not that the designers weren't clever enough — **a sound decidable checker must reject some correct programs.** The only design question is *which ones.*

## Soundness

**The central theorem. "Well-typed programs don't go wrong" (Milner, 1978).**

**Proved in two halves:**

**Progress** — a well-typed term is either a value or can take a step.

$$\text{If } \vdash e : \tau \text{ then } e \text{ is a value or } \exists e'.\ e \to e'$$

**"It doesn't get stuck."** No `3 + true` with nowhere to go.

**Preservation (subject reduction)** — stepping preserves the type.

$$\text{If } \vdash e : \tau \text{ and } e \to e' \text{ then } \vdash e' : \tau$$

**"The type stays true as it runs."**

> **Together, by induction: a well-typed program never reaches a stuck state.** It either terminates with a value of the expected type, or runs forever.
>
> **Note what soundness does *not* promise.** Not termination. Not absence of exceptions (those are defined behaviour). Not correctness. **Only that the specific errors the type system models cannot occur** — and the value of a type system is exactly how many real errors it models.

**Both proofs are structural induction on typing derivations.** → [[foundations/discrete-math/05-induction-and-recursion|Structural Induction]]

## Soundness in real languages

**Where the theory meets deliberate compromise.**

**Java's covariant arrays are unsound, knowingly:**

```java
Object[] objs = new String[1];   // allowed — String[] <: Object[]
objs[0] = Integer.valueOf(42);   // compiles, throws ArrayStoreException
```

**The type checker accepts a program that fails at runtime.** **Java patches the hole with a runtime check on every array store** — a real performance cost on every write, paid forever, for a 1995 decision made before generics existed.

**Other known unsoundnesses:** TypeScript is deliberately unsound in several places (bivariant method parameters, `any`) **because soundness would reject too much existing JavaScript.** Scala had a soundness bug (`null` and type projections) that took years to characterise. **C's type system is thoroughly unsound** — casts, unions, pointer arithmetic.

> **The honest framing: soundness is a design goal traded against usability and compatibility.** TypeScript chose unsound-but-adoptable and it was clearly the right call for its purpose. **What matters is knowing where the holes are** — an unsound language's type errors are still valuable, they're just not guarantees.

## Subtyping

$$\frac{\Gamma\vdash e : S \qquad S <: T}{\Gamma\vdash e : T} \quad\text{(subsumption)}$$

**"An $S$ can be used where a $T$ is expected."**

**The Liskov substitution principle is this, stated for objects** — and it's why LSP is a *typing* rule rather than a style guideline.

### Variance

**The part everyone finds confusing, and there's a rule that makes it mechanical.**

**Given `Cat <: Animal`, what's the relationship between `List<Cat>` and `List<Animal>`?**

| | Rule | Safe when |
|---|---|---|
| **Covariant** | `F<Cat> <: F<Animal>` | $F$ **produces** $T$ |
| **Contravariant** | `F<Animal> <: F<Cat>` | $F$ **consumes** $T$ |
| **Invariant** | no relationship | $F$ does **both** |

> **The mnemonic that actually works: PECS — Producer Extends, Consumer Super.**
>
> **A `List<Cat>` you only *read* from is safely a `List<? extends Animal>`** — everything you get out is an Animal.
>
> **A `List<Animal>` you only *write* to is safely a `List<? super Cat>`** — anything you put in is an Animal.
>
> **A mutable `List<T>` you both read and write must be invariant**, and that's exactly why Java's arrays are broken: they're covariant *and* mutable.

**Function types are the famous case:**

$$\frac{T_1 <: S_1 \qquad S_2 <: T_2}{S_1 \to S_2 \;<:\; T_1 \to T_2}$$

**Contravariant in the argument, covariant in the return.**

**Read it as: a function is more general if it accepts *more* inputs and returns *fewer* possible outputs.** A function taking `Animal` can be used where one taking `Cat` is expected — it handles cats and more.

**Contravariant parameters are counter-intuitive and correct.** Most OO languages get this wrong for method overriding (Java uses invariance; Eiffel was covariant and unsound). **Kotlin and Scala have declaration-site variance** (`out T`, `in T`), which is the cleaner design.

## Polymorphism

**Parametric** — the same code for all types. `List<T>`, `∀a. a -> a`.

**Gives you [[foundations/programming-language-theory/01-what-pl-theory-is|parametricity]]** — a function of type `∀a. [a] -> [a]` cannot inspect the elements, so its behaviour is enormously constrained by the type alone.

**Ad-hoc (overloading)** — different implementations per type. **Typeclasses (Haskell), traits (Rust), protocols (Swift), concepts (C++20).**

**Subtype** — via inheritance.

**Row polymorphism** — "any record with at least these fields". **Structural typing**, and it's what TypeScript and Go interfaces do.

**Implementation matters here:**

**Monomorphisation** (Rust, C++) — generate specialised code per type. **Fast, no runtime cost, larger binaries and slower compiles.**

**Erasure** (Java) — one implementation, types erased at runtime. **Small, and it's why Java can't do `new T[]` or `instanceof List<String>`.** Boxing costs performance for primitives — which is what Project Valhalla is addressing.

**Dictionary passing** (Haskell) — pass a table of methods at runtime. Flexible, indirect.

## Type inference

**Covered fully in [[foundations/programming-language-theory/05-type-inference|note 05]]** — the short version:

**Hindley–Milner infers everything with no annotations**, in practice near-linear time. **The restriction that makes it work is that polymorphism is limited to `let`-bound values** (prenex/rank-1).

**Full inference for System F (rank-N polymorphism) is undecidable** (Wells, 1994). **Which is exactly why Java and C# require you to write type parameters** while ML and Haskell often don't — it's a theorem, not a design preference.

## Advanced systems

**What's coming, and where it's already arrived.**

**Dependent types** — types depending on values. `Vec 3 Int`, `sorted : (xs : List) -> Proof (isSorted xs)`.

**Enormously expressive — you can encode arbitrary specifications in types.** Type checking becomes theorem proving, so **full inference is impossible and you write proofs.** Idris, Agda, Lean, Coq. → [[foundations/programming-language-theory/06-curry-howard-and-proofs|Curry–Howard]]

**Refinement types** — a base type plus a predicate: `{v: Int | v > 0}`. **Less expressive than dependent types, and decidable via SMT solvers.** Liquid Haskell, F*, and this is the pragmatic middle ground that's most likely to reach mainstream languages.

**Gradual typing** — mix static and dynamic, with runtime checks at the boundary. **TypeScript, Python's type hints, Sorbet for Ruby.** The theory (Siek and Taha) is well developed; **the performance of sound gradual typing at the boundary is a real unsolved problem**, which is why TypeScript erases rather than checking.

**Effect systems, linear and session types** → [[foundations/programming-language-theory/07-effects-and-substructural-types|note 07]].

## The trade-offs

**Being fair about static vs dynamic, since the argument is old and mostly settled by practice:**

**Static typing gives you:** errors before running, machine-checked documentation, refactoring confidence, IDE support, and performance (no runtime type checks, better layout).

**Dynamic typing gives you:** no fighting the checker, easier metaprogramming, faster prototyping, and no rejected-correct-programs problem.

> **The empirical evidence is weaker than either camp claims** — studies on defect rates are mixed and confounded.
>
> **The strongest practical argument for static types isn't defects; it's *tooling and change*.** Reliable rename, safe refactoring, and accurate completion require a type checker. **On a large codebase over years, that's where the value is** — which is why TypeScript won JavaScript, why Python added hints, and why Ruby got Sorbet.

**The convergence is clear:** dynamic languages are adding optional types; static languages are adding inference to reduce the annotation burden. **Both are moving toward "types where they help, inferred where they don't."**

---

## Related
- [[foundations/programming-language-theory/05-type-inference|Type Inference]] — Hindley–Milner
- [[foundations/programming-language-theory/06-curry-howard-and-proofs|Curry–Howard]] — where types become proofs
- [[foundations/compilers/05-type-systems-and-checking|Compilers: Type Systems]] — the implementation
- [[foundations/programming-language-theory/README|PL theory map]]

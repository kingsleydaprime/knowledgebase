# Type Inference

**[Advanced]** — Hindley–Milner, unification, and why `var` in Java is weaker than `let` in OCaml.

## The problem

**Given a program with no type annotations, find the types — or prove there aren't any.**

```ocaml
let compose f g x = f (g x)
(* inferred: ('b -> 'c) -> ('a -> 'b) -> 'a -> 'c *)
```

**No annotations, and the most general type is derived automatically.** That result — from Hindley (1969) and Milner (1978) — is one of the genuinely elegant achievements in the field.

## Algorithm W

**Three steps, and the whole thing is mechanical once you see it.**

**1. Assign fresh type variables** to everything unknown.

**2. Generate constraints** from how expressions are used.

**3. Solve by unification.**

**Worked through `fun x -> x + 1`:**

```
x : α                              fresh variable
x + 1  requires  α = Int           (+) : Int -> Int -> Int
result : Int
⟹  fun x -> x + 1  :  Int -> Int
```

**And `fun f x -> f (f x)`:**

```
f : α,  x : β
f x       ⟹  α = β -> γ
f (f x)   ⟹  α = γ -> δ
unify     ⟹  β = γ = δ
⟹  ('a -> 'a) -> 'a -> 'a
```

**The type came out of the structure alone.** Nothing was declared.

## Unification

**The engine — solve equations between type terms.**

```
unify(α, τ)        →  bind α := τ    (if α not in τ)
unify(τ, α)        →  bind α := τ
unify(Int, Int)    →  ok
unify(Int, Bool)   →  TYPE ERROR
unify(σ₁→σ₂, τ₁→τ₂) → unify(σ₁,τ₁); unify(σ₂,τ₂)
```

**Robinson's algorithm (1965)**, and it's the same unification as in Prolog's resolution engine.

**The occurs check** is the crucial guard: **binding $\alpha := \alpha \to \text{Int}$ would create an infinite type.**

> **Rejecting infinite types is what makes self-application $x\,x$ untypable** — and therefore what makes the [[foundations/programming-language-theory/02-lambda-calculus|Y combinator]] untypable in Hindley–Milner. **The occurs check is why HM languages need an explicit `let rec` or `fix` for recursion.**
>
> **Skipping the occurs check gives you equirecursive types** — OCaml offers this behind `-rectypes`, and it's off by default because the error messages become dreadful.

**Union-find is the efficient implementation** — type variables as nodes, unification as merging. **That's why HM is near-linear in practice** despite a pathological exponential worst case. → [[foundations/dsa/04-data-structures/10-union-find|Union-Find]]

## Let-polymorphism

**The idea that makes it useful.**

**Generalise at `let` bindings** — turn free type variables into universally quantified ones:

```ocaml
let id = fun x -> x        (* generalise: ∀a. a -> a *)
in (id 1, id "hello")      (* instantiate FRESHLY at each use *)
```

**Without generalisation, the first use would fix `id` to `Int -> Int`** and the second would fail.

**Instantiation** does the reverse — replace the quantified variables with fresh ones at each use site.

**And the restriction that keeps it decidable:**

> **Lambda-bound variables are *not* generalised.** Only `let`-bound ones.
>
> ```ocaml
> fun id -> (id 1, id "hello")   (* ✗ rejected *)
> ```
>
> **This is rank-1 (prenex) polymorphism** — quantifiers only at the outermost level. **Rank-2 and above is where inference becomes undecidable.**

**Complexity:** HM is DEXPTIME-complete in theory (Kfoury, Mairson), **and near-linear on real programs.** The pathological case requires deeply nested `let`s each doubling the type size — constructible, and never written by hand.

## Where full inference stops

**The theorem that explains a lot of language design:**

> **Type inference for System F (rank-N polymorphism) is undecidable** (Wells, 1994).

**So every language makes a choice:**

**Restrict to rank-1** — full inference, no annotations. **ML, OCaml, Haskell (mostly).**

**Require annotations for polymorphism** — inference only for local, monomorphic uses. **Java, C#, C++, Go, TypeScript.**

> **This is exactly why `var x = foo()` in Java is *far* weaker than `let x = foo()` in OCaml.**
>
> **Java's `var` is local type *deduction*** — copy the type from the initialiser's right-hand side. **No unification, no constraints, no generalisation, and it doesn't work for fields, parameters or return types.**
>
> **OCaml's inference is global and bidirectional** — it can infer a function's parameter types from how they're *used in the body*, which local deduction cannot do. **`var`, `auto` and `:=` are conveniences; HM is an algorithm.**

**Bidirectional type checking** is the modern middle ground — alternate between *checking* an expression against a known type and *inferring* one. **Handles higher-rank types with modest annotations**, and it's what Haskell, Scala 3, Rust and TypeScript actually implement. **It's the practical answer to undecidable full inference.**

## Where it goes wrong

**The known rough edges, and each is instructive:**

**The value restriction.** Naive generalisation is unsound with mutable references:

```ocaml
let r = ref []          (* ∀a. a list ref — UNSOUND *)
r := [1];               (* now int list ref *)
List.hd !r ^ "boom"     (* treats an int as a string *)
```

**The fix: only generalise *syntactic values***, not arbitrary expressions. `ref []` is an application, so it isn't generalised. **This is why OCaml sometimes reports a weak type variable `'_a`** — a variable that's monomorphic but not yet determined, and it confuses everyone once.

**The monomorphism restriction** — Haskell's related rule, where a binding without arguments isn't generalised unless annotated. **Prevents surprising performance loss** from re-evaluating a dictionary-passing polymorphic value, and it's a common source of "why do I need this type signature?"

**Error messages.** **The single worst practical problem with HM.**

> **Unification reports the failure where it's *detected*, not where the mistake was made.** A type error in line 3 surfaces as a bizarre message about line 47, because that's where the constraint finally became contradictory.
>
> **This is a genuine, well-known usability failure of the algorithm**, and it's why Elm made error messages an explicit design priority and why Rust invests so heavily in diagnostics. Research on type-error slicing and localisation is ongoing and hasn't fully solved it.

**Typeclass ambiguity** — `show (read "1")` has no way to determine the intermediate type. **Requires annotation.**

## Practical inference

**What real compilers do beyond textbook HM:**

**Constraint-based inference** — collect all constraints first, then solve. **Better error messages** (you can attribute constraints to source locations), and it handles typeclasses and subtyping more cleanly. **GHC and Rust both work this way.**

**Local type inference** — infer within a function, require signatures at boundaries. **Scala, Kotlin, Swift.** A deliberate trade: **module boundaries are documented, and inference handles the tedium inside.**

**Rust's inference** is HM-like plus lifetimes, traits and integer defaulting. **Lifetime inference is a separate dataflow analysis**, not unification — and NLL (non-lexical lifetimes) made it substantially more permissive. → [[languages/03-rust/05-lifetimes|Lifetimes]]

**TypeScript** is structural with bidirectional checking and heavy contextual typing — **inferring a callback's parameter types from the expected type of the whole expression**, which is why `arr.map(x => x * 2)` works with no annotation.

## Practical notes

**Annotate top-level function signatures**, even when inference makes them optional. **They're documentation, they localise errors, and they stop a small change silently generalising a type and breaking a distant call site.** This is standard Haskell practice for good reason.

**Read the *first* type error.** Later ones are usually cascading consequences.

**When an error is baffling, add annotations to bisect it.** Annotate the parts you're confident about and let the checker tell you where the contradiction actually is. **The fastest debugging technique for inference errors.**

**Expect the value restriction** if you use `ref` or mutable state in ML. **A `'_weak1` in the type means "monomorphic, not yet decided"** — apply it once and it fixes.

**Don't fight inference with casts.** A cast silences the checker without fixing the model; the error is usually telling you something real.

---

## Related
- [[foundations/programming-language-theory/04-type-systems-formally|Type Systems Formally]] — what's being inferred
- [[foundations/compilers/05-type-systems-and-checking|Compilers: Type Systems]] — implementation
- [[foundations/dsa/04-data-structures/10-union-find|Union-Find]] — the data structure behind unification
- [[foundations/programming-language-theory/README|PL theory map]]

# Type Systems and Checking

**[Intermediate → Advanced]** — What a type checker actually does, how inference works, and the design axes that separate every language you've used.

## What a type system is

> A type system is a **decidable, syntactic, conservative** method for proving the absence of certain program behaviours. — roughly, Benjamin Pierce

Every word carries weight:

- **Decidable** — checking terminates. (C++ templates and Rust's trait solver both bump into this, hence recursion limits)
- **Syntactic** — it reasons about the program text, not about what it computes
- **Conservative** — it rejects some programs that would actually be fine. This is the tax, and it's unavoidable

That last point is the honest framing of every argument about type systems: **you accept false rejections in exchange for guarantees.** More expressive systems reject fewer valid programs but cost more to learn and check.

## The design axes

**Static vs dynamic** — checked before running, or during.

**Strong vs weak** — how much implicit coercion is permitted. Orthogonal to static/dynamic, and constantly conflated. Python is dynamic and strong (`1 + "a"` errors); C is static and weak (casts, `void*`, implicit conversions).

**Nominal vs structural** — is compatibility by *name* or by *shape*?

```typescript
interface Point { x: number; y: number }
const p = { x: 1, y: 2 };
const q: Point = p;        // OK — TypeScript is STRUCTURAL, the shape matches
```

```java
class Point { int x, y; }
Point p = new Coordinates(1, 2);    // ERROR — Java is NOMINAL, different names
```

Structural is flexible and catches fewer intent errors — a `Meters` and a `Seconds` with one `f64` field are interchangeable. Nominal is why [[languages/02-go/02-language-fundamentals|Go's `type UserID int`]] and Rust's newtypes are cheap safety.

Go's interfaces are the interesting hybrid: **structural for interfaces, nominal for concrete types.**

**Gradual typing** — TypeScript, Python with hints, PHP. Types are optional, and `any` is an escape hatch that disables checking locally. Pragmatic for retrofitting types onto existing code; the guarantees are weaker than they appear, because one `any` propagates.

**Soundness** — does the type system actually guarantee what it claims? TypeScript is **deliberately unsound** (bivariant array parameters, `any`, unchecked casts) because soundness would reject too much real JavaScript. Java's arrays are unsound too — `ArrayStoreException` exists because array covariance was a mistake.

## Type checking

The core is a **judgement**: in context Γ, expression `e` has type `T`.

```
Γ ⊢ e : T
```

Rules compose:

```
Γ ⊢ e₁ : Int      Γ ⊢ e₂ : Int
──────────────────────────────
     Γ ⊢ e₁ + e₂ : Int
```

Concretely, that's a recursive walk:

```rust
fn check_expr(&mut self, e: &Expr) -> Type {
    match e {
        Expr::Literal { value, .. } => match value {
            Value::Int(_) => Type::Int,
            Value::Str(_) => Type::Str,
        },

        Expr::Var { name, span } => self.env.lookup(*name)
            .unwrap_or_else(|| self.error(*span, "undefined variable")),

        Expr::Binary { op, left, right, span } => {
            let lt = self.check_expr(left);
            let rt = self.check_expr(right);
            match op {
                BinOp::Add if lt == Type::Int && rt == Type::Int => Type::Int,
                BinOp::Add if lt == Type::Str && rt == Type::Str => Type::Str,
                BinOp::Lt if lt == rt => Type::Bool,
                _ => self.error(*span, &format!("cannot apply {op:?} to {lt} and {rt}")),
            }
        }

        Expr::Call { callee, args, span } => {
            let ft = self.check_expr(callee);
            let Type::Fn { params, ret } = ft else {
                return self.error(*span, "not callable");
            };
            if params.len() != args.len() {
                self.error(*span, &format!("expected {} args, got {}", params.len(), args.len()));
            }
            for (arg, param) in args.iter().zip(&params) {
                let at = self.check_expr(arg);
                self.unify(at, param.clone(), arg.span());
            }
            *ret
        }
    }
}
```

**Two modes worth naming:**

- **Checking** — "does `e` have type `T`?" (you know the expected type)
- **Inferring** — "what type does `e` have?" (you don't)

**Bidirectional type checking** alternates between them, and it's what most modern languages actually implement. It gives good inference where it's easy and clear errors where it isn't, without full global inference's diagnostics problem.

**Report the error, then keep going.** Return an `Error` type that unifies with anything, so one mistake doesn't cascade into fifty. This is essential for a usable checker.

## Inference

```rust
let x = 5;              // x: i32, without you saying so
let v = vec![1, 2, 3];  // Vec<i32>
```

**Local inference** — deduce from the initialiser. Easy, and what `auto`/`var`/`:=` do in C++, Java, and Go.

**Hindley–Milner** — full inference for a whole program, no annotations needed anywhere. ML, Haskell, and the core of Rust's and Swift's inference.

The algorithm has three parts:

**1. Assign type variables** to everything unknown:

```
fn id(x) = x            →    x : α,  id : α → β
```

**2. Generate constraints** by walking the code:

```
fn add(a, b) = a + b    →    α = Int,  β = Int,  return = Int
```

**3. Unify** — solve the constraints:

```rust
fn unify(&mut self, a: Type, b: Type) -> Result<(), TypeError> {
    match (a, b) {
        (Type::Var(v), t) | (t, Type::Var(v)) => {
            if self.occurs_check(v, &t) {                       // ← essential
                return Err(TypeError::InfiniteType);
            }
            self.substitutions.insert(v, t);
            Ok(())
        }
        (Type::Fn { params: p1, ret: r1 }, Type::Fn { params: p2, ret: r2 }) => {
            for (a, b) in p1.into_iter().zip(p2) { self.unify(a, b)?; }
            self.unify(*r1, *r2)
        }
        (a, b) if a == b => Ok(()),
        (a, b) => Err(TypeError::Mismatch(a, b)),
    }
}
```

**The occurs check** prevents infinite types: unifying `α` with `List<α>` would loop forever. It's the thing people forget when implementing this, and the symptom is a hang rather than an error.

**Union-find** is the right data structure for the substitution map — it's the same structure as [[foundations/dsa/04-data-structures/10-union-find|union-find]], and it makes unification near-linear.

**Let-polymorphism** — generalise at `let` so a function can be used at multiple types:

```haskell
id x = x                -- generalised to ∀α. α → α
(id 5, id "hello")      -- instantiated at Int and at String
```

Without generalisation, the first use would fix `α` to `Int` and the second would fail.

### Why full inference isn't universally used

**Error messages get worse.** Without annotations, the checker infers a conflict somewhere and reports it at whichever constraint happened to fail last — often far from the actual mistake. Haskell's "couldn't match expected type" pointing at line 200 for a bug on line 12 is the classic experience.

**Signatures are documentation.** A function's type is the most useful thing about it.

**Some features break it.** Subtyping, overloading, and higher-rank types all make full inference undecidable or badly behaved.

So most languages **require annotations at function boundaries and infer inside them** — Rust, Swift, Kotlin, TypeScript, modern C++. That's the sweet spot: signatures document, bodies stay terse, and errors are local.

## Subtyping and variance

`S <: T` — "an S can be used where a T is expected".

**Variance** is how subtyping lifts through generics, and it's the part that confuses everyone:

| | Meaning | Example |
|---|---|---|
| **Covariant** | `S <: T` ⟹ `F<S> <: F<T>` | a `List<Dog>` is a `List<Animal>` — safe only if **read-only** |
| **Contravariant** | `S <: T` ⟹ `F<T> <: F<S>` | a `Consumer<Animal>` is a `Consumer<Dog>` — **write-only** |
| **Invariant** | neither | mutable collections |

**Why mutable containers must be invariant:**

```java
Object[] objs = new String[1];    // Java allows this — arrays are COVARIANT
objs[0] = 42;                     // compiles, throws ArrayStoreException at RUNTIME
```

Java's array covariance is a known design error, patched with a runtime check. Generics got it right — `List<String>` is *not* a `List<Object>` — which is why you need `? extends` and `? super` wildcards.

The mnemonic is **PECS** — Producer Extends, Consumer Super. It falls directly out of the table above: you can safely read from a covariant source and write to a contravariant sink.

Function types are **contravariant in parameters, covariant in the return type**. A function accepting `Animal` and returning `Dog` can be used where one accepting `Dog` and returning `Animal` is expected.

## Beyond the basics

**Generics / parametric polymorphism** — implemented by [[languages/05-cpp/08-templates-and-concepts|monomorphisation]] (a copy per type: C++, Rust) or **erasure** (one copy, boxed: Java) or a [[languages/02-go/09-generics|hybrid]] (Go's GC-shape stenciling).

**Algebraic data types** — sums (`enum`) and products (`struct`), with exhaustive matching. → [[languages/03-rust/06-structs-enums-and-pattern-matching|Rust: Enums]]

**Traits / type classes** — constrained polymorphism. `T: Ord` rather than "T is a subclass of Comparable".

**Dependent types** — types that depend on *values*: `Vec<n>` where `n` is a number, so a length mismatch is a compile error. Idris, Agda, Lean; F* and Coq for verification. Extremely powerful, and type checking becomes theorem proving.

**Effect systems** — track what a function *does*, not just what it returns. Checked exceptions are a primitive version; Koka and Unison have real ones. This is an active research area and likely where mainstream languages go next.

**Linear / affine types** — a value must be used exactly (or at most) once. **This is what [[languages/03-rust/03-ownership|Rust's ownership]] is** — affine types with borrowing, which is why it can guarantee no use-after-free.

## Practical advice

For a language you're building:

1. **Start dynamically typed.** Get a working interpreter first; a type checker is a large separate project
2. **Then add local inference with required signatures.** The best cost/benefit by a wide distance
3. **Bidirectional checking** — it gives good errors
4. **An `Error` type that unifies with everything**, so one mistake doesn't cascade
5. **Nominal types** unless you have a reason — they catch intent errors structural typing misses
6. **Invariant mutable containers.** Don't repeat Java's array mistake
7. **Don't reach for HM inference** unless the language is ML-shaped. The error messages will cost you more than the annotations saved

---

## Related
- [[foundations/compilers/04-asts-and-semantic-analysis|ASTs and Semantic Analysis]] — the pass before this
- [[foundations/compilers/06-intermediate-representations|Intermediate Representations]] — what comes after
- [[languages/03-rust/09-traits|Rust: Traits]] · [[languages/05-cpp/08-templates-and-concepts|C++: Concepts]] — constrained polymorphism in practice
- [[foundations/dsa/04-data-structures/10-union-find|Union-Find]] — the structure unification uses
- [[foundations/compilers/README|Compilers course map]]

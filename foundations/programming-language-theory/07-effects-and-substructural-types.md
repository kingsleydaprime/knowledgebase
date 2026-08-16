# Effects and Substructural Types

**[Advanced]** — Tracking what a program *does*, not just what it returns. Where Rust's borrow checker comes from, and where languages are going.

## The problem with types

**A type says what a function returns. It usually says nothing about what it does on the way.**

```java
int compute(int x)      // reads a file? writes a global? throws? blocks?
```

**Effect systems make that visible in the type.**

## Effects

$$e : \tau\ !\ \{\text{IO}, \text{Exn}, \text{State}\}$$

**"Returns $\tau$, and may perform these effects."**

**What you've already met:**

**Haskell's `IO`** — the original mainstream effect discipline. A function of type `Int -> Int` **provably cannot** do IO. **`IO` in the type is a promise about what a function might touch**, enforced by the compiler.

**Java's checked exceptions** — `throws IOException` is an effect annotation. **Widely disliked**, because there's no polymorphism: a generic `map` can't say "I throw whatever the function I'm given throws". **The idea was right; the ergonomics weren't.**

**`async`/`await`** — an effect. **And it produces "function colouring"**: async functions can only be awaited from async functions, so the annotation propagates up the entire call stack. **That's an effect system with poor polymorphism**, and the complaint ("what colour is your function?") is really a complaint about the lack of effect polymorphism.

**`const` in C++, `pure` in D, Rust's `unsafe`** — all effect annotations.

## Algebraic effects

**The modern approach, and the one worth watching.**

**Separate *declaring* an effect from *handling* it** — like exceptions, but resumable:

```
effect Read : () -> String
effect Log  : String -> ()

program () =
    let x = perform Read () in
    perform Log ("got " ^ x);
    x
```

**The handler decides what the effects mean:**

```
with handler
  | Read () k  -> continue k "test input"    -- resume with a value
  | Log s   k  -> print s; continue k ()
run program
```

> **The `k` is the continuation — the rest of the computation.** An exception handler *discards* it; an effect handler can **resume** it. **That single difference makes effects strictly more powerful than exceptions.**
>
> **And it unifies a remarkable amount:** exceptions (don't resume), generators (resume later), async (resume when I/O completes), backtracking (resume multiple times), dependency injection (the handler supplies the implementation).

**Why it matters practically:**

**Testing becomes trivial.** Swap the handler — the program under test is unchanged, and you supply a pure handler that returns canned values. **Dependency injection without a framework.**

**No function colouring.** The effect is in the type, but a function polymorphic over effects works with any of them.

**Where it exists:** **OCaml 5's effect handlers** (used to implement its concurrency — `eio` and domains), Koka, Eff, Unison, and Multicore OCaml's whole design. **WebAssembly's stack switching proposal** is effectively this at the VM level.

> **The realistic prediction: algebraic effects are where async/await was in 2010** — well understood in research, appearing in one or two production languages, and likely mainstream within a decade.

## Substructural types

**The other half of this note, and the one that already shipped.**

**Ordinary type systems allow three structural rules:**

| Rule | Means |
|---|---|
| **Weakening** | you may *ignore* a value |
| **Contraction** | you may *duplicate* a value |
| Exchange | order doesn't matter |

**Substructural systems remove some:**

| System | Usage |
|---|---|
| **Linear** | **exactly once** — no dropping, no copying |
| **Affine** | **at most once** — may drop, no copying |
| Relevant | at least once — no dropping |
| Ordered | exactly once, in order |

## Rust is affine types

**The mainstream success story of this whole domain.**

```rust
let s = String::from("hi");
let t = s;              // MOVED — s is no longer usable
println!("{}", s);      // compile error
```

> **`String` is an affine type: usable at most once.** Assignment moves rather than copies. **`Copy` types opt back into contraction; `Drop` handles the "at most" by running cleanup.**
>
> **Borrowing is the refinement that makes it usable.** Pure linear types are painfully restrictive — you'd have to thread every value through explicitly. **`&T` and `&mut T` give temporary access without transferring ownership**, and the rule "one mutable *or* many shared" is what makes it work.

**What this buys, statically:**

**No use-after-free.** The value can't be used after being moved or dropped.

**No double free.** It's dropped exactly once.

**No data races.** `&mut` is exclusive, so no aliased mutation. **This is the deep result** — Rust gets memory safety *and* data-race freedom from one mechanism, with no garbage collector.

**Lifetimes** are the region-based half: **how long a reference is valid**, checked by dataflow analysis rather than unification. → [[languages/03-rust/05-lifetimes|Lifetimes]]

**The intellectual lineage is direct:** Wadler's linear types (1990), region-based memory management (Tofte & Talpin, 1994), and Cyclone (2002) — a safe C dialect that was Rust's most immediate ancestor.

> **Rust is the strongest available evidence that PL theory reaches practice.** **Affine types plus regions, thirty years of research, shipped in a language systems programmers actually use** — most of whom have never heard of either term.

**Elsewhere:** Haskell has `LinearTypes`; C++'s move semantics and `unique_ptr` are affine-ish **without compiler enforcement** — which is exactly why use-after-move is a real C++ bug and a compile error in Rust.

## Session types

**Types for *protocols*.**

```
Client = !Request . ?Response . end
Server = ?Request . !Response . end      -- the dual
```

**"Send a Request, receive a Response, close."** The server's type is the **dual** — receive where the client sends.

**Protocol violations become type errors:** sending twice, receiving in the wrong order, forgetting to close, or deadlocking on mismatched duals.

**Multiparty session types** extend it to more than two participants with a global protocol projected onto each role.

**Where it's reaching practice:** Rust and Scala libraries, verified protocol implementations, and **research on typing distributed system protocols.** → [[architecture/04-distributed-systems/README|Distributed Systems]]

**Still mostly research**, and the ideas are seeping in — typestate patterns in Rust (encoding a state machine in the type so invalid transitions don't compile) are session types in a different dress.

## Ownership beyond Rust

**The problem is general, and other languages are attacking it:**

**Swift** — ARC plus exclusivity enforcement, and it's adding explicit ownership (`consuming`, `borrowing`).

**Mojo** — Rust-like ownership with Python syntax, aimed at ML.

**Val/Hylo** — mutable value semantics, avoiding references entirely.

**Vale** — generational references, a different point in the safety/performance space.

**Java's Project Valhalla** — value types, so identity-free objects can be flattened.

> **The pattern across all of them: memory safety without garbage collection**, and every approach is some form of restricting aliasing. **The GC-vs-manual dichotomy that defined systems programming for decades is being dissolved by type systems**, which is the most consequential thing happening in language design right now.

## Where the field is going

**An honest forecast, since this is the last note:**

**Effect systems** — algebraic effects in more languages, and a solution to function colouring.

**Refinement types with SMT** — `{v: Int | v > 0}`, decidable via a solver. **The pragmatic middle ground** between simple types and dependent types, and the most likely to reach mainstream languages next. Liquid Haskell, F*.

**Gradual verification** — add specifications incrementally, verify what you can. **Lowers the cost of formal methods from all-or-nothing.**

**Better inference for advanced types** — the ergonomics barrier is what has kept dependent types out of practice, not the theory.

**ML for PL** — learned type inference, program synthesis, proof search. **LLMs writing Lean proofs is an active and surprisingly productive area.**

**Types for concurrency and distribution** — session types, and typed actor protocols.

> **The consistent lesson from forty years: the theory is usually decades ahead of practice, and the bottleneck is almost always ergonomics rather than expressiveness.**
>
> **Garbage collection was 1959 and mainstream in the 1990s. Generics were 1972 and mainstream in the 2000s. Algebraic data types were 1970s ML and reached the mainstream via Rust, Swift and Kotlin in the 2010s.** **Affine types were 1990 and shipped in Rust in 2015.**
>
> **So the useful question when reading a PL paper isn't "is this practical?" — it's "what would make this practical?"** That's usually inference, error messages, and interoperation with existing code.

---

## Related
- [[languages/03-rust/03-ownership|Rust: Ownership]] — affine types in production
- [[foundations/programming-language-theory/04-type-systems-formally|Type Systems Formally]] — the foundations
- [[foundations/programming-language-theory/06-curry-howard-and-proofs|Curry–Howard]] — types as specifications
- [[foundations/programming-language-theory/README|PL theory map]]

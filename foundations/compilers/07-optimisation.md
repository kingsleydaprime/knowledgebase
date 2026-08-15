# Optimisation

**[Advanced]** — The passes, why inlining is the one that matters most, and the honest limits of what a compiler can do for you.

## The contract

An optimisation must **preserve observable behaviour** while improving some metric — usually speed, sometimes size.

"Observable" is doing a lot of work in that sentence. It's defined by the language standard, and it's exactly why [[languages/04-c/10-undefined-behaviour|undefined behaviour]] matters: UB isn't observable, so the compiler may assume it doesn't happen and optimise accordingly. That's how a null check gets deleted because you dereferenced the pointer two lines earlier.

## The classic passes

**Constant folding** — evaluate at compile time:

```c
int x = 3 * 4 + 2;      →      int x = 14;
```

**Constant propagation** — substitute known values, then fold again:

```c
int a = 5;  int b = a * 2;      →      int b = 10;
```

**Dead code elimination** — remove code whose results are never used, and unreachable blocks:

```c
int x = expensive();     // if x is never read, and expensive() is pure, delete it
if (false) { ... }       // gone
```

**Common subexpression elimination**:

```c
int a = x * y + 1;
int b = x * y + 2;       →      t = x * y; a = t + 1; b = t + 2;
```

**Strength reduction** — cheaper equivalent operations:

```c
x * 8    →  x << 3
x / 4    →  x >> 2       (unsigned only — signed division rounds toward zero)
x * 2    →  x + x
```

**Loop-invariant code motion** — hoist computations that don't change:

```c
for (i = 0; i < n; i++) { y = a * b; arr[i] = y + i; }
→ y = a * b; for (i = 0; i < n; i++) { arr[i] = y + i; }
```

**Loop unrolling** — fewer branches, more instruction-level parallelism, bigger code.

**Tail-call elimination** — a call in tail position becomes a jump, reusing the frame. It's what makes deep recursion viable in functional languages, and it's guaranteed in Scheme, absent in C and Python (deliberately, so stack traces stay intact).

**Escape analysis** — if an object never leaves the function, allocate it on the stack instead of the heap. Java's, Go's, and .NET's runtimes all do this, and it's why "everything is heap-allocated" is not true in practice. → [[languages/02-go/13-performance-and-runtime|Go: escape analysis]]

**Vectorisation** — turn a scalar loop into SIMD instructions, processing 4/8/16 elements at once. Large wins when it fires, and it's fragile: pointer aliasing, unpredictable branches, or non-contiguous access all prevent it.

## Inlining is the one that matters

Replace a call with the callee's body:

```c
int add(int a, int b) { return a + b; }
int x = add(1, 2);              →      int x = 1 + 2;   →   int x = 3;
```

The direct saving — call overhead, ~2ns — is the smaller half. **The real value is that it enables everything else.** Once the body is inline:

- The arguments are known constants → constant folding
- The result feeds directly into the next computation → CSE
- Branches on parameters become determinate → dead code elimination
- The whole thing may collapse to nothing

This is why [[languages/03-rust/11-collections-and-iterators|iterator chains]] compile to the same code as a hand-written loop: `map`, `filter` and `sum` each inline, and LLVM then sees one loop body with no indirection. **Zero-cost abstraction is inlining plus the passes it unlocks.**

The cost is code size, which hurts instruction-cache locality. So it's a heuristic: inline small functions, hot call sites, and single-caller functions. `#[inline]` and `__attribute__((always_inline))` are hints — the compiler can and does ignore them.

**Cross-module inlining needs LTO** (link-time optimisation) or the body visible in a header. That's why templates live in headers, why Rust ships MIR in rlibs, and why `lto = "fat"` is worth 10–20% in a release build. → [[languages/03-rust/18-performance-and-zero-cost|Rust: Performance]]

## What blocks optimisation

Knowing what *prevents* optimisation is more actionable than knowing the passes:

**Aliasing.** If two pointers might refer to the same memory, the compiler must assume the worst:

```c
void f(int *a, int *b) {
    *a = 1;
    *b = 2;
    return *a;      // must RELOAD — b might alias a
}
```

`restrict` in C promises they don't. **Rust's `&mut` guarantees it in the type system**, which is why rustc can emit `noalias` far more aggressively than any C compiler dares.

**Function calls to unknown code.** An opaque call might modify any global or any memory reachable through a pointer, so everything must be reloaded across it. `pure`/`const` attributes and inlining both help.

**Volatile.** `volatile` explicitly forbids optimising accesses away — that's its entire purpose for hardware registers. → [[languages/04-c/04-types-and-integers|C: volatile]]

**Exceptions and unwinding.** Every call is potentially a branch out, which constrains reordering. Part of why `-fno-exceptions` codebases are marginally faster.

**Floating-point semantics.** `(a + b) + c ≠ a + (b + c)` in IEEE 754, so the compiler cannot reassociate without `-ffast-math` — which changes results and is genuinely dangerous in numerical code.

## Interprocedural and whole-program

**IPO/LTO** — optimise across function and module boundaries. Enables cross-module inlining, better devirtualisation, and global dead-code elimination.

```bash
gcc -flto -O2 ...
```
```toml
[profile.release]
lto = "fat"            # or "thin" — nearly as good, much faster to build
```

**Devirtualisation** — prove a virtual call has one possible target and make it direct, then inline it. Critical for [[languages/05-cpp/06-inheritance-and-virtual-dispatch|C++]] and Java, where dynamic dispatch is everywhere. `final` helps enormously by telling the compiler no override exists.

**PGO** (profile-guided optimisation) — build instrumented, run a representative workload, rebuild using the profile:

```bash
clang -fprofile-generate ...  &&  ./prog  &&  clang -fprofile-use=... -O2 ...
```

The profile tells the optimiser which branches are taken, which calls are hot, and which code is cold. **Typical gains are 10–20%** — larger than most hand optimisation, and almost nobody does it because of the build-pipeline complexity.

**BOLT** does the same at link/post-link time by reordering the binary's layout for instruction-cache locality, and it's easier to adopt.

## Pass ordering

Passes enable each other, and the ordering is a genuinely hard problem:

```
inline → constant propagation → dead code elimination → simplify CFG
       → loop analysis → LICM → vectorise → ...
```

Inlining exposes constants; propagating them makes branches determinate; eliminating dead branches simplifies the CFG; a simpler CFG makes loop analysis work. Then you run several of them again, because the later ones exposed new opportunities.

There's **no optimal order** — it's NP-hard in general, and real compilers use a hand-tuned pipeline refined over decades. `opt -O2` in LLVM runs roughly 200 passes, several of them multiple times.

```bash
opt -O2 -debug-pass-manager foo.ll        # see the pipeline
opt -O2 -print-after-all foo.ll           # IR after every pass — verbose and illuminating
```

## The limits, honestly

**Compilers do not fix algorithms.** An O(n²) loop stays O(n²). No optimiser will replace bubble sort with quicksort, or add a cache, or change your data structure. **Algorithmic choice is yours** and it dominates everything here. → [[foundations/dsa/05-algorithms/01-algorithms|Algorithms]]

**Memory layout is mostly yours.** The compiler won't convert array-of-structs to struct-of-arrays, or fix pointer-chasing through a linked list. Cache behaviour is usually the real bottleneck, and it's a design decision.

**Allocations are mostly yours.** Escape analysis catches some; it won't restructure a program that allocates in a loop.

**`-O3` is not reliably faster than `-O2`.** It enables more aggressive inlining and vectorisation, which can hurt via code bloat. Measure.

> **The honest hierarchy:** algorithm → data structure and memory layout → allocation behaviour → compiler flags → micro-optimisation. Compiler optimisation is the fourth item, and people reach for it first.

## What this means for you

**Write clear code.** The optimiser handles the mechanical transformations, and clever source-level tricks (manual loop unrolling, `x >> 3` instead of `x / 8`) usually make it *harder* to optimise by obscuring the pattern.

**Give it information.** `const`, `restrict`, `final`, `noexcept`, `#[inline]` on genuinely small cross-crate functions, and `static` on internal functions all help.

**Turn on LTO** in release builds. Free, and 10–20%.

**Consider PGO** if you have a representative workload and care enough.

**Measure the release build.** Benchmarking a debug build is measuring nothing. → [[languages/03-rust/18-performance-and-zero-cost|Performance]]

**Read the output when it matters:**

```bash
gcc -O2 -S -masm=intel foo.c -o -
cargo asm my_crate::my_function          # cargo-show-asm
```

[Compiler Explorer](https://godbolt.org) is the standard tool, and an hour there teaches more about what optimisers do than any amount of reading.

---

## Related
- [[foundations/compilers/06-intermediate-representations|Intermediate Representations]] — what these passes operate on
- [[foundations/compilers/08-code-generation|Code Generation]] — the passes after these
- [[languages/03-rust/18-performance-and-zero-cost|Rust: Performance]] — inlining as the basis of zero-cost abstraction
- [[foundations/dsa/05-algorithms/01-algorithms|Algorithms]] — the thing the compiler cannot fix
- [[foundations/compilers/README|Compilers course map]]

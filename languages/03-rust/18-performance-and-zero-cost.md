# Performance and Zero-Cost Abstractions

**[Advanced]** — What "zero-cost" actually claims, where Rust is genuinely fast, where it isn't, and how to measure instead of guess.

## The claim

> *"What you don't use, you don't pay for. What you do use, you couldn't hand-code any better."* — Bjarne Stroustrup, inherited by Rust

Concretely, these compile to the same machine code as the obvious hand-written loop:

- Iterator chains — `v.iter().map(f).filter(g).sum()`
- Generics — monomorphised and inlined
- `Option<T>` — **niche optimisation** makes `Option<&T>` the same size as `&T`, using the null pointer as `None`
- Ownership and borrowing — entirely compile-time; no runtime representation at all
- `impl Trait` static dispatch
- Newtype wrappers — `struct Meters(f64)` is a `f64`

What is **not** free, despite occasional marketing:

- `dyn Trait` — a vtable indirection, no inlining
- `Rc`/`Arc` — refcount updates; `Arc`'s are atomic and genuinely cost
- `RefCell` — a runtime borrow flag check
- `Box` — a heap allocation
- Bounds checks — usually elided, not always
- `async` — a state machine, and a runtime to poll it

The honest version: the *abstractions* are free, the *escape hatches* are not.

## Where Rust actually wins

**No GC.** No pauses, no background collector, no tail-latency spikes. This is the biggest practical difference from [[languages/02-go/13-performance-and-runtime|Go]] and Java, and it's why Rust shows up in trading systems, databases and proxies.

**Memory layout control.** Structs are values, laid out contiguously. A `Vec<Point>` is one allocation of packed points, not an array of pointers to heap objects. Cache behaviour is often the whole story in hot code, and this is where it's decided.

**Aggressive optimisation from the aliasing rules.** `&mut T` is guaranteed unique, which lets LLVM optimise more than it can with C pointers.

**No runtime overhead at startup.** Static binary, no VM, no JIT warm-up.

## Where it doesn't

- **Compile times.** Slow, and it's the main day-to-day cost.
- **Allocation-heavy code with lots of `clone()`** — beginner Rust often clones its way past the borrow checker and ends up slower than the Go version.
- **`Arc<Mutex<T>>` under contention** — no better than any other language's locks.
- **Startup-dominated workloads** where the language never mattered.

## Build profiles first

Before any code change:

```toml
[profile.release]
opt-level = 3
lto = "fat"          # link-time optimisation across crates — often 10-20%
codegen-units = 1    # one unit = better optimisation, slower build
panic = "abort"      # smaller and slightly faster if you don't catch panics
strip = true
```

**Never benchmark a debug build.** `cargo build` produces code that can be 10–100× slower — debug assertions on, no inlining, overflow checks everywhere. This is the single most common Rust benchmarking mistake and it produces wildly wrong conclusions.

## Measuring

```bash
cargo install cargo-criterion flamegraph cargo-bloat
```

**Criterion** — statistical benchmarking, the standard:

```rust
// benches/bench.rs
fn bench(c: &mut Criterion) {
    c.bench_function("parse", |b| {
        b.iter(|| parse(black_box(INPUT)))     // black_box stops the optimiser
    });
}
criterion_group!(benches, bench);
criterion_main!(benches);
```

```bash
cargo bench
```

Criterion runs many iterations, reports confidence intervals, and **compares against the previous run** — telling you "improved by 12% (p < 0.05)" rather than a number you have to eyeball.

`black_box` is essential. Without it the optimiser sees a pure function whose result is discarded and deletes the whole thing, giving you a benchmark that measures nothing.

**Flamegraphs** — where time actually goes:

```bash
cargo flamegraph --bin myapp
perf record -g ./target/release/myapp && perf report
```

**Binary size and compile time:**

```bash
cargo bloat --release --crates       # which dependency is 4MB?
cargo build --timings                # HTML report of what's slow to compile
```

## The things that actually matter

In rough order of how often they're the answer:

**1. Allocations.** `String`, `Vec`, `Box`, and every `clone()`.

```rust
let mut s = String::with_capacity(n);      // preallocate
let mut v = Vec::with_capacity(n);
fn f(s: &str)                               // borrow instead of taking String
v.extend(iter);                             // one reserve, not n pushes
```

Removing a `clone()` from a hot loop beats almost any micro-optimisation.

**2. Cache locality.** `Vec<T>` over `Vec<Box<T>>`, `Vec<T>` over `LinkedList<T>` always. Struct-of-arrays over array-of-structs when you iterate one field.

**3. The right collection.** `HashMap`'s default SipHash is DoS-resistant, not fast — `rustc-hash`'s `FxHashMap` is substantially quicker for internal maps with trusted keys.

**4. Avoid `dyn` in hot paths.** Prefer generics where it's on the critical path; the indirection blocks inlining.

**5. `#[inline]` sparingly.** LLVM is good at this. `#[inline]` is a hint; `#[inline(always)]` is usually a mistake. It matters mainly for small functions *across crate boundaries*, where LLVM can't see the body without LTO.

**6. Bounds checks — measure before caring.** They're often elided when the optimiser can prove the range. Iterators avoid them entirely, which is another reason to prefer a chain over an indexed loop. `get_unchecked` is `unsafe` and rarely the real bottleneck.

## Rules of thumb

1. **Release build, or the numbers are fiction.**
2. **Profile before optimising.** Rust's performance intuitions are wrong as often as anyone's.
3. **Allocations are usually the answer.**
4. **`clone()` freely while learning; grep for it later.** Correct-and-slow beats fighting the borrow checker for a week.
5. **`unsafe` is not a performance strategy.** Measure first — the win is often zero.
6. **Narrow your feature flags** if compile time is the pain. `tokio = ["full"]` is rarely what you need.
7. **Split into workspace crates** for parallel compilation.

## The honest summary

Rust is in the same performance class as C and C++, with predictable latency because there's no GC. But **badly-written Rust is not automatically fast** — a program that clones in a loop and boxes everything will lose to idiomatic Go.

What you reliably get is *predictability*: no pauses, no surprise allocations, and a memory profile you can reason about. That's usually worth more than raw throughput, and it's the actual reason infrastructure is being rewritten in it.

---

## Related
- [[languages/03-rust/11-collections-and-iterators|Collections and Iterators]] — the flagship zero-cost abstraction
- [[languages/03-rust/10-generics-and-trait-bounds|Generics]] — monomorphisation, and its compile-time cost
- [[languages/03-rust/15-unsafe-and-ffi|Unsafe and FFI]] — the last resort, after measuring
- [[languages/02-go/13-performance-and-runtime|Go: Performance and the Runtime]] — GC tuning, the other approach
- [[languages/03-rust/README|Rust course map]]

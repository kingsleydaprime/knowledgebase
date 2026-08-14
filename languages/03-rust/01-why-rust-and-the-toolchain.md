# Why Rust, and the Toolchain

**[Beginner]** — The problem Rust solves that no mainstream language had solved, what it costs you, and the tooling that comes in the box.

**Source:** `[reference]` — cross-referenced against [roadmap.sh Rust](https://roadmap.sh/rust). No Rust project in this vault yet; see [[project-ideas|Project Ideas]].

## The actual problem

Before Rust you picked one of two deals:

**Manual memory management** (C, C++) — full control, no runtime overhead, and you personally guarantee that no pointer outlives its data. Nobody has ever done this reliably at scale. Microsoft and Google have both reported that **~70% of their serious security vulnerabilities are memory-safety bugs**: use-after-free, double-free, buffer overrun, data race.

**Garbage collection** (Java, Go, Python, JS) — the runtime guarantees it for you, at the cost of a GC pause, a heavier runtime, and less control over layout and allocation.

Rust's claim is that this was a false choice. It gets memory safety **at compile time**, with no garbage collector and no runtime cost, by making ownership a part of the type system. If your program compiles, an entire category of bug is gone — including data races, which even a GC doesn't save you from.

That's the deal. Here's the price:

- **The learning curve is real and front-loaded.** Ownership, borrowing and lifetimes are genuinely new concepts, not syntax to memorise. Expect weeks, not days.
- **You will fight the borrow checker.** Everyone does. It mostly means your design is wrong in a way other languages would have let you ship.
- **Compile times are slow.** Monomorphisation and heavy optimisation cost real minutes on large projects.
- **Some data structures are painful.** A doubly-linked list or a cyclic graph fights the ownership model. → [[languages/03-rust/12-smart-pointers-and-interior-mutability|Smart Pointers]]

## Where it fits

**Good at:** systems programming, CLI tools, WebAssembly, embedded, game engines, network services where tail latency matters, and anything where a GC pause or a memory-safety bug is unacceptable. It's displacing C++ in new infrastructure — parts of the Linux kernel, Android, Windows, Firefox, and most new storage/database engines.

**Bad at:** rapid prototyping, scripting, anything where iteration speed beats correctness, and teams that can't absorb the learning curve. A CRUD API you'd write in a day with [[backend/frameworks/java/README|Spring Boot]] or [[languages/02-go/README|Go]] takes longer in Rust and the safety buys you comparatively little.

The honest comparison with Go, since that's the other systems language here:

| | Go | Rust |
|---|---|---|
| Memory safety | GC | compile-time ownership |
| Learning curve | days | weeks to months |
| Compile speed | very fast | slow |
| Runtime | GC, scheduler | none |
| Concurrency | goroutines, blocking style | async/await + threads |
| Error handling | `if err != nil` | `Result` + `?` |
| Verbosity | verbose by design | dense, expressive |
| Best for | services, infra tooling | systems, latency-critical, embedded |

Pick Go when the team and the deadline matter more than the last 10% of performance. Pick Rust when a crash, a pause, or a memory bug is genuinely unacceptable.

## Install and toolchain

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

rustup update
rustup default stable
rustup toolchain install nightly     # for unstable features
rustup component add clippy rustfmt rust-analyzer
rustup target add wasm32-unknown-unknown   # cross-compilation targets
```

`rustup` manages toolchains; `cargo` does everything else:

```bash
cargo new myproject          # binary crate
cargo new mylib --lib        # library crate
cargo build                  # debug build → target/debug/
cargo build --release        # optimised → target/release/  (10-100x faster; always benchmark this)
cargo run
cargo check                  # type-check WITHOUT codegen — much faster, use constantly
cargo test
cargo fmt                    # rustfmt; non-negotiable, like gofmt
cargo clippy                 # the linter, and it is unusually good
cargo doc --open             # generate and view docs for you AND your dependencies
cargo add serde --features derive
cargo tree                   # dependency graph
```

Two habits worth forming immediately:

**`cargo check` in a watch loop.** It skips code generation, so it's several times faster than `cargo build`, and while you're fighting the type system that's all you need.

**Take `clippy` seriously.** It isn't a style linter — it catches real bugs and teaches idiom. `clippy::pedantic` is worth trying on a small project just for the education.

## Hello world, and three surprises

```rust
fn main() {
    println!("Hello, world!");
}
```

**`println!` has an exclamation mark** because it's a *macro*, not a function — it does compile-time format-string checking, so `println!("{}", )` fails to build rather than at runtime. Anything ending in `!` is a macro. → [[languages/03-rust/17-macros|Macros]]

**Variables are immutable by default:**

```rust
let x = 5;
x = 6;          // ERROR: cannot assign twice to immutable variable
let mut y = 5;
y = 6;          // fine
```

Mutability is opt-in, the reverse of nearly every other language. This turns out to matter enormously once borrowing arrives — the compiler needs to know what can change.

**The last expression is the return value**, with no semicolon:

```rust
fn add(a: i32, b: i32) -> i32 {
    a + b        // no semicolon, no `return`
}
```

A semicolon turns an expression into a statement and discards its value. `a + b;` in that function is a type error — you'd be returning `()` where `i32` was promised. This trips everyone up once, and the compiler's message about it is unusually clear.

## The compiler is the teaching tool

Rust's error messages are the best in mainstream programming, and this isn't a small thing — it's a deliberate investment that substitutes for a lot of documentation:

```
error[E0502]: cannot borrow `v` as mutable because it is also borrowed as immutable
  --> src/main.rs:4:5
   |
3  |     let first = &v[0];
   |                  - immutable borrow occurs here
4  |     v.push(4);
   |     ^^^^^^^^^ mutable borrow occurs here
5  |     println!("{}", first);
   |                    ----- immutable borrow later used here
```

It names the rule, points at all three relevant lines, and often suggests the fix. `rustc --explain E0502` gives a full write-up with examples.

**Read the errors properly.** The instinct from other languages is to skim for a line number; here the message usually contains the actual explanation of what you got wrong about ownership.

---

## Related
- [[languages/03-rust/03-ownership|Ownership]] — the idea everything else rests on
- [[languages/03-rust/16-modules-cargo-and-testing|Modules, Cargo and Testing]] — the toolchain in depth
- [[languages/02-go/01-why-go-and-the-toolchain|Go: Why Go]] — the other answer to the same problems
- [[backend/frameworks/rust/README|Rust Backends]] — Axum and Actix
- [[languages/03-rust/README|Rust course map]]

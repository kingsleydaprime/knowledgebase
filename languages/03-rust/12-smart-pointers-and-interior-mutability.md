# Smart Pointers and Interior Mutability

**[Intermediate → Advanced]** — The escape hatches for when one owner isn't enough, and the runtime checks you pay for when the compiler can't do it statically.

## `Box<T>` — heap allocation

```rust
let b = Box::new(5);        // the value lives on the heap; b owns it
```

The simplest smart pointer: one owner, heap-allocated, freed on drop. Three real uses:

**1. Recursive types**, which otherwise have infinite size:

```rust
enum List { Cons(i32, Box<List>), Nil }     // without Box: "recursive type has infinite size"
```

**2. Trait objects**, which are unsized:

```rust
let shapes: Vec<Box<dyn Shape>> = vec![Box::new(Circle), Box::new(Square)];
```

**3. Moving a large value without copying it** — though this matters less than people assume, since moves are memcpy and the optimiser often elides them.

## `Rc<T>` — multiple owners, single-threaded

```rust
use std::rc::Rc;

let a = Rc::new(vec![1, 2, 3]);
let b = Rc::clone(&a);          // NOT a deep copy — increments the refcount
println!("{}", Rc::strong_count(&a));   // 2
```

Reference counting. The value drops when the last `Rc` does. Use it when a value genuinely has several owners and no single one outlives the others — a graph node, a shared config, a tree where children reference parents.

`Rc::clone(&a)` over `a.clone()` is a strong convention: it signals "cheap refcount bump" rather than "deep copy" at the call site.

**`Rc` gives you shared *immutable* access.** You cannot get a `&mut` out of it while more than one exists, because that would break the borrow rule. Combining it with mutation needs `RefCell`.

**`Rc` is not thread-safe** — its counter isn't atomic. That's deliberate: you don't pay for atomics you don't use, and the compiler stops you sharing it across threads because `Rc` isn't `Send`. → [[languages/03-rust/13-concurrency|Concurrency]]

## Interior mutability

The idea: **mutate through a shared reference**, with the borrow rule enforced at *runtime* instead of compile time.

```rust
use std::cell::RefCell;

let c = RefCell::new(5);
*c.borrow_mut() += 1;        // mutating through &self
let v = *c.borrow();
```

| | Check | Cost of breaking it |
|---|---|---|
| `&`/`&mut` | compile time | won't compile |
| `RefCell<T>` | runtime | **panics** |

```rust
let b1 = c.borrow_mut();
let b2 = c.borrow_mut();     // PANIC: already mutably borrowed: BorrowMutError
```

You haven't escaped the rule, you've moved when it's checked. That's a real trade — a bug that would have been a compile error is now a crash in production. Use `try_borrow_mut()` where a panic is unacceptable.

- **`Cell<T>`** — for `Copy` types. No borrowing at all: `get()` copies out, `set()` writes in. No runtime check, no panic, and cheaper. Prefer it when the type is `Copy`.
- **`RefCell<T>`** — for anything, with the runtime check.
- **`OnceCell<T>` / `OnceLock<T>`** — write exactly once, then read forever. The clean lazy-initialisation primitive; `OnceLock` is the thread-safe one and replaces the old `lazy_static` crate.

## `Rc<RefCell<T>>` — shared mutable state

The combination, and the standard shape for graphs and observer patterns:

```rust
let shared = Rc::new(RefCell::new(Vec::new()));
let a = Rc::clone(&shared);
let b = Rc::clone(&shared);

a.borrow_mut().push(1);
b.borrow_mut().push(2);
println!("{:?}", shared.borrow());   // [1, 2]
```

`Rc` gives multiple owners; `RefCell` gives mutation. Its thread-safe counterpart is `Arc<Mutex<T>>`, and the parallel is exact.

**Treat this as a smell in a first draft.** It's the right answer for genuinely shared graph-shaped data and the wrong answer for "the borrow checker was annoying me." Try restructuring first: an arena with indices instead of pointers (`Vec<Node>` plus `usize` handles) is often simpler, faster, and sidesteps the whole problem.

## Reference cycles leak

```rust
struct Node { children: RefCell<Vec<Rc<Node>>>, parent: RefCell<Weak<Node>> }
```

Two `Rc`s pointing at each other never reach zero, and the memory is never freed. **Rust prevents use-after-free, not leaks** — a leak is memory-safe, so it's outside the guarantee. `std::mem::forget` is even a safe function.

The fix is `Weak<T>`: a non-owning reference that doesn't affect the count.

```rust
let weak: Weak<Node> = Rc::downgrade(&strong);
if let Some(rc) = weak.upgrade() { }   // Option<Rc<T>> — None if it's been dropped
```

The convention that avoids cycles: **children hold `Rc` to their data, parents are held as `Weak`.** Ownership flows one direction; back-references are weak.

## `Deref` and deref coercion

```rust
impl Deref for MyBox<T> {
    type Target = T;
    fn deref(&self) -> &T { &self.0 }
}
```

Implementing `Deref` makes a wrapper transparent — `*b` works, and methods on `T` are callable on `MyBox<T>`.

**Deref coercion** is why `&String` works where `&str` is expected, and why `&Vec<T>` works for `&[T]`. The compiler inserts the conversion:

```rust
fn hello(name: &str) { }
let s = String::from("k");
hello(&s);           // &String → &str, automatically
```

Don't implement `Deref` for your own non-pointer types just to get method inheritance. It's a documented anti-pattern — `Deref` means "this *is* a smart pointer", and abusing it makes method resolution confusing.

## `Drop`, again

```rust
impl Drop for Guard {
    fn drop(&mut self) { println!("released"); }
}
```

Runs deterministically at scope exit, in reverse declaration order. This is what makes `MutexGuard` work — the lock releases when the guard drops, so you cannot forget to unlock. It's also why Rust needs no `finally`, no `defer`, and no `try-with-resources`.

`std::mem::drop(x)` drops early by taking ownership. You can't call `x.drop()` directly, since that would leave a double-drop.

## Choosing

| Need | Use |
|---|---|
| One owner, heap | `Box<T>` |
| Several owners, one thread | `Rc<T>` |
| Several owners, many threads | `Arc<T>` |
| Mutate a `Copy` through `&` | `Cell<T>` |
| Mutate anything through `&`, one thread | `RefCell<T>` |
| Mutate through `&`, many threads | `Mutex<T>` / `RwLock<T>` |
| Shared mutable, one thread | `Rc<RefCell<T>>` |
| Shared mutable, many threads | `Arc<Mutex<T>>` |
| Break a cycle | `Weak<T>` |
| Initialise once, read often | `OnceLock<T>` |

The single-threaded and multi-threaded columns are exact mirrors, which makes the set easier to remember than it first looks.

---

## Related
- [[languages/03-rust/13-concurrency|Concurrency]] — `Arc<Mutex<T>>`, the threaded mirror of this
- [[languages/03-rust/04-borrowing-and-references|Borrowing and References]] — the rule being moved to runtime
- [[languages/03-rust/15-unsafe-and-ffi|Unsafe and FFI]] — what these are built on
- [[languages/03-rust/README|Rust course map]]

# Ownership

**[Beginner → Intermediate]** — The idea the entire language is built on. Read this one slowly; everything after it assumes you have it.

## The three rules

> 1. Every value has exactly one **owner**.
> 2. There can only be one owner at a time.
> 3. When the owner goes out of scope, the value is **dropped** (freed).

That's the whole memory-management strategy. No garbage collector, no `free()`, no reference counting by default — the compiler inserts the deallocation because it knows statically where the owner dies.

```rust
{
    let s = String::from("hello");   // s owns the heap allocation
    // ...
}                                     // s goes out of scope → memory freed here
```

This is C++'s RAII, promoted from a convention you follow to a rule the compiler enforces.

## Move semantics

```rust
let s1 = String::from("hello");
let s2 = s1;                  // s1 is MOVED into s2
println!("{}", s1);           // ERROR: borrow of moved value: `s1`
```

Coming from any other language this looks broken. It isn't — it's the second rule doing its job.

A `String` is three words on the stack: **pointer, length, capacity**, pointing at heap data. Assigning copies those three words. If both `s1` and `s2` were valid, both would point at the same heap buffer, and when both went out of scope both would free it — a **double free**.

Rust's options were: copy the heap data (expensive, silent), reference-count it (a runtime cost you didn't ask for), or invalidate the source. It invalidates the source. The move is free; the old binding is statically unusable.

```
 s1 (moved-out, unusable)        s2
┌──────────────┐               ┌──────────────┐
│ ptr    ─────╳│               │ ptr     ─────┼──→ heap: "hello"
│ len    5     │               │ len     5    │
│ cap    5     │               │ cap     5    │
└──────────────┘               └──────────────┘
```

To actually duplicate the data, say so:

```rust
let s2 = s1.clone();     // deep copy; both valid, and the cost is VISIBLE
```

`.clone()` being explicit is a design choice — expensive operations should be greppable.

## `Copy` types

Some types don't move, they copy:

```rust
let x = 5;
let y = x;
println!("{}", x);    // fine — i32 is Copy
```

A type is `Copy` if it's entirely stack data with no heap allocation and no destructor: all integers, floats, `bool`, `char`, `&T` shared references, and tuples/arrays of `Copy` types.

`String`, `Vec<T>`, `Box<T>` and anything owning a resource are **not** `Copy` — that's precisely the point.

The mental shortcut: **if dropping it needs to do work, it moves. If it's just bytes, it copies.**

## Functions move too

```rust
fn takes_ownership(s: String) { }       // s is dropped at the end of this fn

let s = String::from("hi");
takes_ownership(s);
println!("{}", s);      // ERROR — s was moved into the function
```

```rust
fn gives_ownership() -> String { String::from("hi") }   // moves out to the caller

fn takes_and_gives_back(s: String) -> String { s }      // takes, then returns it
```

That last pattern — take ownership, hand it back so the caller can keep using it — is what people write before they learn borrowing, and it's miserable. It's the motivation for the next note.

```rust
let s1 = String::from("hi");
let (s2, len) = calculate_length(s1);      // the ugly version

fn calculate_length(s: String) -> (String, usize) {
    let length = s.len();
    (s, length)
}
```

→ [[languages/03-rust/04-borrowing-and-references|Borrowing and References]] is the fix.

## Partial moves

Moving a field out of a struct moves *that field*, leaving the rest usable:

```rust
struct Person { name: String, age: u32 }

let p = Person { name: "K".into(), age: 30 };
let name = p.name;         // p.name moved out
println!("{}", p.age);     // fine — age is Copy and wasn't moved
println!("{:?}", p);       // ERROR — p as a whole is partially moved
```

Confusing the first time. The compiler tracks moves per-field, not per-variable.

## `Drop`

```rust
impl Drop for Connection {
    fn drop(&mut self) {
        println!("closing connection");
    }
}
```

`drop` runs automatically when the owner goes out of scope, in **reverse declaration order**. This is deterministic — unlike a finaliser in a GC'd language, you know exactly when it runs.

That determinism is what makes RAII work for more than memory: file handles, sockets, mutex guards, and database connections all release at a known point. There's no `try-with-resources` because there's no need for one, and no `defer` because scope exit already does it.

You cannot call `.drop()` manually — use `std::mem::drop(value)`, which just takes ownership and lets it fall out of scope.

## Ownership and collections

```rust
let v = vec![String::from("a"), String::from("b")];

for s in v {          // MOVES v — each String is moved out
    println!("{}", s);
}
println!("{:?}", v);  // ERROR: v was moved

for s in &v { }       // borrows — v still usable afterwards
for s in &mut v { }   // mutable borrow
```

`for x in collection` versus `for x in &collection` is a distinction that doesn't exist in most languages and is the most common early stumble.

Indexing out of a `Vec` can't move either, because that would leave a hole:

```rust
let s = v[0];              // ERROR: cannot move out of index
let s = &v[0];             // borrow
let s = v[0].clone();      // copy
let s = v.remove(0);       // take it out, shifting the rest
let s = std::mem::take(&mut v[0]);   // swap in the default value
```

## Why this is worth the trouble

Ownership eliminates, **at compile time**:

- **Use-after-free** — you can't use a moved value
- **Double free** — one owner, one drop
- **Dangling pointers** — a reference can't outlive its owner ([[languages/03-rust/05-lifetimes|Lifetimes]])
- **Data races** — mutable aliasing is forbidden ([[languages/03-rust/13-concurrency|Concurrency]])

That last one deserves emphasis: **a garbage collector does not prevent data races.** Java and Go are memory-safe but will happily let two threads write the same field. Rust's ownership rules were designed for memory management and turned out to solve concurrency for free — which is the language's most genuinely surprising result.

The cost is that you now think about ownership explicitly. In exchange, you think about it once, at compile time, rather than at 3am.

---

## Related
- [[languages/03-rust/04-borrowing-and-references|Borrowing and References]] — using a value without taking it
- [[languages/03-rust/12-smart-pointers-and-interior-mutability|Smart Pointers]] — for when one owner isn't enough
- [[languages/03-rust/13-concurrency|Concurrency]] — where ownership pays off unexpectedly
- [[languages/02-go/13-performance-and-runtime|Go: the GC]] — the alternative deal
- [[languages/03-rust/README|Rust course map]]

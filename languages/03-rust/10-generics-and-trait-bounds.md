# Generics and Trait Bounds

**[Intermediate]** — Generic code with no runtime cost, and the bounds that make it type-check before it's instantiated.

## The basics

```rust
fn largest<T: PartialOrd>(list: &[T]) -> &T {
    let mut largest = &list[0];
    for item in list {
        if item > largest { largest = item; }
    }
    largest
}

struct Point<T> { x: T, y: T }

impl<T: Display> Point<T> {
    fn show(&self) { println!("({}, {})", self.x, self.y); }
}

impl Point<f64> {                     // impl for ONE concrete type only
    fn distance(&self) -> f64 { (self.x.powi(2) + self.y.powi(2)).sqrt() }
}
```

**Bounds are mandatory and checked at definition.** `item > largest` requires `PartialOrd`; without the bound the *generic function itself* fails to compile, not its instantiation.

This is the key difference from C++ templates. A C++ template is checked when instantiated, which is why a small mistake produces four hundred lines of error from inside `<algorithm>`. Rust checks the generic against its bounds up front, so the error points at your function and says which trait is missing.

## Expressing bounds

```rust
fn f<T: Display + Clone, U: Clone + Debug>(t: T, u: U) { }

fn f<T, U>(t: T, u: U)                 // where clause — use this once it gets long
where
    T: Display + Clone,
    U: Clone + Debug,
{ }

fn notify(item: &impl Summary) { }      // argument-position impl Trait — sugar for a generic
fn make() -> impl Iterator<Item = u32> { (0..10).map(|x| x * 2) }
```

`-> impl Trait` in return position means "some concrete type implementing this, which I'm not naming". It's how you return a closure or an iterator chain without writing an unnameable type:

```rust
fn adder(n: i32) -> impl Fn(i32) -> i32 { move |x| x + n }
```

The restriction: it must be **one** concrete type. Returning `impl Iterator` from two branches with different chains doesn't compile — you need `Box<dyn Iterator>` for that.

## Monomorphisation

The compiler generates a separate copy of a generic function for each concrete type used:

```rust
let a = largest(&vec![1, 2, 3]);           // generates largest::<i32>
let b = largest(&vec!["a", "b"]);          // generates largest::<&str>
```

Consequences, all of them significant:

- **Zero runtime cost.** No boxing, no vtable, no type erasure. Each copy is specialised and inlinable — often *faster* than the hand-written concrete version, because the optimiser sees through everything.
- **Binary size grows.** Widely-instantiated generics are the main cause of large Rust binaries.
- **Compile times suffer.** This is the biggest single contributor to Rust's slow builds.

Compare with [[languages/01-java/01-language/03-generics|Java's erasure]] (one copy, boxing, no runtime type info) and [[languages/02-go/09-generics|Go's GC-shape stenciling]] (a hybrid, which is why Go generics aren't faster than interfaces). Rust picked the fast-at-runtime, slow-at-compile end of the spectrum, deliberately.

The mitigation when binary size matters is the **thin-wrapper pattern** — a small generic function that converts and calls a non-generic one:

```rust
pub fn read<P: AsRef<Path>>(path: P) -> Result<String> {
    read_inner(path.as_ref())          // only THIS is monomorphised; it's tiny
}
fn read_inner(path: &Path) -> Result<String> { /* the real work, one copy */ }
```

The standard library does this throughout.

## Const generics

Generic over *values*, not just types:

```rust
struct Matrix<const N: usize, const M: usize> {
    data: [[f64; M]; N],
}

fn sum<const N: usize>(arr: [i32; N]) -> i32 { arr.iter().sum() }
```

This is why `[T; N]` works generically — arrays of every length share impls. It's the feature that makes fixed-size numeric code (and embedded work) pleasant, and it has no C++-style template metaprogramming attached.

## The closure traits

Closures implement one of three traits, and knowing which is when you stop guessing:

```rust
FnOnce   // consumes captured values — callable ONCE
FnMut    // mutably borrows captures — callable repeatedly, can mutate
Fn       // immutably borrows captures — callable repeatedly, no mutation
```

They nest: every `Fn` is an `FnMut`, every `FnMut` is a `FnOnce`. The compiler infers the most permissive one that works.

```rust
fn apply<F: Fn(i32) -> i32>(f: F, v: i32) -> i32 { f(v) }
fn apply_once<F: FnOnce() -> String>(f: F) -> String { f() }
```

`move` forces the closure to take ownership of what it captures:

```rust
let data = vec![1, 2, 3];
thread::spawn(move || println!("{data:?}"));   // must move — the thread outlives this scope
```

**Take the loosest bound you can.** A parameter typed `FnOnce` accepts more callers than one typed `Fn`. Take `Fn` only if you genuinely call it more than once.

Storing a closure in a struct needs either a generic parameter or boxing:

```rust
struct Handler<F: Fn(&str)> { callback: F }        // static, one type per handler
struct Handler { callback: Box<dyn Fn(&str)> }     // dynamic, heterogeneous
```

## Marker traits and phantom types

Traits with no methods that carry information for the type system:

```rust
Send    // safe to move to another thread
Sync    // safe to share by reference across threads
Sized   // size known at compile time — an implicit bound on every generic
Copy
```

`Sized` being implicit is worth knowing, because opting out is how you accept unsized types:

```rust
fn f<T: ?Sized>(t: &T) { }      // ?Sized = "maybe not sized" — accepts str, [T], dyn Trait
```

`PhantomData` encodes a type parameter you don't actually store:

```rust
struct Meters<T> { value: f64, _unit: PhantomData<T> }
```

This is the typestate pattern — encoding units, or a state machine's state, in the type so mixing them is a compile error, at zero runtime cost.

## Practical advice

1. **Start concrete.** Write it for one type; generalise when the second appears. Same rule as [[languages/02-go/09-generics|Go]].
2. **`impl Trait` in argument position** is more readable than `<T: Trait>` for simple cases.
3. **`where` clauses** the moment bounds exceed one line.
4. **Prefer static dispatch**, use `dyn` for heterogeneous collections.
5. **Watch compile times.** If builds crawl, look for a widely-instantiated generic and apply the thin-wrapper pattern.
6. **Don't reach for `PhantomData` and const generics early.** They're excellent and they're not beginner tools.

---

## Related
- [[languages/03-rust/09-traits|Traits]] — what bounds are made of
- [[languages/03-rust/05-lifetimes|Lifetimes]] — lifetimes are generic parameters too
- [[languages/03-rust/18-performance-and-zero-cost|Performance and Zero-Cost Abstractions]] — what monomorphisation buys
- [[languages/01-java/01-language/03-generics|Java: Generics]] — erasure, for contrast
- [[languages/03-rust/README|Rust course map]]

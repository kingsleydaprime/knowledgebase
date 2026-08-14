# Structs, Enums and Pattern Matching

**[Beginner → Intermediate]** — Rust's enums are not the enums you know, and `match` is why they're the best feature in the language.

## Structs

```rust
struct User { name: String, email: String, active: bool }

struct Point(f64, f64);      // tuple struct
struct Meters(f64);          // newtype — a distinct type wrapping one value
struct Marker;               // unit struct — zero size

let u = User { name: "K".into(), email: "k@x.com".into(), active: true };
let User { name, .. } = u;   // destructuring, ignoring the rest
```

**Field init shorthand** and **struct update syntax**:

```rust
fn new(name: String) -> User {
    User { name, email: String::new(), active: true }   // `name` for `name: name`
}

let u2 = User { email: "new@x.com".into(), ..u1 };   // rest from u1 — MOVES non-Copy fields out of u1
```

The newtype pattern is worth using more than people do:

```rust
struct UserId(u64);
struct OrderId(u64);
```

Distinct types, zero runtime cost, and passing one where the other belongs is a compile error. It's also how you attach your own trait impls to a foreign type, working around the orphan rule. → [[languages/03-rust/09-traits|Traits]]

```rust
impl User {
    fn new(name: String) -> Self { }        // associated function — no self; called User::new()
    fn greet(&self) -> String { }           // borrows
    fn rename(&mut self, n: String) { }     // mutably borrows
    fn consume(self) -> String { self.name } // TAKES ownership — caller can't use it after
}
```

The four receiver forms are `self`, `&self`, `&mut self`, and none. Choosing between them *is* API design in Rust — `consume(self)` is the builder-pattern receiver, `&self` is the default.

## Enums are sum types

This is the part that's genuinely different. A Rust enum isn't a named integer — **each variant can carry different data**:

```rust
enum Message {
    Quit,                           // no data
    Move { x: i32, y: i32 },        // named fields, like a struct
    Write(String),                  // one value
    ChangeColor(i32, i32, i32),     // a tuple
}
```

This is an **algebraic data type**: a value is *exactly one* of these shapes, and the compiler knows it. In Java or Go you'd model this with an interface plus four classes, or a struct with four nullable fields and a tag — both of which let you construct invalid states. Here it's unrepresentable.

The two you'll use constantly are in the standard library:

```rust
enum Option<T> { Some(T), None }
enum Result<T, E> { Ok(T), Err(E) }
```

**There is no `null` in Rust.** Absence is `Option<T>`, and it's a *different type* from `T` — so you cannot forget to check it. That single decision removes Tony Hoare's "billion-dollar mistake" from the language. → [[languages/03-rust/07-option-and-result|Option and Result]]

## `match`

```rust
match msg {
    Message::Quit => println!("quit"),
    Message::Move { x, y } => println!("move to {x},{y}"),
    Message::Write(text) => println!("{text}"),
    Message::ChangeColor(r, g, b) => println!("rgb({r},{g},{b})"),
}
```

**`match` is exhaustive.** Miss a variant and it doesn't compile. This is the feature that makes enums so useful: adding a variant to an enum turns every `match` on it into a compile error listing exactly what needs updating. Refactoring becomes mechanical instead of hopeful.

That's the concrete argument for enums over interfaces — with an interface, adding a case fails silently at runtime in whatever code forgot about it.

`match` is an expression, so it produces a value:

```rust
let status = match code {
    200 => "ok",
    404 => "not found",
    _   => "other",        // _ is the catch-all
};
```

Use `_` sparingly on your own enums. It defeats exhaustiveness — the whole point — by silently absorbing new variants.

### Patterns in full

```rust
match x {
    1 | 2 | 3 => "small",              // or
    4..=10 => "medium",                // inclusive range
    n if n > 100 => "huge",            // guard
    n => "other",                      // binding
}

match point {
    Point { x: 0, y } => ...,          // destructure with a literal
    Point { x, .. } => ...,            // ignore the rest
}

match slice {
    [] => "empty",
    [one] => "single",
    [first, .., last] => "many",       // slice patterns
    [first, rest @ ..] => ...,         // @ binds while matching
}

match opt {
    Some(n @ 1..=5) => ...,            // bind AND constrain
    _ => ...,
}
```

Patterns nest arbitrarily, and destructuring works in `let`, function parameters, and `for` too — not just `match`.

## `if let`, `let else`, `while let`

`match` with one interesting arm is noisy, so there are shorthands:

```rust
if let Some(v) = opt {
    println!("{v}");
} else {
    println!("nothing");
}

// Rust 1.65+ — the early-return form, and a genuinely good addition
let Some(v) = opt else {
    return Err("missing".into());
};
// v is in scope here, unwrapped, for the rest of the function

while let Some(top) = stack.pop() {
    println!("{top}");
}
```

`let else` deserves attention: it removes the rightward drift that `if let` chains cause. The `else` block must diverge — `return`, `break`, `continue`, or `panic!`.

## Modelling with enums — the actual payoff

The idiom to internalise is **make invalid states unrepresentable**:

```rust
// Weak: four fields, and nothing stops all four being set at once
struct Connection {
    connecting: bool,
    connected: bool,
    error: Option<String>,
    socket: Option<TcpStream>,
}

// Strong: exactly one state, with exactly the data that state has
enum Connection {
    Disconnected,
    Connecting { started: Instant },
    Connected { socket: TcpStream, since: Instant },
    Failed { error: String },
}
```

The second version cannot represent "connected and failed", and it can't hold a `socket` while disconnected. Whole classes of bug disappear at the type level, and every `match` on it is checked for completeness.

This is the state-machine pattern from [[backend/frameworks/java/01-spring-boot|the retry state machine]], except the compiler enforces the transitions instead of a comment describing them. If you take one design idea from Rust into other languages, take this one.

---

## Related
- [[languages/03-rust/07-option-and-result|Option and Result]] — the two enums you'll use hourly
- [[languages/03-rust/09-traits|Traits]] — behaviour on these types
- [[languages/03-rust/10-generics-and-trait-bounds|Generics]] — `Option<T>` is generic
- [[concepts/03-design-patterns/README|Design Patterns]] — many of which are language features here
- [[languages/03-rust/README|Rust course map]]

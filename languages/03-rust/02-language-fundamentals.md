# Language Fundamentals

**[Beginner]** — Bindings, the type system, expressions-as-values, and the control flow you'll use before ownership makes sense.

## Bindings

```rust
let x = 5;              // immutable
let mut y = 5;          // mutable
const MAX: u32 = 100;   // compile-time constant, type REQUIRED, screaming case
static NAME: &str = "k"; // has a fixed memory address; lives for the program
```

`const` is inlined everywhere it's used; `static` is a single location in memory. Reach for `const` unless you specifically need an address.

**Shadowing** — re-declaring a name with `let`, which is different from mutation:

```rust
let spaces = "   ";
let spaces = spaces.len();   // now a usize — the TYPE changed
```

This is idiomatic and genuinely useful for the parse-and-rebind pattern:

```rust
let input = "42";
let input: i32 = input.trim().parse().expect("not a number");
```

You don't end up with `input_str` and `input_num` in scope, and the old binding can't be used by accident.

## Types

```rust
i8 i16 i32 i64 i128 isize      // signed; i32 is the default integer
u8 u16 u32 u64 u128 usize      // unsigned
f32 f64                         // f64 is the default float
bool
char                            // 4 bytes, one Unicode scalar value — not a byte
```

`usize` is pointer-sized and is what indexing and `.len()` return. You'll convert to and from it constantly.

**Integer overflow is a panic in debug builds and wraps in release builds.** That difference is deliberate — the panic catches bugs while you develop, the wrap avoids a runtime check in production. When you actually want a behaviour, say so:

```rust
a.checked_add(b)      // Option<T> — None on overflow
a.saturating_add(b)   // clamps at the type's max
a.wrapping_add(b)     // explicit wraparound
a.overflowing_add(b)  // (result, did_it_overflow)
```

**No implicit conversion at all**, same as Go:

```rust
let a: i32 = 5;
let b: i64 = a;           // ERROR
let b: i64 = a as i64;    // explicit cast
let b: i64 = a.into();    // infallible conversion, preferred where it exists
let c: u8 = x.try_into()?; // fallible conversion — returns Result
```

`as` is a blunt instrument that truncates silently (`300u32 as u8` is `44`). Prefer `into`/`try_into`, which encode whether the conversion can fail.

### Compound types

```rust
let tup: (i32, f64, char) = (1, 2.0, 'x');
let (a, b, c) = tup;        // destructuring
let first = tup.0;

let arr: [i32; 5] = [1, 2, 3, 4, 5];   // fixed size, on the STACK; size is part of the type
let zeros = [0; 10];                    // ten zeros
let slice: &[i32] = &arr[1..3];         // a borrowed view
```

`()` is the **unit type** — one value, zero size. It's what functions return when they return nothing, and it's the reason `Result<(), Error>` is the signature for "can fail, produces nothing".

## Functions and expressions

```rust
fn add(a: i32, b: i32) -> i32 {
    a + b       // no semicolon = this is the return value
}
```

Parameter types are always required; return types are required unless the function returns `()`. There's no inference across function boundaries — deliberate, so a signature is a stable contract.

**Almost everything is an expression**, which is the single most pleasant thing about the syntax:

```rust
let x = if cond { 5 } else { 6 };          // if is an expression

let y = match n {
    0 => "zero",
    _ => "other",
};

let z = {                                   // a block is an expression
    let a = 3;
    a * a
};

let w = loop {
    counter += 1;
    if counter == 10 { break counter * 2; }  // loop can return a value
};
```

Both arms of an `if` must have the same type — there's no truthiness and no implicit coercion. This eliminates the ternary operator by making it unnecessary.

`return` exists for early exit, but the trailing-expression form is idiomatic for the final value.

### The never type

```rust
fn forever() -> ! { loop { } }
```

`!` means "never returns". `panic!`, `std::process::exit`, and infinite loops have this type, and it coerces to anything — which is why this compiles:

```rust
let x = match n {
    Some(v) => v,
    None => panic!("nothing"),   // ! coerces to the type of v
};
```

## Control flow

```rust
if x > 5 { } else if x > 2 { } else { }     // no parentheses; braces mandatory

loop { break; }
while cond { }
for i in 0..10 { }          // exclusive range
for i in 0..=10 { }         // inclusive
for item in &collection { }  // borrow
for item in collection { }   // MOVES the collection — you can't use it after
```

There's no C-style `for`. Ranges and iterators cover it, and `for item in collection` moving the collection is your first real encounter with [[languages/03-rust/03-ownership|ownership]].

**Labels** for breaking out of nested loops:

```rust
'outer: for i in 0..10 {
    for j in 0..10 {
        if i * j > 50 { break 'outer; }
    }
}
```

## Strings, which surprise everyone

Two types, and you need both:

```rust
let s: &str = "hello";              // string SLICE — borrowed, fixed, often static
let mut s: String = String::from("hello");  // OWNED, growable, heap-allocated
s.push_str(" world");

let slice: &str = &s;               // String derefs to &str automatically
let owned: String = slice.to_string();
```

**Take `&str` in function parameters, return `String`.** A `&str` accepts both a literal and a borrowed `String`, so it's the more general parameter type. This is the single most common piece of Rust API advice.

```rust
fn greet(name: &str) -> String {    // good
    format!("Hello, {name}!")        // inline format args, Rust 2021+
}
```

Strings are **UTF-8 and cannot be indexed by integer**:

```rust
let s = String::from("héllo");
let c = s[0];              // ERROR — no Index<usize> for String
s.len()                    // 6 — BYTES, not characters
s.chars().nth(1)           // Option<char> — O(n), because UTF-8 is variable-width
s.chars().count()          // 5
&s[0..1]                   // byte slice — PANICS if it splits a char boundary
```

This is the same reality as Go's strings, enforced harder: Go lets you index and get a byte, Rust refuses the operation. Annoying at first, correct in the end — indexing a UTF-8 string by "character" is an O(n) operation and the API shouldn't pretend otherwise.

## Comments and docs

```rust
// line comment

/// Doc comment for the item BELOW. Markdown. Code blocks here are run as tests.
/// ```
/// assert_eq!(mylib::add(2, 2), 4);
/// ```
fn add(a: i32, b: i32) -> i32 { a + b }

//! Doc comment for the ENCLOSING item — used at the top of a module or crate
```

Doc-comment code blocks are **compiled and run by `cargo test`**. Documentation that can't go stale, because CI breaks when it does — the same idea as Go's example tests, taken further.

---

## Related
- [[languages/03-rust/03-ownership|Ownership]] — why `for item in collection` consumes it
- [[languages/03-rust/06-structs-enums-and-pattern-matching|Structs, Enums and Pattern Matching]] — where `match` gets serious
- [[languages/02-go/02-language-fundamentals|Go: Language Fundamentals]] — the same ground, different trade-offs
- [[languages/03-rust/README|Rust course map]]

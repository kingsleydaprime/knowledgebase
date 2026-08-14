# Lifetimes

**[Intermediate]** — The scariest-looking syntax in Rust, which turns out to be describing something you already understand.

## What they actually are

A lifetime is **the scope for which a reference is valid**. Every reference has one; the compiler infers it almost always. Annotations appear only when it can't.

The crucial thing to get straight, because it's the usual misconception:

> **Lifetime annotations do not change how long anything lives.** They *describe* a relationship between the lifetimes of existing values, so the compiler can check it.

You're not allocating or extending anything. You're telling the compiler "the reference coming out is valid as long as the one going in", and it verifies you.

## Why they're needed

```rust
fn longest(x: &str, y: &str) -> &str {      // ERROR: missing lifetime specifier
    if x.len() > y.len() { x } else { y }
}
```

The compiler cannot tell whether the return value borrows from `x` or from `y` — it depends on runtime data. Without knowing, it can't check that the result doesn't outlive whichever it came from.

```rust
fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() { x } else { y }
}
```

Read `'a` as a label: "these two inputs and the output all share a lifetime." Concretely, `'a` resolves to the **shorter** of the two inputs' lifetimes, and the compiler checks the caller against that:

```rust
let s1 = String::from("long string");
let result;
{
    let s2 = String::from("short");
    result = longest(&s1, &s2);      // 'a is the shorter one — s2's scope
}
println!("{}", result);              // ERROR: s2 doesn't live long enough
```

That error is the whole feature working. In C++ this compiles and reads freed memory.

Note that a lifetime only needs to appear where it constrains something:

```rust
fn first<'a>(x: &'a str, _y: &str) -> &'a str { x }   // _y is unrelated; give it its own
```

## Elision — why you rarely write them

Three rules let the compiler infer lifetimes in the common cases. If they fully determine the answer, you write nothing:

1. **Each elided input lifetime gets its own parameter.**
2. **If there is exactly one input lifetime, it's assigned to all output lifetimes.**
3. **If one of the inputs is `&self` or `&mut self`, its lifetime is assigned to all output lifetimes.**

```rust
fn first_word(s: &str) -> &str { }        // rule 2 — unambiguous, no annotation needed

impl Parser {
    fn name(&self) -> &str { &self.name }  // rule 3 — output borrows from self
}
```

Rule 3 is why methods almost never need annotations, and it's why `longest` above *does* — two inputs, no `self`, so rules 1 and 2 leave the output ambiguous.

## Lifetimes in structs

A struct holding a reference must declare that it can't outlive what it borrows:

```rust
struct Parser<'a> {
    input: &'a str,
    pos: usize,
}

impl<'a> Parser<'a> {
    fn new(input: &'a str) -> Self { Parser { input, pos: 0 } }

    fn rest(&self) -> &str { &self.input[self.pos..] }   // rule 3 applies
}
```

`Parser<'a>` means "a Parser that borrows something living at least `'a`". This is the zero-copy parsing pattern — the parser holds slices into the original buffer rather than allocating `String`s, which is a real performance win and a place Rust shines.

**When a struct starts collecting lifetime parameters, consider owning the data instead.** `String` rather than `&'a str` costs an allocation and removes the constraint. Fighting three lifetime parameters to avoid one `clone()` in a config struct is a bad trade — measure before assuming it matters.

## `'static`

```rust
let s: &'static str = "I live for the whole program";
```

`'static` means the reference is valid for the program's entire duration. String literals are `'static` because they're baked into the binary.

Two distinct meanings that get conflated:

- **`&'static T`** — a reference valid forever
- **`T: 'static`** — a *type* that contains no non-`'static` references, i.e. it either owns all its data or only holds `'static` references. `String` is `T: 'static`. `&'a str` is not.

The second is what you see in thread-spawn and async bounds — `thread::spawn` requires `F: 'static` because the closure might outlive the caller. It does **not** mean "lives forever"; it means "doesn't borrow anything short-lived".

When the compiler suggests adding a `'static` bound, that's usually the wrong fix. It's telling you something borrowed is escaping a scope, and the right answer is normally to own it — `to_owned()`, `Arc`, or restructuring — not to promise it lives forever.

## Bounds and subtyping

```rust
struct Wrapper<'a, 'b: 'a> {    // 'b outlives 'a
    long: &'b str,
    short: &'a str,
}
```

`'b: 'a` reads "'b outlives 'a". You'll meet this rarely, mostly in library code.

Lifetimes are **covariant** in most positions, meaning a longer lifetime can be used where a shorter one is expected — which is why passing a `'static` reference to a function wanting `&'a str` just works.

## Higher-ranked bounds

```rust
fn apply<F>(f: F) where F: for<'a> Fn(&'a str) -> &'a str { }
```

`for<'a>` means "for *any* lifetime `'a`", not one specific one — the function must work for all of them. It's usually inferred; you'll only write it explicitly for closures stored in structs. Filed here so it isn't alarming when you see it.

## Practical advice

1. **Don't add lifetimes until the compiler asks.** Elision covers most code.
2. **When you're stuck, try owning the data.** `String` over `&'a str`, `Vec<T>` over `&'a [T]`. Correct first, optimise later.
3. **Read the error message.** "borrowed value does not live long enough" names the exact scope that ends too early.
4. **`'static` in an error is a hint, not usually the fix.** It means something is escaping.
5. **Multiple lifetime parameters are a smell** in application code. Common and correct in libraries; usually over-engineering elsewhere.

Lifetimes are the last big concept and they're less used day to day than ownership and borrowing. Most application Rust has almost no explicit lifetime annotations at all.

---

## Related
- [[languages/03-rust/04-borrowing-and-references|Borrowing and References]] — what lifetimes describe
- [[languages/03-rust/10-generics-and-trait-bounds|Generics and Trait Bounds]] — lifetimes are a kind of generic parameter
- [[languages/03-rust/14-async-and-tokio|Async and Tokio]] — where `'static` bounds bite hardest
- [[languages/03-rust/README|Rust course map]]
